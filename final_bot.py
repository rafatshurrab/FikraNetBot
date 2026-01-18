import os
import logging
import threading
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- 1. سيرفر Render لمنع التوقف ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'FikraNet Bot is Active!')

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# --- 2. الإعدادات ---
TOKEN = '8229979144:AAGJUdqyt9EiZmB3wauIZ4PwOZwaHJJrczk' 
MY_CHAT_ID = 180270007 

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
back_home_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data='main_menu')]])

# --- 3. الدوال البرمجية ---
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
    text = "👋 أهلاً بك في خدمات شبكة فكرة!\nالرجاء اختيار الخدمة المطلوبة:"
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'main_menu':
        await start(update, context)
    elif query.data == 'menu_internet':
        keyboard = [[InlineKeyboardButton("يوزر 1.5 ميجا (100 ₪)", callback_data='req_1.5M')], [InlineKeyboardButton("يوزر 2 ميجا (150 ₪)", callback_data='req_2M')], [InlineKeyboardButton("⬅️ عودة", callback_data='main_menu')]]
        await query.edit_message_text("👤 **اليوزرات الشهرية:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    elif query.data == 'menu_cards':
        keyboard = [[InlineKeyboardButton("30 بطاقة (60 ₪)", callback_data='req_30C')], [InlineKeyboardButton("40 بطاقة (80 ₪)", callback_data='req_40C')], [InlineKeyboardButton("⬅️ عودة", callback_data='main_menu')]]
        await query.edit_message_text("💳 **طلب كميات البطاقات:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    elif query.data == 'menu_vip':
        keyboard = [[InlineKeyboardButton("VIP 5 ميجا (5 ₪)", callback_data='req_VIP5')], [InlineKeyboardButton("VIP 10 ميجا (10 ₪)", callback_data='req_VIP10')], [InlineKeyboardButton("⬅️ عودة", callback_data='main_menu')]]
        await query.edit_message_text("🚀 **بطاقات VIP السرعات العالية:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    elif query.data == 'check_card':
        context.user_data['waiting_for_card_check'] = True
        await query.message.reply_text("🔍 أرسل رقم البطاقة للفحص الآن:", reply_markup=back_home_markup)
    elif query.data.startswith('req_'):
        service = query.data.split('_')[1]
        context.user_data['current_order'] = service
        await query.message.reply_text(f"✅ اخترت: {service}\n\n📸 **أرسل صورة الوصل هنا ليتم التفعيل.**", reply_markup=back_home_markup)
    elif query.data.startswith('admin_reply_'):
        parts = query.data.split('_')
        context.user_data['reply_to_user'] = parts[2]
        context.user_data['reply_type_label'] = parts[3]
        await context.bot.send_message(chat_id=MY_CHAT_ID, text=f"📝 اكتب الرد للمستخدم `{parts[2]}`:")

async def handle_uploads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if update.effective_chat.id == MY_CHAT_ID and 'reply_to_user' in context.user_data:
        target_id = context.user_data.pop('reply_to_user')
        await context.bot.send_message(chat_id=target_id, text=f"🔔 **رد من الإدارة:**\n\n{update.message.text}", parse_mode='Markdown')
        await context.bot.send_message(chat_id=target_id, text="هل تحتاج خدمة أخرى؟", reply_markup=back_home_markup)
        await update.message.reply_text("✅ تم إرسال الرد.")
        return
    if update.message.text and context.user_data.get('waiting_for_card_check'):
        context.user_data['waiting_for_card_check'] = False
        await update.message.reply_text("⏳ جاري الفحص...", reply_markup=back_home_markup)
        keyboard = [[InlineKeyboardButton("إرسال نتيجة الفحص 🛠️", callback_data=f"admin_reply_{user.id}_tech")]]
        await context.bot.send_message(chat_id=MY_CHAT_ID, text=f"🔍 **طلب فحص:** @{user.username}\n🔢 الرقم: `{update.message.text}`", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        return
    if update.message.photo:
        order = context.user_data.get('current_order', 'طلب عام')
        await update.message.reply_text("📥 استلمنا الوصل، سيتم الرد عليك فوراً.", reply_markup=back_home_markup)
        keyboard = [[InlineKeyboardButton("إرسال بيانات التفعيل 💰", callback_data=f"admin_reply_{user.id}_sales")]]
        await context.bot.send_photo(chat_id=MY_CHAT_ID, photo=update.message.photo[-1].file_id, caption=f"🔔 **وصل جديد:** @{user.username}\n📦 الخدمة: {order}", reply_markup=InlineKeyboardMarkup(keyboard))

# --- 4. التشغيل مع معالجة التعارض ---
def main():
    threading.Thread(target=run_web_server, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_choice))
    app.add_handler(MessageHandler(filters.PHOTO | filters.TEXT, handle_uploads))
    
    print("🚀 البوت يبدأ الآن...")
    app.run_polling(drop_pending_updates=True) # هذا الخيار يحل مشكلة الـ Conflict

if __name__ == '__main__':
    main()
