import logging

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from telegram import Update
from telegram.ext import ContextTypes

from config import check_access, load_persona, log_token_usage, GEMINI_API_KEY
from tools import ALL_TOOLS

log = logging.getLogger("bot")


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route a free-form question through the LLM with tool-calling support."""
    if not check_access(update):
        return

    question = " ".join(context.args).strip() if context.args else ""
    if not question:
        await update.message.reply_text("Usage: /ask <your question>")
        return

    await update.message.reply_text("Thinking...")

    try:
        persona = load_persona()
        system_prompt = (
            persona
            + "\n\nWhen tools return data to you, always respond to the user in a "
            "friendly, natural, conversational way — never dump raw lists, JSON, or "
            "array syntax. Summarize or present the information clearly in plain English."
        )
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", google_api_key=GEMINI_API_KEY
        ).bind_tools(ALL_TOOLS)

        messages = [SystemMessage(content=system_prompt), HumanMessage(content=question)]

        # Tool-call loop — run until the model returns a plain reply
        while True:
            response = await llm.ainvoke(messages)
            messages.append(response)

            if not response.tool_calls:
                log_token_usage(response, label="/ask")
                break

            for tc in response.tool_calls:
                # Find the matching tool and invoke it (sync; tools are pure data)
                tool_fn = next((t for t in ALL_TOOLS if t.name == tc["name"]), None)
                if tool_fn is None:
                    result = f"Unknown tool: {tc['name']}"
                else:
                    result = tool_fn.invoke(tc["args"])
                messages.append(
                    ToolMessage(content=str(result), tool_call_id=tc["id"])
                )

        await update.message.reply_text(response.content)

    except Exception as e:
        log.exception("Error in /ask handler")
        await update.message.reply_text(f"Something went wrong: {e}")
