import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Logging ማዘጋጃ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# የውይይት ደረጃዎች (States)
LOCATION, BUDGET, PHONE, CONFIRM = range(4)

# የቦታዎች ዝርዝር ቁልፎች (Buttons)
LOCATION_KEYBOARD = [
    ['ካሳንችስ', 'መገናኛ/ሲግናል'],
    ['ፒያሳ', 'ሜክሲኮ'],
    ['ቦሌ/ጋዜቦ']
]

# የበጀት ዝርዝር ቁልፎች (Buttons)
BUDGET_KEYBOARD = [
    ['ከ 10-20 ሚሊዮን'],
    ['ከ 20-30 ሚሊዮን']
]

# /start ሲባል የሚጀምር አስተናጋጅ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_name = update.effective_user.first_name
    welcome_text = (
        f"ሰላም {user_name}! እንኳን ወደ Hyab Homes በደህና መጡ።\n\n"
        "የሚፈልጉትን የመኖሪያ ወይም የንግድ ቦታ ለመምረጥ እባክዎን ከታች ካሉት አማራጮች አንዱን ይምረጡ፦"
    )
    await update.message.reply_text(
        welcome_text,
        reply_markup=ReplyKeyboardMarkup(
            LOCATION_KEYBOARD, one_time_keyboard=True, resize_keyboard=True
        )
    )
    return LOCATION

# ቦታ ሲመረጥ
async def location_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['location'] = update.message.text
    await update.message.reply_text(
        f"በጣም ጥሩ! የመረጡት ቦታ፦ {context.user_data['location']}\n\n"
        "አሁን ደግሞ ያሰቡትን የበጀት መጠን ከታች ካሉት አማራጮች ይምረጡ፦",
        reply_markup=ReplyKeyboardMarkup(
            BUDGET_KEYBOARD, one_time_keyboard=True, resize_keyboard=True
        )
    )
    return BUDGET

# በጀት ሲመረጥ
async def budget_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['budget'] = update.message.text
    await update.message.reply_text(
        f"አመሰግናለሁ! የተመረጠው በጀት፦ {context.user_data['budget']}\n\n"
        "እባክዎን የትስስር (ስልክ) ቁጥርዎን ያስገቡልን፦",
        reply_markup=ReplyKeyboardRemove()
    )
    return PHONE

# ስልክ ቁጥር ሲገባ
async def phone_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['phone'] = update.message.text
    
    summary_text = (
        "📋 **የመረጧቸው ዝርዝሮች፦**\n\n"
        f"📍 **ቦታ:** {context.user_data['location']}\n"
        f"💰 **በጀት:** {context.user_data['budget']}\n"
        f"📞 **ስልክ:** {context.user_data['phone']}\n\n"
        "መረጃው ትክክል ከሆነ በቅርቡ አነጋግርዎታለን! አመሰግናለሁ።"
    )
    
    await update.message.reply_text(summary_text, parse_mode='Markdown')
    return ConversationHandler.END

# ሂደቱን ለማቋረጥ (/cancel)
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "ሂደቱ ተቋርጧል። እንደገና ለመጀመር /start ይበሉ።",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main():
    # ቦት ቶከን
    BOT_TOKEN = "7933932470:AAHLxY6P0pE2L3sY9S5nC2yY-Z-N_Q_xX_8"  # እዚህ ጋር የእርስዎን Bot Token ያረጋግጡ

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, location_choice)],
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, budget_choice)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_choice)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
