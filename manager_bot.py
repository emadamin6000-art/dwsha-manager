# =========================================================
#                DWSHA BOT MANAGER 🇪🇬🚀
#               بوت إدارة البوتات المتعددة
# =========================================================

import os
import zipfile
import shutil
import subprocess
import signal
import json
import telebot
from telebot import types
from datetime import datetime

# =========================================================
# الإعدادات
# =========================================================

BOT_TOKEN = "8636552077:AAEv_Lc9rM8AasrY2EdxjiABSE5fyD8R1oE"  # ⚠️ غيره بتوكن البوت
OWNER_ID = 8234517259
BOTS_DIR = "/home/bots"  # مجلد البوتات
ALLOWED_USERS = [8234517259]  # الآيديهات المسموح لها

bot = telebot.TeleBot(BOT_TOKEN)

# =========================================================
# إنشاء المجلدات
# =========================================================

if not os.path.exists(BOTS_DIR):
    os.makedirs(BOTS_DIR)

# =========================================================
# ملف حالة البوتات
# =========================================================

BOTS_STATUS_FILE = os.path.join(BOTS_DIR, "bots_status.json")

def load_bots_status():
    if os.path.exists(BOTS_STATUS_FILE):
        with open(BOTS_STATUS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_bots_status(data):
    with open(BOTS_STATUS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# =========================================================
# صلاحيات
# =========================================================

def is_allowed(user_id):
    return user_id in ALLOWED_USERS

def is_owner(user_id):
    return user_id == OWNER_ID

# =========================================================
# لوحة مفاتيح رئيسية
# =========================================================

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📂 قائمة البوتات")
    btn2 = types.KeyboardButton("📤 رفع بوت جديد")
    btn3 = types.KeyboardButton("🔄 إعادة تشغيل الكل")
    btn4 = types.KeyboardButton("🛑 إيقاف الكل")
    btn5 = types.KeyboardButton("📊 حالة السيرفر")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

# =========================================================
# أمر البداية
# =========================================================

@bot.message_handler(commands=['start'])
def start(message):
    if not is_allowed(message.from_user.id):
        bot.reply_to(message, "❌ البوت خاص بالمطور فقط.\n👨‍💻 @DWSHA_TOP")
        return

    text = f"""
╭━━━〔 🚀 DWSHA BOT MANAGER 〕━━━╮

🎮 أهلاً بك في مدير البوتات المتعدد

📤 ارفع أي سورس (ZIP) وهشتغله
🔄 تقدر تتحكم في كل البوتات
📊 متابعة حالة كل بوت

📋 الأوامر:
/start - القائمة الرئيسية
/upload - رفع بوت جديد
/list - عرض البوتات
/run - تشغيل بوت
/stop - إيقاف بوت
/delete - حذف بوت
/status - حالة بوت
/logs - سجلات بوت
/restart_all - إعادة تشغيل الكل
/stop_all - إيقاف الكل

╰━━━━━━━━━━━━━━━━╯
👨‍💻 @DWSHA_TOP
"""
    bot.reply_to(message, text, reply_markup=main_keyboard())

# =========================================================
# عرض البوتات
# =========================================================

@bot.message_handler(commands=['list'])
def list_bots(message):
    if not is_allowed(message.from_user.id):
        return

    bots_status = load_bots_status()
    
    if not bots_status:
        bot.reply_to(message, "❌ لا توجد بوتات مرفوعة.\n📤 استخدم /upload لرفع بوت جديد.")
        return

    text = "📂 **البوتات المرفوعة:**\n\n"
    
    for i, (bot_name, info) in enumerate(bots_status.items(), 1):
        is_running = info.get('running', False)
        upload_date = info.get('date', 'غير معروف')
        status_emoji = "🟢" if is_running else "🔴"
        
        text += f"{i}. {status_emoji} **{bot_name}**\n"
        text += f"   📅 {upload_date}\n"
        text += f"   ⚙️ /run_{bot_name} | /stop_{bot_name} | /delete_{bot_name}\n\n"

    text += f"👨‍💻 @DWSHA_TOP"
    bot.reply_to(message, text, parse_mode="Markdown")

# =========================================================
# أمر الرفع
# =========================================================

@bot.message_handler(commands=['upload'])
def upload_command(message):
    if not is_allowed(message.from_user.id):
        return

    text = f"""
📤 **رفع بوت جديد**

📋 الخطوات:
1. اضغط الملفات في ZIP
2. ابعت الملف هنا
3. البوت هيفك الضغط ويجهزه

⚠️ تأكد إن الملف الرئيسي اسمه main.py أو min.py

👨‍💻 @DWSHA_TOP
"""
    bot.reply_to(message, text, parse_mode="Markdown")

# =========================================================
# استقبال الملفات
# =========================================================

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    if not is_allowed(message.from_user.id):
        bot.reply_to(message, "❌ البوت خاص بالمطور فقط.")
        return

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = message.document.file_name

    if not file_name.endswith('.zip'):
        bot.reply_to(message, "❌ يرجى إرسال ملف ZIP فقط!")
        return

    # حفظ الملف
    zip_path = os.path.join(BOTS_DIR, file_name)
    with open(zip_path, 'wb') as f:
        f.write(downloaded_file)

    waiting_msg = bot.reply_to(message, f"✅ تم استلام: {file_name}\n📦 جاري فك الضغط...")

    # اسم المجلد
    folder_name = file_name.replace('.zip', '')
    extract_path = os.path.join(BOTS_DIR, folder_name)

    # لو المجلد موجود، نحذفه الأول
    if os.path.exists(extract_path):
        shutil.rmtree(extract_path)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        os.remove(zip_path)

        # البحث عن الملف الرئيسي
        files_inside = os.listdir(extract_path)
        bot_file = None
        for f in files_inside:
            if f in ['main.py', 'min.py']:
                bot_file = f
                break

        # تحديث حالة البوتات
        bots_status = load_bots_status()
        bots_status[folder_name] = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'running': False,
            'main_file': bot_file,
            'files': len(files_inside)
        }
        save_bots_status(bots_status)

        # إنشاء أزرار للبوت الجديد
        markup = types.InlineKeyboardMarkup(row_width=3)
        btn_run = types.InlineKeyboardButton("▶️ تشغيل", callback_data=f"run_{folder_name}")
        btn_delete = types.InlineKeyboardButton("🗑️ حذف", callback_data=f"delete_{folder_name}")
        markup.add(btn_run, btn_delete)

        success_msg = f"""
✅ **تم رفع البوت بنجاح!**

📂 **الاسم:** {folder_name}
📁 **عدد الملفات:** {len(files_inside)}
📅 **التاريخ:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

🔍 **الملف الرئيسي:** {bot_file if bot_file else '❌ غير موجود'}

⚠️ لو الملف الرئيسي مش موجود، البوت مش هيشتغل!

👨‍💻 @DWSHA_TOP
"""
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=waiting_msg.message_id,
            text=success_msg,
            parse_mode="Markdown",
            reply_markup=markup
        )

    except Exception as e:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=waiting_msg.message_id,
            text=f"❌ خطأ في فك الضغط:\n{str(e)[:100]}"
        )

