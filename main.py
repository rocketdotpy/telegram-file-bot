import os
import uuid
from datetime import datetime
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Configuration
BOT_TOKEN= 'Your-bot-token'
ADMIN_ID = 'rocket_0_07'  # Your Telegram username
STORAGE_FOLDER = 'file_storage'
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Ensure storage folder exists
os.makedirs(STORAGE_FOLDER, exist_ok=True)

bot = telebot.TeleBot(BOT_TOKEN)

# Database simulation (in a real app, use a proper database)
file_db = {}

def generate_file_id():
    return str(uuid.uuid4())

def save_file_info(file_id, original_name, file_type, file_size, uploader, caption=None):
    file_db[file_id] = {
        'original_name': original_name,
        'file_type': file_type,
        'file_size': file_size,
        'upload_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'uploader': uploader,
        'download_count': 0,
        'caption': caption or ""
    }

def increment_download_count(file_id):
    if file_id in file_db:
        file_db[file_id]['download_count'] += 1

def format_size(size):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def create_file_info_message(file_id):
    if file_id not in file_db:
        return "🚫 File not found in database"
    
    file_info = file_db[file_id]
    caption_display = f"\n📝 *Caption:* `{file_info['caption']}`" if file_info['caption'] else ""
    message = (
        f"📁 *File Information*\n\n"
        f"🔖 *Name:* `{file_info['original_name']}`\n"
        f"📦 *Type:* `{file_info['file_type']}`\n"
        f"📊 *Size:* `{format_size(file_info['file_size'])}`\n"
        f"📅 *Upload Date:* `{file_info['upload_date']}`\n"
        f"👤 *Uploader:* `{file_info['uploader']}`\n"
        f"📥 *Downloads:* `{file_info['download_count']}`"
        f"{caption_display}"
    )
    return message

@bot.message_handler(commands=['start','help'])
def handle_start(message):
    # Check if this is a file download request
    if len(message.text.split()) > 1 and message.text.split()[1].startswith('file_'):
        file_id = message.text.split('_')[1]
        if file_id in file_db:
            file_info = file_db[file_id]
            file_extension = os.path.splitext(file_info['original_name'])[1] if '.' in file_info['original_name'] else ''
            stored_filename = f"{file_id}{file_extension}"
            file_path = os.path.join(STORAGE_FOLDER, stored_filename)
            
            if os.path.exists(file_path):
                # Increment download count
                increment_download_count(file_id)
                
                # Prepare caption with file details
                caption = (
                    f"📁 *File Name:* {file_info['original_name']}\n"
                    f"📅 *Uploaded:* {file_info['upload_date']}\n"
                    f"👤 *Uploader:* {file_info['uploader']}"
                )
                
                # Add original caption if exists
                if file_info['caption']:
                    caption = f"📝 *Caption:* {file_info['caption']}\n\n" + caption
                
                # Send the file with caption
                with open(file_path, 'rb') as file_to_send:
                    if file_info['file_type'].startswith('image/'):
                        bot.send_photo(message.chat.id, file_to_send, caption=caption, parse_mode='Markdown')
                    elif file_info['file_type'].startswith('video/'):
                        bot.send_video(message.chat.id, file_to_send, caption=caption, parse_mode='Markdown')
                    elif file_info['file_type'].startswith('audio/'):
                        bot.send_audio(message.chat.id, file_to_send, caption=caption, parse_mode='Markdown')
                    else:
                        bot.send_document(message.chat.id, file_to_send, caption=caption, parse_mode='Markdown')
            else:
                bot.reply_to(message, "❌ File not found in storage")
        else:
            bot.reply_to(message, "❌ Invalid file link")
    else:
        # Show normal start message if not a file request
        welcome_msg = (
            "🌟 *Welcome to File Storage Bot!* 🌟\n\n"
            "📤 *How to use:*\n"
            "1. Simply send me any file (document, photo, video, audio)\n"
            "2. I'll store it and give you a download link\n"
            "3. Share the link with others\n\n"
            "🔒 *Privacy:* Your files are stored securely and only accessible via the generated links."
        )
        bot.reply_to(message, welcome_msg, parse_mode='Markdown')

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if str(message.from_user.username) != ADMIN_ID:
        bot.reply_to(message, "⛔ *Access Denied!* You're not admin!", parse_mode='Markdown')
        return
    
    total_files = len(file_db)
    total_size = sum(f['file_size'] for f in file_db.values())
    stats_msg = (
        "📊 *Bot Statistics*\n\n"
        f"📂 *Total Files:* `{total_files}`\n"
        f"🗃️ *Total Storage Used:* `{format_size(total_size)}`\n"
        f"📥 *Total Downloads:* `{sum(f['download_count'] for f in file_db.values())}`"
    )
    bot.reply_to(message, stats_msg, parse_mode='Markdown')

@bot.message_handler(commands=['cleanup'])
def cleanup_files(message):
    if str(message.from_user.username) != ADMIN_ID:
        bot.reply_to(message, "⛔ *Access Denied!* You're not admin!", parse_mode='Markdown')
        return
    
    # Create confirmation keyboard
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("✅ Yes, delete all", callback_data="cleanup_confirm"),
        InlineKeyboardButton("❌ Cancel", callback_data="cleanup_cancel")
    )
    
    bot.reply_to(message, "⚠️ *WARNING!* This will delete ALL stored files. Continue?", 
                 reply_markup=keyboard, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('cleanup'))
