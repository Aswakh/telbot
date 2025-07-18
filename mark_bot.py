from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# States for conversation
MID1, MID2, WEEKLY = range(3)

user_data = {}

def start(update, context):
    update.message.reply_text("👋 Welcome to the Mark Estimator Bot!\n\nPlease enter Mid-1 marks (Short+Descriptive) like: 9 22")
    return MID1

def get_mid1(update, context):
    try:
        s, d = map(int, update.message.text.strip().split())
        user_data['mid1'] = s + d / 2
        update.message.reply_text("Now enter Mid-2 marks (Short+Descriptive) like: 8 20")
        return MID2
    except:
        update.message.reply_text("Invalid format! Please enter two numbers separated by space.")
        return MID1

def get_mid2(update, context):
    try:
        s, d = map(int, update.message.text.strip().split())
        user_data['mid2'] = s + d / 2
        update.message.reply_text("Great! Now enter weekly test average (out of 5):")
        return WEEKLY
    except:
        update.message.reply_text("Invalid format! Please enter two numbers separated by space.")
        return MID2

def get_weekly(update, context):
    try:
        weekly = float(update.message.text.strip())
        mid1, mid2 = user_data['mid1'], user_data['mid2']
        
        # Weighted average
        if mid1 >= mid2:
            mid_score = 0.8 * mid1 + 0.2 * mid2
        else:
            mid_score = 0.8 * mid2 + 0.2 * mid1
        
        internal = mid_score + weekly
        required_in_sem = max(28, 50 - internal)

        result = f"📊 Internal Marks: {internal:.2f}/30\n"
        if required_in_sem <= 70:
            result += f"✅ You need at least {required_in_sem:.2f}/70 in Sem Exam to PASS."
        else:
            result += f"❌ You need {required_in_sem:.2f} marks, which is more than 70. Not possible to pass."

        update.message.reply_text(result)
        return ConversationHandler.END
    except:
        update.message.reply_text("Enter a valid number for weekly test marks.")
        return WEEKLY

def cancel(update, context):
    update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END

def main():
    TOKEN = "7746502278:AAG890T6tMvjcwDZKLjpo-6mweZ4mJsZJhk"
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MID1: [MessageHandler(Filters.text & ~Filters.command, get_mid1)],
            MID2: [MessageHandler(Filters.text & ~Filters.command, get_mid2)],
            WEEKLY: [MessageHandler(Filters.text & ~Filters.command, get_weekly)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    print("🤖 Bot is running...")
    updater.idle()

if __name__ == '__main__':
    main()