# =========================================================
# تشغيل بوت
# =========================================================

def start_bot_process(bot_name):
    bots_status = load_bots_status()
    
    if bot_name not in bots_status:
        return False, "البوت غير موجود!"
    
    bot_info = bots_status[bot_name]
    bot_path = os.path.join(BOTS_DIR, bot_name)
    main_file = bot_info.get('main_file')
    
    if not main_file:
        return False, "لم يتم العثور على الملف الرئيسي!"
    
    try:
        # استخدام screen عشان يشتغل في الخلفية
        screen_name = f"dwsha_{bot_name}"
        
        # لو فيه سكرين قديم، نقتله
        subprocess.run(['screen', '-S', screen_name, '-X', 'quit'], 
                      capture_output=True, text=True)
        
        # تشغيل البوت في screen جديدة
        cmd = f"cd {bot_path} && python3 {main_file}"
        subprocess.Popen(['screen', '-dmS', screen_name, 'bash', '-c', cmd])
        
        # تحديث الحالة
        bots_status[bot_name]['running'] = True
        bots_status[bot_name]['screen'] = screen_name
        save_bots_status(bots_status)
        
        return True, f"تم تشغيل {bot_name} بنجاح!"
        
    except Exception as e:
        return False, f"خطأ: {str(e)[:100]}"

