from telegram import Update
from telegram.ext import ContextTypes
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from config import check_access, load_persona, GEMINI_API_KEY, DUCK_FORTUNE_IMAGE


async def fortune(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_access(update):
        return
    await update.message.reply_text("Consulting the duck oracle...")
    try:
        persona = load_persona()
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GEMINI_API_KEY)
        response = await llm.ainvoke([
            SystemMessage(content=persona),
            HumanMessage(
                content="Give me a short, whimsical daily fortune in 1-2 sentences. "
                        "Be creative and uplifting."
            ),
        ])
        with open(DUCK_FORTUNE_IMAGE, "rb") as photo:
            await update.message.reply_photo(photo=photo, caption=response.content)
    except Exception as e:
        await update.message.reply_text(f"The oracle is unavailable: {e}")
