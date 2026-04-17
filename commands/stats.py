import datetime
import os
import httpx
from telegram import Update
from telegram.ext import ContextTypes

from config import check_access, log

AWS_API_URL = os.environ.get("AWS_API_URL", "https://9qgq6qqfvh.execute-api.us-west-2.amazonaws.com/dev")
AWS_API_KEY = os.environ.get("AWS_API_KEY", os.environ.get("API_KEY", ""))
AWS_USER = os.environ.get("AWS_USER", "")

ALIASES = {
    "steps": "steps-iphone",
    "weight": "weight-scale"
}

def parse_metric_id_from_sk(sk: str) -> str:
    """Parse metric ID from SK value like 'METRIC#weight-scale' -> 'weight-scale'."""
    if "#" in sk:
        return sk.split("#", 1)[1]
    return sk

def extract_metric_ids(data) -> list:
    """Extract metric IDs from an API response.

    Handles both a bare list and a dict with an 'items' or 'data' wrapper.
    Prefers the SK field (e.g. 'METRIC#weight-scale') over metricId when present.
    """
    if isinstance(data, dict):
        items = data.get("items", data.get("data", []))
    elif isinstance(data, list):
        items = data
    else:
        return []

    result = []
    for item in items:
        if isinstance(item, dict):
            sk = item.get("SK", "")
            if sk:
                result.append(parse_metric_id_from_sk(sk))
            else:
                result.append(item.get("metricId", ""))
        else:
            result.append(str(item))
    return result

async def get_stats_list(user: str) -> str:
    headers = {"x-api-key": AWS_API_KEY} if AWS_API_KEY else {}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{AWS_API_URL}/users/{user}/metrics", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                if not data:
                    return "No stats found."
                metric_ids = extract_metric_ids(data)
                if not metric_ids:
                    return "No stats found."
                return "Available stats:\n" + "".join(f"  - {m}\n" for m in metric_ids)
            return f"Error {resp.status_code}: {resp.text}"
        except Exception as e:
            log.error(f"Error fetching stats list: {e}")
            return f"Error fetching stats list: {e}"

async def get_stat(user: str, metric_id: str) -> str:
    headers = {"x-api-key": AWS_API_KEY} if AWS_API_KEY else {}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{AWS_API_URL}/users/{user}/metrics/{metric_id}/events", headers=headers, params={"limit": 10})
            if resp.status_code == 200:
                data = resp.json()
                if not data:
                    return f"No events found for {metric_id}."

                raw = data.get("items", data) if isinstance(data, dict) else data
                parsed_data = [item for item in raw if isinstance(item, dict)]
                parsed_data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                
                result = f"Last 30 days for {metric_id}:\n"
                for item in parsed_data[:30]:
                    ts = item.get("timestamp", "")
                    val = item.get("value", "")
                    if ts:
                        ts = ts[:10]
                    result += f"  {ts}: {val}\n"
                return result
            return f"Error {resp.status_code}: {resp.text}"
        except Exception as e:
            log.error(f"Error fetching stat: {e}")
            return f"Error fetching stat: {e}"

async def set_stat(user: str, metric_id: str, value: str, date_str: str = None) -> str:
    try:
        val = float(value) if '.' in value else int(value)
    except ValueError:
        return f"Invalid value: {value}"
    
    now = datetime.datetime.now(datetime.timezone.utc)
    if date_str:
        try:
            parts = date_str.split('/')
            month = int(parts[0])
            day = int(parts[1])
            ts_date = now.replace(month=month, day=day, hour=7, minute=0, second=0, microsecond=0)
            if ts_date > now:
                # If parsed date is in the future, might be last year? Assume current year per prompt constraint
                pass
        except Exception:
            return "Invalid date format. Use MM/DD."
    else:
        ts_date = now.replace(hour=7, minute=0, second=0, microsecond=0)
    
    # We want format: 2026-04-14T07:00:00.000Z
    # use strftime('%Y-%m-%dT%H:%M:%S.000Z')
    timestamp = ts_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    
    payload = {
        "PK": f"USER#{user}",
        "SK": f"EVENT#{metric_id}#{timestamp}",
        "entityType": "MetricEvent",
        "metricId": metric_id,
        "value": val,
        "timestamp": timestamp,
        "GSI1PK": f"USER#{user}#METRIC#{metric_id}",
        "GSI1SK": timestamp
    }
    
    headers = {"x-api-key": AWS_API_KEY} if AWS_API_KEY else {}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{AWS_API_URL}/users/{user}/metrics/{metric_id}/events",
                json=payload,
                headers=headers
            )
            if resp.status_code in [200, 201]:
                return f"Successfully set {metric_id} to {val} on {ts_date.strftime('%Y-%m-%d')}."
            return f"Error {resp.status_code}: {resp.text}"
        except Exception as e:
            log.error(f"Error setting stat: {e}")
            return f"Error setting stat: {e}"

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_access(update):
        return
    
    user = AWS_USER if AWS_USER else update.effective_user.username.lower()
    args = context.args
    
    if not args:
        await update.message.reply_text("Usage:\n/stats list\n/stats <metric>\n/stats set <metric> <value> [MM/DD]")
        return
    
    cmd = args[0].lower()
    
    if cmd == "list":
        res = await get_stats_list(user)
        await update.message.reply_text(res)
    elif cmd == "set":
        if len(args) < 3:
            await update.message.reply_text("Usage: /stats set <metric> <value> [MM/DD]")
            return
        
        metric_id = args[1].lower()
        metric_id = ALIASES.get(metric_id, metric_id)
        value = args[2]
        date_str = args[3] if len(args) > 3 else None
        
        res = await set_stat(user, metric_id, value, date_str)
        await update.message.reply_text(res)
    else:
        metric_id = cmd
        metric_id = ALIASES.get(metric_id, metric_id)
        res = await get_stat(user, metric_id)
        await update.message.reply_text(res)
