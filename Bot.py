import re
import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters
)

BOT_TOKEN = "8959615387:AAEDDaSyhmYnW5D8BEQuyp8p1wongBPJeFU"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# الگوهای رایج لینک گوگل درایو
PATTERNS = [
    # فایل: /file/d/FILE_ID/...
    re.compile(r"drive\.google\.com/file/d/([a-zA-Z0-9_-]{10,})"),
    # قدیمی: open?id=FILE_ID یا uc?id=FILE_ID
    re.compile(r"drive\.google\.com/(?:open|uc)\?(?:.*&)?id=([a-zA-Z0-9_-]{10,})"),
    # پوشه: /drive/(u/0/)?folders/FILE_ID
    re.compile(r"drive\.google\.com/drive/(?:u/\d+/)?folders/([a-zA-Z0-9_-]{10,})"),
]


def extract_file_id(url: str) -> str | None:
    url = url.strip()
    for pattern in PATTERNS:
        if match := pattern.search(url):
            return match.group(1)
    return None


def build_links(file_id: str) -> dict[str, str]:
    return {
        "دانلود مستقیم": f"https://drive.google.com/uc?export=download&id={file_id}",
        "مشاهده/پیش‌نمایش": f"https://drive.google.com/file/d/{file_id}/view",
        "دانلود (فایل حجیم)": (
            f"https://drive.usercontent.google.com/download?id={file_id}"
            "&export=download&confirm=t"
        ),
    }


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "سلام! 👋\n\n"
        "لینک اشتراک‌گذاری گوگل درایو را بفرست تا لینک دانلود مستقیمش را بگیری.\n\n"
        "قالب‌های پشتیبانی‌شده:\n"
        "• drive.google.com/file/d/…/view\n"
        "• drive.google.com/open?id=…\n"
        "• drive.google.com/drive/folders/…",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    file_id = extract_file_id(update.message.text or "")
    if not file_id:
        await update.message.reply_text(
            "❌ لینک گوگل درایو معتبر پیدا نشد.\n"
            "لطفاً لینک اشتراک‌گذاری فایل را دقیق بفرست."
        )
        return

    links = build_links(file_id)
    lines = ["✅ *لینک‌های آماده:*\n"]
    lines += [f"🔗 [{title}]({url})" for title, url in links.items()]
    lines.append("\n⚠️ برای دانلود مستقیم، فایل باید «همه با لینک» قابل دسترس باشد.")
    await update.message.reply_text(
        "\n".join(lines), parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
