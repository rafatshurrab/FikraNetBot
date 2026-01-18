import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات الشخصية ---
TOKEN = '8229979144:AAHfkYDhz_u86Tch677T_5woezpDek43jEw'
MY_CHAT_ID = 180270007 

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # مسح حالات الطلب القديمة عند البدء من جديد
    context.user_data.clear()
    
    keyboard = [
        [InlineKeyboardButton("يوزرات اشتراك شهري 👤", callback_data='menu_internet')],
        [InlineKeyboardButton("طلب بطاقات انترنت 💳", callback_data='menu_cards')],
        [InlineKeyboardButton("بطاقات VIP سرعات عالية 🚀", callback_data='menu_vip')],
        [InlineKeyboardButton("فحص بطاقة انترنت 🔍", callback_data='check_card')],
        [InlineKeyboardButton("التحويل إلى موظف 👨‍💻", callback_data='agent')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "👋 أهلاً بك في نظام خدمات الشبكة!\nالرجاء اختيار الخدمة المطلوبة من القائمة أدناه:"
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # 1. يوزرات الاشتراك الشهري
    if query.data == 'menu_internet':
        keyboard = [
            [InlineKeyboardButton("يوزر 1.5 ميجا (100 ₪)", callback_data='req_يوزر 1.5 ميجا')],
            [InlineKeyboardButton("يوزر 2 ميجا (150 ₪)", callback_data='req_يوزر 2 ميجا')],
            [InlineKeyboardButton("يوزر 3 ميجا (200 ₪)", callback_data='req_يوزر 3 ميجا')],
            [InlineKeyboardButton("⬅️ عودة", callback_data='main_menu')]
        ]
        await query.edit_message_text("👤 **خدمات اليوزرات الشهرية:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    # 2. طلب بطاقات انترنت (تم التعديل هنا)
    elif query.data == 'menu_cards':
        keyboard = [
            [InlineKeyboardButton("30 بطاقة (60 ₪)", callback_data='req_30 بطاقة')],
            [InlineKeyboardButton("40 بطاقة (80 ₪)", callback_data='req_40 بطاقة')],
            [InlineKeyboardButton("50 بطاقة (100 ₪)", callback_data='req_50 بطاقة')],
            [InlineKeyboardButton("⬅️ عودة", callback_data='main_menu')]
        ]
        await query.edit_message_text("💳 **طلب كميات البطاقات:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    # 3. بطاقات VIP
    elif query.data == 'menu_vip':
        keyboard = [
            [InlineKeyboardButton("5 ميجا (3س) - 5 ₪", callback_data='req_VIP 5 ميجا')],
            [InlineKeyboardButton("10 ميجا (4س) - 10 ₪", callback_data='req_VIP 10 ميجا')],
            [InlineKeyboardButton("20 ميجا (4س) - 15 ₪", callback_data='req_VIP 20 ميجا')],
            [InlineKeyboardButton("⬅️ عودة", callback_data='main_menu')]
        ]
        await query.edit_message_text("🚀 **بطاقات VIP السرعات العالية:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    # 4. فحص بطاقة (دعم فني)
    elif query.data == 'check_card':
        context.user_data['waiting_for_card_check'] = True
        context.user_data['last_type'] = 'tech'
        await query.message.reply_text("🔍 **قسم الدعم الفني:**\nالرجاء إرسال رقم البطاقة (اسم المستخدم) للفحص:")

    elif query.data == 'main_menu':
        await start(update, context)

    # 5. معالجة الطلبات (مبيعات)
    elif query.data.startswith('req_'):
        service = query.data.split('_')[1]
        context.user_data['current_order'] = service
        context.user_data['last_type'] = 'sales'
        msg = (f"✅ اخترت: {service}\n\n"
               f"⚠️ لإتمام الطلب يرجى الدفع عبر:\n"
               f"🏦 بنك: 1064997\n"
               f"📱 جوال: 0595822440\n\n"
               f"📸 أرسل صورة الوصل هنا ليتم التفعيل من قبل قسم المبيعات.")
        await query.message.reply_text(msg)

    # 6. زر الرد الخاص بك (الإدارة)
    elif query.data.startswith('admin_reply_'):
        data_parts = query.data.split('_')
        target_user_id = data_parts[2]
        reply_type = data_parts[3]
        
        context.user_data['reply_to_user'] = target_user_id
        context.user_data['reply_type_label'] = reply_type
        
        dept_name = "💰 قسم المبيعات" if reply_type == 'sales' else "🛠️ الدعم الفني"
        await context.bot.send_message(chat_id=MY_CHAT_ID, text=f"📝 اكتب الآن الرد المطلوب إرساله من {dept_name}:")

    elif query.data == 'agent':
        await query.message.reply_text("👨‍💻 للتواصل المباشر مع مسؤول الشبكة: @rytoo")

async def handle_uploads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # معالجة ردك أنت (المسؤول) للزبون
    if update.effective_chat.id == MY_CHAT_ID and 'reply_to_user' in context.user_data:
        target_id = context.user_data.pop('reply_to_user')
        dept_type = context.user_data.pop('reply_type_label', 'sales')
        
        label = "💰 قسم المبيعات" if dept_type == 'sales' else "🛠️ الدعم الفني"
        admin_text = update.message.text
        
        await context.bot.send_message(chat_id=target_id, text=f"🔔 **رسالة من {label}:**\n\n{admin_text}", parse_mode='Markdown')
        await update.message.reply_text(f"✅ تم إرسال الرد باسم {label}.")
        return

    # معالجة إرسال الزبون لرقم البطاقة (فحص)
    if update.message.text and context.user_data.get('waiting_for_card_check'):
        card_num = update.message.text
        context.user_data['waiting_for_card_check'] = False
        await update.message.reply_text("⏳ تم استلام الرقم، جاري الفحص من قبل الدعم الفني...")
        
        keyboard = [[InlineKeyboardButton("إرسال نتيجة الفحص 🛠️", callback_data=f"admin_reply_{user.id}_tech")]]
        await context.bot.send_message(chat_id=MY_CHAT_ID, text=f"🔍 **طلب فحص فني:**\n👤 المستخدم: @{user.username}\n🔢 الرقم: `{card_num}`", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        return

    # معالجة إرسال الزبون لصورة الوصل (طلب جديد)
    if update.message.photo:
        order = context.user_data.get('current_order', 'طلب عام')
        await update.message.reply_text("📥 استلمنا الوصل، سيقوم قسم المبيعات بالرد عليك فور التأكد.")
        
        keyboard = [[InlineKeyboardButton("إرسال بيانات التفعيل 💰", callback_data=f"admin_reply_{user.id}_sales")]]
        caption = f"🔔 **طلب مبيعات جديد:**\n👤 المستخدم: @{user.username}\n📦 الخدمة: {order}"
        await context.bot.send_photo(chat_id=MY_CHAT_ID, photo=update.message.photo[-1].file_id, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_choice))
    app.add_handler(MessageHandler(filters.PHOTO | filters.TEXT, handle_uploads))
    print("🚀 البوت يعمل الآن بنظام المبيعات والدعم الفني المزدوج واستخدام الرمز ₪.")
    app.run_polling()