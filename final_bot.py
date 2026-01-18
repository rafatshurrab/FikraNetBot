import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- 1. إعدادات السيرفر لمنع التوقف على Render ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'FikraNet Bot is Active!')

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# --- 2. الإعدادات الشخصية ---
TOKEN = '8229979144:AAGJUdqyt9EiZmB3wauIZ4PwOZwaHJJrczk' 
MY_CHAT_ID = 180270007 

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- 3. الدوال الأساسية للبوت ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    keyboard = [
        [InlineKeyboardButton("يوزرات اشتراك شهري 👤", callback_data='menu_internet')],
        [InlineKeyboardButton("طلب بطاقات انترنت 💳", callback_data='menu_cards')],
        [InlineKeyboardButton("بطاقات VIP سرعات عالية 🚀", callback_data='menu_vip')],
        [InlineKeyboardButton("فحص بطاقة انترنت 🔍", callback_data='check_card')],
        [InlineKeyboardButton("التحويل إلى موظف 👨‍💻", callback_data='agent')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "👋 أهلاً بك في نظام خدمات شبكة فكرة!\nالرجاء اختيار الخدمة المطلوبة من القائمة أدناه:"
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'menu_internet':
        keyboard = [
            [InlineKeyboardButton("يوزر 1.5 ميجا (100 ₪)", callback_data='req_يوزر 1.5 ميجا')],
            [InlineKeyboardButton("يوزر 2 ميجا (150 ₪)", callback_data='req_يوزر 2 ميجا')],
            [InlineKeyboardButton("يوزر 3 ميجا (200 ₪)", callback_data='req_يوزر 3 ميجا')],
            [InlineKeyboardButton("⬅️ عودة", callback_data='main_menu')]
        ]
        await query.edit_message_text("👤 **خدمات اليوزرات الشهرية:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif query.data == 'menu_cards':
        keyboard = [
            [InlineKeyboardButton("30 بطاقة (60 ₪)", callback_data='req_30 بطاقة')],
            [InlineKeyboardButton("40 بطاقة (80 ₪)", callback_data='req_40 بطاقة')],
            [InlineKeyboardButton("50 بطاقة (100 ₪)", callback_data='req_50 بطاقة')],
            [InlineKeyboardButton("⬅️ عودة", callback_data='main_menu')]
        ]
        await query.edit_message_text("💳 **طلب كميات البطاقات:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif query.data == 'menu_vip':
        keyboard = [
            [InlineKeyboardButton("5 ميجا (3س) - 5 ₪", callback_data='req_VIP 5 ميجا')],
            [InlineKeyboardButton("10 ميجا (4س) - 10 ₪", callback_data='req_VIP 10 ميجا')],
            [InlineKeyboardButton("20 ميجا (4س) - 15 ₪", callback_data='req_VIP 20 ميجا')],
            [InlineKeyboardButton("⬅️ عودة", callback_data='main_menu')]
        ]
        await query.edit_message_text("🚀 **بطاقات VIP السرعات العالية:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif query.data == 'check_card':
        context.user_data['waiting_for_card_check'] = True
        await query.message.reply_text("🔍 **قسم الدعم الفني:**\nالرجاء إرسال رقم البطاقة (اسم المستخدم) للفحص:")

    elif query.data == 'main_menu':
        await start(update, context)

    elif query.data.startswith('req_'):
        service = query.data.split('_')[1]
        context.user_data['current_order'] = service
        msg = (f"✅ اخترت: {service}\n\n"
               f"⚠️ لإتمام الطلب يرجى الدفع عبر:\n"
               f"🏦 بنك: 1064997\n"
               f"📱 جوال: 0595822440\n\n"
               f"📸 أرسل صورة الوصل هنا ليتم التفعيل من قبل قسم المبيعات.")
        await query.message.reply_text(msg)

    elif query.data.startswith('admin_reply_'):
        data_parts = query.data.split('_')
