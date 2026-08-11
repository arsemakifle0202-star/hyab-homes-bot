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
NAME, PHONE, PROPERTY_TYPE, BEDROOMS, LOCATION, BUDGET = range(6)

# የንብረት አይነቶች ቁልፎች
PROPERTY_KEYBOARD = [
    ['የመኖሪያ'],
    ['የሱቅ'],
    ['የቢሮ']
]

# የመኝታ ክፍሎች ቁልፎች
BEDROOM_KEYBOARD = [
    ['ባለ 1', 'ባለ 2'],
    ['ባለ 3', 'ባለ 4']
]

# የቦታዎች ዝርዝር ቁልፎች
LOCATION_KEYBOARD = [
    ['ካሳንችስ', 'መገናኛ/ሲግናል'],
    ['ፒያሳ', 'ሜክሲኮ'],
    ['ቦሌ/ጋዜቦ']
]

# 1. /start ሲባል የሚጀምር - ስም መቀበያ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    welcome_text = (
        "ሰላም! እንኳን ወደ Hyab Homes በደህና መጡ። 😊\n\n"
        "የሚፈልጉትን ንብረት በጥራት ለማቅረብ እንድንችል እባክዎን በመጀመሪያ **ሙሉ ስምዎን** ያስገቡልን፦"
    )
    await update.message.reply_text(welcome_text, reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')
    return NAME

# 2. ስም ሲገባ - ስልክ ቁጥር መቀበያ
async def name_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        f"እናመሰግናለን {context.user_data['name']}! 🙏\n\n"
        "እባክዎን እርስዎን የምናገኝበትን **የስልክ ቁጥር** ያስገቡልን፦"
    )
    return PHONE

# 3. ስልክ ቁጥር ሲገባ - የንብረት አይነት መቀበያ
async def phone_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['phone'] = update.message.text
    await update.message.reply_text(
        "በጣም ጥሩ! አሁን ደግሞ **ምን አይነት ንብረት** እንደሚፈልጉ ከታች ካሉት አማራጮች ይምረጡ፦",
        reply_markup=ReplyKeyboardMarkup(
            PROPERTY_KEYBOARD, one_time_keyboard=True, resize_keyboard=True
        )
    )
    return PROPERTY_TYPE

# 4. የንብረት አይነት ሲመረጥ
async def property_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    selected_type = update.message.text
    context.user_data['property_type'] = selected_type

    if selected_type == 'የመኖሪያ':
        await update.message.reply_text(
            "እሺ! **ባለ ስንት መኝታ** እንደሚፈልጉ ከታች ካሉት አማራጮች ይምረጡ፦",
            reply_markup=ReplyKeyboardMarkup(
                BEDROOM_KEYBOARD, one_time_keyboard=True, resize_keyboard=True
            ),
            parse_mode='Markdown'
        )
        return BEDROOMS
    else:
        context.user_data['bedrooms'] = 'አልተገለጸም'
        await update.message.reply_text(
            f"እሺ! የመረጡት ንብረት አይነት፦ **{selected_type}**\n\n"
            "ቀጥለው ደግሞ ንብረቱ የሚገኝበትን **ቦታ** ከታች ካሉት አማራጮች ይምረጡ፦",
            reply_markup=ReplyKeyboardMarkup(
                LOCATION_KEYBOARD, one_time_keyboard=True, resize_keyboard=True
            ),
            parse_mode='Markdown'
        )
        return LOCATION

# 4.1. የመኝታ ብዛት ሲመረጥ (የመኖሪያ ለሆነ ብቻ)
async def bedrooms_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['bedrooms'] = update.message.text
    await update.message.reply_text(
        f"በጣም ጥሩ! **{context.user_data['bedrooms']}** ተመርጧል።\n\n"
        "ቀጥለው ደግሞ ንብረቱ የሚገኝበትን **ቦታ** ከታች ካሉት አማራጮች ይምረጡ፦",
        reply_markup=ReplyKeyboardMarkup(
            LOCATION_KEYBOARD, one_time_keyboard=True, resize_keyboard=True
        ),
        parse_mode='Markdown'
    )
    return LOCATION

# 5. ቦታ ሲመረጥ - የበጀት መጠን በጽሁፍ መጠየቂያ (ያለ ምርጫ ቁልፎች)
async def location_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['location'] = update.message.text
    await update.message.reply_text(
        f"በጣም ያማረ ምርጫ! የተመረጠው ቦታ፦ **{context.user_data['location']}**\n\n"
        "እባክዎን ያሰቡትን **የበጀት መጠን** በጽሁፍ ያስገቡልን (ለምሳሌ፦ ከ 10-20 ሚሊዮን)፦",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='Markdown'
    )
    return BUDGET

# 6. በጀት በጽሁፍ ሲገባ - ማጠቃለያ እና ምስጋና
async def budget_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['budget'] = update.message.text
    
    bedrooms_info = f"\n🛏️ **የመኝታ ብዛት:** {context.user_data['bedrooms']}" if context.user_data['property_type'] == 'የመኖሪያ' else ""
    
    summary_text = (
        "✨ **ያቀረቡት መረጃ በትክክል ተመዝግቧል!** ✨\n\n"
        f"👤 **ስም:** {context.user_data['name']}\n"
        f"📞 **ስልክ:** {context.user_data['phone']}\n"
        f"🏢 **የምርጫ አይነት:** {context.user_data['property_type']}"
        f"{bedrooms_info}\n"
        f"📍 **ቦታ:** {context.user_data['location']}\n"
        f"💰 **በጀት:** {context.user_data['budget']}\n\n"
        "ስለ ሰጡን መረጃ እናመሰግናለን! 🙏\n"
        "የድርጅታችን አባል በተመዘገበው ስልክ ቁጥርዎ በቅርቡ አነጋግሮ አመርቂ መረጃ ያቀርብልዎታል።"
    )
    
    await update.message.reply_text(summary_text, reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')
    return ConversationHandler.END

# ሂደቱን ለማቋረጥ (/cancel)
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "ሂደቱ ተቋርጧል። እንደገና ለመጀመር እባክዎን /start ይበሉ።",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main():
    BOT_TOKEN = "8818812895:AAGjxnofPELR83l7ulS80h5pJZPG1FyoZ5Q"

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_choice)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_choice)],
            PROPERTY_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, property_choice)],
            BEDROOMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, bedrooms_choice)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, location_choice)],
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, budget_choice)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