@bot.message_handler(commands=['run'])
def run_bot_command(message):
    if not is_allowed(message.from_user.id):
        return

    args = message.text.split()
    if len(args) < 2:
        # عرض البوتات المتاحة للتشغيل
        bots_status = load_bots_status()
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        for bot_name, info in bots_status.items():
            if not info.get('running', False):
                btn = types.InlineKeyboardButton(
                    f"▶️ {bot_name}", 
                    callback_data=f"run_{bot_name}"
                )
                markup.add(btn)
        
        if len(markup.to_dict().get('inline_keyboard', [])) == 0:
            bot.reply_to(message, "❌ لا توجد بوتات متاحة للتشغيل.")
        else:
            bot.reply_to(message, "اختر بوت لتشغيله:", reply_markup=markup)
        return

    bot_name = args[1]
    success, msg = start_bot_process(bot_name)
    
    if success:
        bot.reply_to(message, f"✅ {msg}")
    else:
        bot.reply_to(message, f"❌ {msg}")

# =========================================================
# إيقاف بوت
# =========================================================

def stop_bot_process(bot_name):
    bots_status = load_bots_status()
    
    if bot_name not in bots_status:
        return False, "البوت غير موجود!"
    
    bot_info = bots_status[bot_name]
    screen_name = f"dwsha_{bot_name}"
    
    try:
        # قتل السكرين
        subprocess.run(['screen', '-S', screen_name, '-X', 'quit'], 
                      capture_output=True, text=True)
        
        # تحديث الحالة
        bots_status[bot_name]['running'] = False
        save_bots_status(bots_status)
        
        return True, f"تم إيقاف {bot_name} بنجاح!"
        
    except Exception as e:
        return False, f"خطأ: {str(e)[:100]}"

@bot.message_handler(commands=['stop'])
def stop_bot_command(message):
    if not is_allowed(message.from_user.id):
        return

    args = message.text.split()
    if len(args) < 2:
        # عرض البوتات الشغالة
        bots_status = load_bots_status()
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        for bot_name, info in bots_status.items():
            if info.get('running', False):
                btn = types.InlineKeyboardButton(
                    f"⏹️ {bot_name}", 
                    callback_data=f"stop_{bot_name}"
                )
                markup.add(btn)
        
        if len(markup.to_dict().get('inline_keyboard', [])) == 0:
            bot.reply_to(message, "❌ لا توجد بوتات شغالة حالياً.")
        else:
            bot.reply_to(message, "اختر بوت لإيقافه:", reply_markup=markup)
        return

    bot_name = args[1]
    success, msg = stop_bot_process(bot_name)
    
    if success:
        bot.reply_to(message, f"✅ {msg}")
    else:
        bot.reply_to(message, f"❌ {msg}")

# =========================================================
# حذف بوت
# =========================================================

@bot.message_handler(commands=['delete'])
def delete_bot_command(message):
    if not is_allowed(message.from_user.id):
        return

    args = message.text.split()
    if len(args) < 2:
        bots_status = load_bots_status()
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        for bot_name in bots_status:
            btn = types.InlineKeyboardButton(
                f"🗑️ {bot_name}", 
                callback_data=f"delete_{bot_name}"
            )
            markup.add(btn)
        
        if len(markup.to_dict().get('inline_keyboard', [])) == 0:
            bot.reply_to(message, "❌ لا توجد بوتات للحذف.")
        else:
            bot.reply_to(message, "⚠️ اختر بوت لحذفه (لا يمكن التراجع):", reply_markup=markup)
        return

    bot_name = args[1]
    bot_path = os.path.join(BOTS_DIR, bot_name)

    if not os.path.exists(bot_path):
        bot.reply_to(message, f"❌ البوت {bot_name} غير موجود!")
        return

    # إيقاف البوت لو شغال
    stop_bot_process(bot_name)

    # حذف المجلد
    try:
        shutil.rmtree(bot_path)
        
        bots_status = load_bots_status()
        if bot_name in bots_status:
            del bots_status[bot_name]
            save_bots_status(bots_status)
        
        bot.reply_to(message, f"🗑️ تم حذف {bot_name} بنجاح!")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ في الحذف:\n{str(e)[:100]}")

