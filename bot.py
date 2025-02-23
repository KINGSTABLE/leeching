import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Google Drive API Setup
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'E:/DOWNLOADS/CLONEBOT/clonebot-451709-3e1c39b01a3f.json'  # Path to your JSON key file
TEAM_DRIVE_FOLDER_ID = '1xa81RJIZ_zPHboGZs_74fy9Whjcd0AaY'  # Folder ID in Team Drive

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = '6656285409:AAGchYWCtZs6Vf6DhAHmzQRjFn44NKDc6ZA'

# Initialize Google Drive API
def initialize_drive():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('drive', 'v3', credentials=creds)

# Upload file to Google Drive
def upload_to_drive(file_path, file_name):
    drive_service = initialize_drive()
    file_metadata = {
        'name': file_name,
        'parents': [TEAM_DRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        supportsAllDrives=True
    ).execute()
    return file.get('id')

# Telegram Bot Handlers
async def start(update: Update, context):
    await update.message.reply_text("Send me a file, and I'll upload it to Google Drive!")

async def handle_file(update: Update, context):
    file = await update.message.document.get_file()
    file_path = f"downloads/{file.file_id}_{file.file_name}"
    await file.download_to_drive(file_path)
    
    try:
        file_id = upload_to_drive(file_path, file.file_name)
        await update.message.reply_text(f"File uploaded to Google Drive! File ID: {file_id}")
    except Exception as e:
        await update.message.reply_text(f"Failed to upload file: {e}")
    finally:
        os.remove(file_path)

# Main Function
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    
    app.run_polling()