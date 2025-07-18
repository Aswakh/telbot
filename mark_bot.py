import os
import logging
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)

# ── 1. Logging (optional but handy) ──────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── 2. Conversation states ─────────────────────────────────────────────────────
MID1, MID2, WEEKLY = range(3)

# ── 3. Handlers ────────────────────────────────────────────────────────────────
def start(update, context):
    update.message.reply_text(
        "👋 Hi! Send me your Mid‑1 marks (short 10 + descriptive 30) "
        "as two numbers, e.g. 9 22"
    )
    return MID1

def get_mid1(update, context):
    try:
        s, d = map(float, update.message.text.strip().split())
        context.user_data["mid1"] = s + d / 2  # convert to /25
        update.message.reply_text("Now send Mid‑2 marks, e.g. 8 20")
        return MID2
    except Exception:
        update.message.reply_text("❌ Please send two numbers separated by space.")
        return MID1

def get_mid2(update, context):
    try:
        s, d = map(float, update.message.text.strip().split())
        context.user_data["mid2"] = s + d / 2
        update.message.reply_text("Weekly‑test average (out of 5)?")
        return WEEKLY
    except Exception:
        update.message.reply_text("❌ Please send two numbers separated by space.")
        return MID2

def get_weekly(update, context):
    try:
        weekly = float(update.message.text.strip())
        m1 = context.user_data["mid1"]
        m2 = context.user_data["mid2"]

        # weighted mid score (/25)
        mid_score = 0.8 * max(m1, m2) + 0.2 * min(m1, m2)
        internal = mid_score + weekly                     # /30
        needed_in_sem = max(28, 50 - internal)            # ≥28 rule

        if needed_in_sem <= 70:
            reply = (
                f"📊 Internal: {internal:.2f}/30\n"
                f"✅ Need at least {needed_in_sem:.2f}/70 in the sem exam to pass."
            )
        else:
            reply = (
                f"📊 Internal: {internal:.2f}/30\n"
                f"❌ Even 70/70 won’t reach 50 total – not possible to pass."
            )
        update.message.reply_text(reply)
        return ConversationHandler.END
    except Exception:
        update.message.reply_text("❌ Please send a valid number (0‑5).")
        return WEEKLY

def cancel(update, context):
    update.message.reply_text("Conversation cancelled.")
    return ConversationHandler.END

# ── 4. Main ────────────────────────────────────────────────────────────────────
def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable not set!")

    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MID1:   [MessageHandler(Filters.text & ~Filters.command, get_mid1)],
            MID2:   [MessageHandler(Filters.text & ~Filters.command, get_mid2)],
            WEEKLY: [MessageHandler(Filters.text & ~Filters.command, get_weekly)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dp.add_handler(conv)

    updater.start_polling()   # keeps bot alive (fine on Render free)
    updater.idle()

if __name__ == "__main__":
    main()
