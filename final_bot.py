import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- كود لمنع Render من إغلاق البوت (Web Server) ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'FikraNet Bot is Active!')

def run_web_server():
    # Render يمرر المنفذ عبر متغير PORT تلقائياً
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# --- رسالة الترحيب المختصرة لشبكة فكرة ---
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
    # 1. تشغيل السيرفر في الخلفية لإرضاء Render ومنع الـ Timeout
    threading.Thread(target=run_web_server, daemon=True).start()
    
    # 2. توكن بوتك الخاص (المستخرج من سجلاتك)
    TOKEN = "8229979144:AAHfkYDhzu86Tch677T_5woezpDek43jEw"
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("Bot is starting...")
    app.run_polling()

if __name__ == '__main__':
    main()
