import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

# معلومات البوت
TOKEN = '8053977903:AAHHgYtjmm2HJe7_XKQSHTonsxw0vv-YpU4'
bot = telebot.TeleBot(TOKEN)

# معرف الأدمن
ADMIN_ID = 6180691243

# ملف تخزين المنتجات
PRODUCTS_FILE = "products.json"

# تحميل المنتجات
def load_products():
    try:
        with open(PRODUCTS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# حفظ المنتجات
def save_products(products):
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

# أمر لإضافة منتج جديد (خاص بالأدمن)
@bot.message_handler(commands=['addproduct'])
def start_add_product(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "هذا الأمر مخصص فقط لصاحب المتجر.")
        return
    bot.send_message(message.chat.id, "أدخل اسم المنتج:")
    bot.register_next_step_handler(message, get_product_name)

def get_product_name(message):
    name = message.text
    bot.send_message(message.chat.id, "أدخل السعر:")
    bot.register_next_step_handler(message, get_product_price, name)

def get_product_price(message, name):
    price = message.text
    bot.send_message(message.chat.id, "أدخل وصف المنتج:")
    bot.register_next_step_handler(message, get_product_desc, name, price)

def get_product_desc(message, name, price):
    desc = message.text
    bot.send_message(message.chat.id, "أرسل صورة المنتج:")
    bot.register_next_step_handler(message, get_product_image, name, price, desc)

def get_product_image(message, name, price, desc):
    if not message.photo:
        bot.send_message(message.chat.id, "من فضلك أرسل صورة.")
        return
    file_id = message.photo[-1].file_id

    product = {
        "name": name,
        "price": price,
        "desc": desc,
        "image": file_id
    }
    products = load_products()
    products.append(product)
    save_products(products)

    bot.send_message(message.chat.id, "تمت إضافة المنتج بنجاح!")

# عرض المنتجات للزبائن
@bot.message_handler(commands=['start'])
def show_products(message):
    products = load_products()
    if not products:
        bot.send_message(message.chat.id, "لا توجد منتجات حالياً.")
        return
    for i, product in enumerate(products):
        markup = InlineKeyboardMarkup()
        order_btn = InlineKeyboardButton("اطلب الآن", callback_data=f"order_{i}")
        markup.add(order_btn)
        bot.send_photo(
            message.chat.id,
            photo=product["image"],
            caption=f"{product['name']}\nالسعر: {product['price']}\n{product['desc']}",
            reply_markup=markup
        )

# تابع الطلب (سنجمع بيانات الزبون بعد الضغط على زر "اطلب الآن")
@bot.callback_query_handler(func=lambda call: call.data.startswith("order_"))
def handle_order(call):
    product_index = int(call.data.split("_")[1])
    bot.send_message(call.message.chat.id, "من فضلك أرسل اسمك الكامل:")
    bot.register_next_step_handler(call.message, get_name, product_index)

def get_name(message, product_index):
    name = message.text
    bot.send_message(message.chat.id, "أرسل رقم هاتفك:")
    bot.register_next_step_handler(message, get_phone, product_index, name)

def get_phone(message, product_index, name):
    phone = message.text
    bot.send_message(message.chat.id, "أرسل عنوان التوصيل:")
    bot.register_next_step_handler(message, confirm_order, product_index, name, phone)

def confirm_order(message, product_index, name, phone):
    address = message.text
    product = load_products()[product_index]
    order_details = f"""
طلب جديد:

المنتج: {product['name']}
السعر: {product['price']}

اسم الزبون: {name}
رقم الهاتف: {phone}
العنوان: {address}
    """
    # أرسل الطلب إلى الأدمن
    bot.send_message(ADMIN_ID, order_details)
    bot.send_message(message.chat.id, "تم تسجيل طلبك بنجاح! سنتواصل معك قريباً.")

bot.polling()