# =========================================================
# حالة بوت
# =========================================================

@bot.message_handler(commands=['status'])
def status_bot_command(message):
    if not is_allowed(message.from_user.id):
        return

    args = message.text.split()
    
    if len(args) < 2:
        bots_status = load_bots_status()
        if not bots_status:
            bot.reply_to(message, "❌ لا توجد بوتات.")
            return
        
        text = "📊 **حالة جميع البوتات:**\n\n"
        for bot_name, info in bots_status.items():
            status = "🟢 شغال" if info.get('running') else "🔴 متوقف"
            text += f"**{bot_name}**: {status}\n"
        
        bot.reply_to(message, text, parse_mode="Markdown")
        return

    bot_name = args[1]
    bots_status = load_bots_status()
    
    if bot_name not in bots_status:
        bot.reply_to(message, f"❌ البوت {bot_name} غير موجود!")
        return

    info = bots_status[bot_name]
    status = "🟢 شغال" if info.get('running') else "🔴 متوقف"
    
    text = f"""
📊 **حالة البوت:** {bot_name}

⚙️ **الحالة:** {status}
📅 **تاريخ الرفع:** {info.get('date', 'غير معروف')}
📁 **عدد الملفات:** {info.get('files', 'غير معروف')}
📄 **الملف الرئيسي:** {info.get('main_file', 'غير موجود')}

👨‍💻 @DWSHA_TOP
"""
    bot.reply_to(message, text, parse_mode="Markdown")

# =========================================================
# سجلات البوت
# =========================================================

@bot.message_handler(commands=['logs'])
def logs_bot_command(message):
    if not is_allowed(message.from_user.id):
        return

    bot.reply_to(message, "⚠️ خاصية السجلات غير متاحة حالياً في الاستضافة المجانية.")

# =========================================================
# أوامر جماعية
# =========================================================

@bot.message_handler(commands=['restart_all'])
def restart_all_command(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ الأمر متاح للمطور الأساسي فقط.")
        return

    bots_status = load_bots_status()
    
    if not bots_status:
        bot.reply_to(message, "❌ لا توجد بوتات.")
        return

    waiting_msg = bot.reply_to(message, "🔄 جاري إعادة تشغيل جميع البوتات...")
    
    count = 0
    for bot_name in bots_status:
        stop_bot_process(bot_name)
        success, _ = start_bot_process(bot_name)
        if success:
            count += 1

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=waiting_msg.message_id,
        text=f"✅ تم إعادة تشغيل {count}/{len(bots_status)} بوت."
    )

@bot.message_handler(commands=['stop_all'])
def stop_all_command(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ الأمر متاح للمطور الأساسي فقط.")
        return

    bots_status = load_bots_status()
    
    if not bots_status:
        bot.reply_to(message, "❌ لا توجد بوتات.")
        return

    waiting_msg = bot.reply_to(message, "🛑 جاري إيقاف جميع البوتات...")
    
    count = 0
    for bot_name in bots_status:
        success, _ = stop_bot_process(bot_name)
        if success:
            count += 1

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=waiting_msg.message_id,
        text=f"✅ تم إيقاف {count}/{len(bots_status)} بوت."
    )

# =========================================================
# حالة السيرفر
# =========================================================

@bot.message_handler(commands=['server'])
def server_status(message):
    if not is_allowed(message.from_user.id):
        return

    # مساحة القرص
    disk = os.popen('df -h /').read().splitlines()[1].split()
    
    # الذاكرة
    mem = os.popen('free -h').read().splitlines()[1].split()
    
    # البوتات الشغالة
    bots_status = load_bots_status()
    running_bots = sum(1 for info in bots_status.values() if info.get('running'))
    total_bots = len(bots_status)

    # عدد السكرينات
    screens = os.popen('screen -ls').read()
    screen_count = screens.count('dwsha_')

    text = f"""
📊 **حالة السيرفر**

💾 **المساحة:** {disk[2]}/{disk[1]}
🧠 **الذاكرة:** {mem[2]}/{mem[1]}
🤖 **البوتات:** {running_bots}/{total_bots} شغال
📺 **السكرينات:** {screen_count}

👨‍💻 @DWSHA_TOP
"""
    bot.reply_to(message, text, parse_mode="Markdown")

