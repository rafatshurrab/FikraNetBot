import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# كود لمنع Render من إغلاق البوت نهائياً (Keep Alive)
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'FikraNet Bot is Active and Running!')

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# رسالة الترحيب المختصرة لشبكة فكرة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "أهلاً بك في بوت خدمات شبكة فكرة للإنترنت الذكي! 🌐\n\n"
        "• اشتراكات شهرية 👤\n"
        "• بطاقات إنترنت 💳\n"
        "• بطاقات VIP 🚀\n"
        "• فحص البطاقات 🔍\n"
        "• دفع إلكتروني سهل 💸\n\n"
        "اضغط على /start واطلب خدماتك الآن! 👇"
    )
    await update.message.reply_text(msg)

def main():
    # تشغيل السيرفر الوهمي لمنع وضع السكون
    threading.Thread(target=run_web_server, daemon=True).start()
    
    # التوكن الجديد الذي أرسلته: 8229979144:AAGJUdqyt9EiZmB3wauIZ4PwOZwaHJJrczk
    TOKEN = "8229979144:AAGJUdqyt9EiZmB3wauIZ4PwOZwaHJJrczk"
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("Bot is starting with new token...")
    app.run_polling()

if __name__ == '__main__':
    main()
