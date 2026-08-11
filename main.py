import logging
import warnings
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)
warnings.filterwarnings("ignore")

TOKEN = os.getenv("TOKEN", "8818812895:AAGjxnofPELR83l7ulS80h5pJZPG1FyoZ5Q")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "8966922370")

NAME, PHONE, HOUSE_TYPE, BUDGET = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ሰላም! እንኳን ወደ Hyab Homes በሰላም መጡ። 👋\n\n"
        "የሚፈልጉትን ቤት መረጃ ለመመዝገብ እባክዎን **ስምዎን** ያስገቡ፦"
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        f"እናመሰግናለን {context.user_data['name']}!\n"
        "አሁን ደግሞ **የስልክ ቁጥርዎን** ያስገቡልን፦"
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    
    reply_keyboard = [['የመኖሪያ ቤት', 'የንግድ ቤት (ሱቅ)'], ['አፓርትመንት', 'ሌላ']]
    await update.message.reply_text(
        "በጣም ጥሩ! **ምን ዓይነት ቤት** ነው የሚፈልጉት?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return HOUSE_TYPE

async def get_house_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['house_type'] = update.message.text
    await update.message.reply_text(
        "መድበው የያዙት **በጀት (የገንዘብ መጠን)** ስንት ነው? (ለምሳሌ፦ 20% ቅድመ ክፍያ / 3 ሚሊዮን ብር)",
        reply_markup=ReplyKeyboardRemove()
    )
    return BUDGET

async def get_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['budget'] = update.message.text
    
    name = context.user_data['name']
    phone = context.user_data['phone']
    house_type = context.user_data['house_type']
    budget = context.user_data['budget']
    user_handle = update.effective_user.mention_html()

    summary_text = (
        "✅ **መረጃዎ በተሳካ ሁኔታ ተመዝግቧል!**\n\n"
        f"👤 **ስም፦** {name}\n"
        f"📞 **ስልክ፦** {phone}\n"
        f"🏢 **የቤት ዓይነት፦** {house_type}\n"
        f"💰 **በጀት፦** {budget}\n\n"
        "በቅርብ ጊዜ በስልክ መስመራችን ደውለን እናናግርዎታለን። እናመሰግናለን!"
    )
    await update.message.reply_text(summary_text, parse_mode="Markdown")
    
    admin_text = (
        "🚨 **አዲስ የደንበኛ መረጃ ደርሷል!**\n\n"
        f"👤 **ስም፦** {name}\n"
        f"📞 **ስልክ፦** {phone}\n"
        f"🏢 **የቤት ዓይነት፦** {house_type}\n"
        f"💰 **በጀት፦** {budget}\n"
        f"🔗 **መገለጫ፦** {user_handle}"
    )
    
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text, parse_mode="HTML")
    except Exception as e:
        print(f"Error sending to admin: {e}")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ምዝገባው ተሰርዟል። እንደገና ለመጀመር /start በሉ፤", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            HOUSE_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_house_type)],
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_budget)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    print("Bot is running...")
    app.run_polling()