# =========================================================
# معالج الأزرار
# =========================================================

@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    if not is_allowed(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ غير مصرح لك!")
        return

    data = call.data

    if data.startswith('run_'):
        bot_name = data.replace('run_', '')
        success, msg = start_bot_process(bot_name)
        bot.answer_callback_query(call.id, msg)
        
        if success:
            # تحديث الأزرار
            new_markup = types.InlineKeyboardMarkup(row_width=3)
            btn_stop = types.InlineKeyboardButton("⏹️ إيقاف", callback_data=f"stop_{bot_name}")
            btn_status = types.InlineKeyboardButton("📊 حالة", callback_data=f"status_{bot_name}")
            btn_delete = types.InlineKeyboardButton("🗑️ حذف", callback_data=f"delete_{bot_name}")
            new_markup.add(btn_stop, btn_status, btn_delete)
            
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=new_markup
            )

    elif data.startswith('stop_'):
        bot_name = data.replace('stop_', '')
        success, msg = stop_bot_process(bot_name)
        bot.answer_callback_query(call.id, msg)
        
        if success:
            new_markup = types.InlineKeyboardMarkup(row_width=3)
            btn_run = types.InlineKeyboardButton("▶️ تشغيل", callback_data=f"run_{bot_name}")
            btn_status = types.InlineKeyboardButton("📊 حالة", callback_data=f"status_{bot_name}")
            btn_delete = types.InlineKeyboardButton("🗑️ حذف", callback_data=f"delete_{bot_name}")
            new_markup.add(btn_run, btn_status, btn_delete)
            
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=new_markup
            )

    elif data.startswith('delete_'):
        bot_name = data.replace('delete_', '')
        bot_path = os.path.join(BOTS_DIR, bot_name)

        if not os.path.exists(bot_path):
            bot.answer_callback_query(call.id, "❌ البوت غير موجود!")
            return

        stop_bot_process(bot_name)
        
        try:
            shutil.rmtree(bot_path)
            
            bots_status = load_bots_status()
            if bot_name in bots_status:
                del bots_status[bot_name]
                save_bots_status(bots_status)
            
            bot.answer_callback_query(call.id, f"✅ تم حذف {bot_name}")
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"🗑️ تم حذف **{bot_name}** بنجاح!",
                parse_mode="Markdown"
            )
        except Exception as e:
            bot.answer_callback_query(call.id, f"❌ خطأ: {str(e)[:50]}")

    elif data.startswith('status_'):
        bot_name = data.replace('status_', '')
        bots_status = load_bots_status()
        
        if bot_name not in bots_status:
            bot.answer_callback_query(call.id, "❌ البوت غير موجود!")
            return

        info = bots_status[bot_name]
        status = "🟢 شغال" if info.get('running') else "🔴 متوقف"
        
        bot.answer_callback_query(
            call.id,
            f"{bot_name}: {status} | {info.get('date', '')}",
            show_alert=True
        )

# =========================================================
# معالج الأزرار النصية
# =========================================================

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    if not is_allowed(message.from_user.id):
        return

    text = message.text.strip()

    if text == "📂 قائمة البوتات":
        list_bots(message)
    elif text == "📤 رفع بوت جديد":
        upload_command(message)
    elif text == "🔄 إعادة تشغيل الكل":
        restart_all_command(message)
    elif text == "🛑 إيقاف الكل":
        stop_all_command(message)
    elif text == "📊 حالة السيرفر":
        server_status(message)

# =========================================================
# تشغيل البوت
# =========================================================

print("🚀 DWSHA BOT MANAGER IS RUNNING...")
print(f"📂 BOTS DIRECTORY: {BOTS_DIR}")
print("👨‍💻 @DWSHA_TOP")

bot.infinity_polling()
