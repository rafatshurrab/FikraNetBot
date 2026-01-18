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

# زر العودة الموحد لاستخدامه في كل مكان
back_home_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data='main_menu')]])

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
        await query.message.reply_text("🔍 **قسم الدعم الفني:**\nالرجاء إرسال رقم البطاقة للفحص:", reply_markup=back_home_markup)

    elif query.data == 'main_menu':
        await start(update, context)

    elif query.data.startswith('req_'):
        service = query.data.split('_')[1]
        context.user_data['current_order'] = service
        msg = (f"✅ اخترت: {service}\n\n"
               f"⚠️ لإتمام الطلب يرجى الدفع عبر:\n"
               f"🏦 بنك: 1064997\n"
               f"📱 جوال: 0595822440\n\n"
               f"📸 أرسل صورة الوصل هنا ليتم التفعيل.")
        # إضافة زر العودة هنا لضمان ظهوره فور اختيار الخدمة
        await query.message.reply_text(msg, reply_markup=back_home_markup)

    elif query.data.startswith('admin_reply_'):
        data_parts = query.data.split('_')
        target_user_id = data_parts[2]
        reply_type = data_parts[3]
        context.user_data['reply_to_user'] = target_user_id
        context.user_data['reply_type_label'] = reply_type
        dept_name = "💰 قسم المبيعات" if reply_type == 'sales' else "🛠️ الدعم الفني"
        await context.bot.send_message(chat_id=MY_CHAT_ID, text=f"📝 اكتب رد {dept_name} للمستخدم `{target_user_id}`:", parse_mode='Markdown')

    elif query.data == 'agent':
        await query.message.reply_text("👨‍💻 للتواصل المباشر مع مسؤول الشبكة: @rytoo", reply_markup=back_home_markup)

async def handle_uploads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if update.effective_chat.id == MY_CHAT_ID and 'reply_to_user' in context.user_data:
        target_id = context.user_data.pop('reply_to_user')
        dept_type = context.user_data.pop('reply_type_label', 'sales')
        label = "💰 قسم المبيعات" if dept_type == 'sales' else "🛠️ الدعم الفني"
        admin_text = update.message.text
        await context.bot.send_message(chat_id=target_id, text=f"🔔 **رسالة من {label}:**\n\n{admin_text}", parse_mode='Markdown')
        await context.bot.send_message(chat_id=target_id, text="هل ترغب في خدمة أخرى؟", reply_markup=back_home_markup)
        await update.message.reply_text(f"✅ تم إرسال الرد.")
        return

    if update.message.text and context.user_data.get('waiting_for_card_check'):
        card_num = update.message.text
        context.user_data['waiting_for_card_check'] = False
        await update.message.reply_text("⏳ جاري الفحص من قبل الدعم الفني...", reply_markup=back_home_markup)
        keyboard = [[InlineKeyboardButton("إرسال نتيجة الفحص 🛠️", callback_data=f"admin_reply_{user.id}_tech")]]
        await context.bot.send_message(chat_id=MY_CHAT_ID, text=f"🔍 **طلب فحص فني:**\n👤 المستخدم: @{user.username}\n🔢 الرقم: `{card_num}`", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        return

    if update.message.photo:
        order = context.user_data.get('current_order', 'طلب عام')
        await update.message.reply_text("📥 استلمنا الوصل، سيتم الرد عليك فوراً.", reply_markup=back_home_markup)
        keyboard = [[InlineKeyboardButton("إرسال بيانات التفعيل 💰", callback_data=f"admin_reply_{user.id}_sales")]]
        caption = f"🔔 **طلب مبيعات جديد:**\n👤 المستخدم: @{user.username}\n📦 الخدمة: {order}"
        await context.bot.send_photo(chat_id=MY_CHAT_ID, photo=update.message.photo[-1].file_id, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

def main():
    threading.Thread(target=run_web_server, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_choice))
    app.add_handler(MessageHandler(filters.PHOTO | filters.TEXT, handle_uploads))
    app.run_polling()

if __name__ == '__main__':
    main()