def handle_cleanup_callback(call):
    if call.data == "cleanup_confirm":
        # Delete all files
        for filename in os.listdir(STORAGE_FOLDER):
            file_path = os.path.join(STORAGE_FOLDER, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
        
        # Clear database
        file_db.clear()
        
        bot.edit_message_text("🧹 *All files have been deleted!*", 
                             call.message.chat.id, call.message.message_id, 
                             parse_mode='Markdown')
    elif call.data == "cleanup_cancel":
        bot.edit_message_text("✅ *Cleanup canceled.*", 
                             call.message.chat.id, call.message.message_id, 
                             parse_mode='Markdown')

@bot.message_handler(content_types=['document', 'photo', 'video', 'audio', 'voice'])
def handle_file(message):
    try:
        # Check if there's a caption
        caption = message.caption if message.caption else None
        
        # Get file information
        if message.document:
            file_info = bot.get_file(message.document.file_id)
            original_name = message.document.file_name
            file_type = message.document.mime_type
            file_size = message.document.file_size
        elif message.photo:
            file_info = bot.get_file(message.photo[-1].file_id)
            original_name = f"photo_{file_info.file_id}.jpg"
            file_type = "image/jpeg"
            file_size = file_info.file_size
        elif message.video:
            file_info = bot.get_file(message.video.file_id)
            original_name = message.video.file_name if message.video.file_name else f"video_{file_info.file_id}.mp4"
            file_type = message.video.mime_type
            file_size = message.video.file_size
        elif message.audio:
            file_info = bot.get_file(message.audio.file_id)
            original_name = message.audio.file_name if message.audio.file_name else f"audio_{file_info.file_id}.mp3"
            file_type = message.audio.mime_type
            file_size = message.audio.file_size
        elif message.voice:
            file_info = bot.get_file(message.voice.file_id)
            original_name = f"voice_{file_info.file_id}.ogg"
            file_type = "audio/ogg"
            file_size = message.voice.file_size
        else:
            bot.reply_to(message, "❌ Unsupported file type")
            return

        # Check file size
        if file_size > MAX_FILE_SIZE:
            bot.reply_to(message, f"📛 *File too large!* Max size is {format_size(MAX_FILE_SIZE)}", 
                         parse_mode='Markdown')
            return

        # Generate unique file ID
        file_id = generate_file_id()
        file_extension = os.path.splitext(original_name)[1] if '.' in original_name else ''
        stored_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(STORAGE_FOLDER, stored_filename)

        # Download the file
        downloaded_file = bot.download_file(file_info.file_path)
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Save file info
        uploader = f"@{message.from_user.username}" if message.from_user.username else str(message.from_user.id)
        save_file_info(file_id, original_name, file_type, file_size, uploader, caption)

        # Create download link
        download_url = f"https://t.me/{bot.get_me().username}?start=file_{file_id}"
        
        # Create keyboard with file info button
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("ℹ️ File Info", callback_data=f"info_{file_id}"))
        
        # Send success message
        caption_msg = f"\n📝 *Caption:* `{caption}`" if caption else ""
        success_msg = (
            f"✅ *File stored successfully!*\n\n"
            f"📄 *Name:* `{original_name}`\n"
            f"🔗 *Download Link:* [Click Here]({download_url})"
            f"{caption_msg}\n\n"
            f"📌 *Share this link to allow others to download the file*"
        )
        bot.reply_to(message, success_msg, 
                     reply_markup=keyboard, 
                     parse_mode='Markdown', 
                     disable_web_page_preview=True)

    except Exception as e:
        bot.reply_to(message, f"❌ *Error!* Failed to process file: {str(e)}", parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text and message.text.startswith('/start file_'))
def handle_file_download(message):
    try:
        file_id = message.text.split('_')[1]
        if file_id in file_db:
            file_info = file_db[file_id]
            file_extension = os.path.splitext(file_info['original_name'])[1] if '.' in file_info['original_name'] else ''
            stored_filename = f"{file_id}{file_extension}"
            file_path = os.path.join(STORAGE_FOLDER, stored_filename)
            
            if os.path.exists(file_path):
                # Increment download count
                increment_download_count(file_id)
                
                # Prepare caption
                caption = f"📥 *File:* {file_info['original_name']}"
                if file_info['caption']:
                    caption += f"\n📝 *Caption:* {file_info['caption']}"
                caption += f"\n👤 *Uploaded by:* {file_info['uploader']}"
                
                # Send the file with caption
                with open(file_path, 'rb') as file_to_send:
                    if file_info['file_type'].startswith('image/'):
                        bot.send_photo(message.chat.id, file_to_send, caption=caption, parse_mode='Markdown')
                    elif file_info['file_type'].startswith('video/'):
                        bot.send_video(message.chat.id, file_to_send, caption=caption, parse_mode='Markdown')
                    elif file_info['file_type'].startswith('audio/'):
                        bot.send_audio(message.chat.id, file_to_send, caption=caption, parse_mode='Markdown')
                    else:
                        bot.send_document(message.chat.id, file_to_send, caption=caption, parse_mode='Markdown')
            else:
                bot.reply_to(message, "❌ File not found in storage")
        else:
            bot.reply_to(message, "❌ Invalid file link")
    except Exception as e:
        bot.reply_to(message, f"❌ Error downloading file: {str(e)}")

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    bot.reply_to(message, "📤 Please send me a file to store, or use /help for instructions")

@bot.callback_query_handler(func=lambda call: call.data.startswith('info_'))
def handle_file_info_callback(call):
    file_id = call.data.split('_')[1]
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, create_file_info_message(file_id), parse_mode='Markdown')

if __name__ == '__main__':
    bot.remove_webhook()
    print("🤖 Bot is running...")
    bot.infinity_polling()
