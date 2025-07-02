import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from woocommerce import API

WC_URL = os.getenv("WOOCOMMERCE_URL")
WC_KEY = os.getenv("WOOCOMMERCE_CONSUMER_KEY")
WC_SECRET = os.getenv("WOOCOMMERCE_CONSUMER_SECRET")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "cks67")

wcapi = API(
    url=WC_URL,
    consumer_key=WC_KEY,
    consumer_secret=WC_SECRET,
    version="wc/v3"
)

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "به فروشگاه کارکیتس خوش آمدید.\nلطفاً نام قطعه را وارد کنید.\nدر صورت عدم پیدا شدن، با پشتیبانی تماس بگیرید."
    )

def search_product(name):
    res = wcapi.get("products", params={"search": name})
    if res.status_code == 200:
        return res.json()
    return []

def handle_message(update: Update, context: CallbackContext):
    query = update.message.text
    results = search_product(query)
    if results:
        for product in results[:3]:
            title = product["name"]
            price = product["price"]
            link = product["permalink"]
            update.message.reply_text(f"🔧 {title}\n💰 قیمت: {price} تومان\n🔗 {link}")
        keyboard = [[InlineKeyboardButton("🧑‍💼 پشتیبان فروش", url=f"https://t.me/{SUPPORT_USERNAME}")]]
        update.message.reply_text("نیاز به کمک بیشتری داری؟", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        keyboard = [[InlineKeyboardButton("🧑‍💼 سفارش قطعه از پشتیبان", url=f"https://t.me/{SUPPORT_USERNAME}")]]
        update.message.reply_text("متأسفم، قطعه‌ای با این مشخصات پیدا نشد.", reply_markup=InlineKeyboardMarkup(keyboard))

app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
