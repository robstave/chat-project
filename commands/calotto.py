import hashlib
import random

from telegram import Update
from telegram.ext import ContextTypes
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from config import check_access, load_persona, GEMINI_API_KEY, DUCK_LOTTO_IMAGE


async def calotto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate CA SuperLotto Plus numbers seeded by an LLM cat haiku."""
    if not check_access(update):
        return
    await update.message.reply_text("Purring for lucky numbers...")
    try:
        persona = load_persona()
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GEMINI_API_KEY)
        haiku_response = await llm.ainvoke([
            SystemMessage(content=persona),
            HumanMessage(
                content="Write a single lucky haiku. Make it cat-themed. "
                        "Output only the three lines of the haiku, nothing else."
            ),
        ])
        haiku = haiku_response.content.strip()

        seed = int(hashlib.sha256(haiku.encode()).hexdigest(), 16)
        rng = random.Random(seed)

        # CA SuperLotto Plus: 5 unique numbers from 1-47, 1 Mega from 1-27
        main_numbers = sorted(rng.sample(range(1, 48), 5))
        mega = rng.randint(1, 27)

        numbers_str = "  ".join(f"{n:02d}" for n in main_numbers)
        caption = (
            f"\U0001F408 Lucky Haiku:\n{haiku}\n\n"
            f"\U0001F3B1 CA SuperLotto Plus Numbers:\n"
            f"{numbers_str}  +  Mega: {mega:02d}"
        )
        with open(DUCK_LOTTO_IMAGE, "rb") as photo:
            await update.message.reply_photo(photo=photo, caption=caption)
    except Exception as e:
        await update.message.reply_text(f"The cat lottery oracle is unavailable: {e}")
