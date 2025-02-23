import os
import logging
from pyrogram import Client, filters
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Telegram API Config
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Google Drive Config
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")  # Google Drive Folder ID where files will be uploaded

# Initialize Telegram Bot
app = Client("gdrive_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Setup Logging
logging.basicConfig(level=logging.INFO)

# Authenticate Google Drive API
def get_gdrive_service():
    creds = Credentials.from_service_account_file("credentials.json", scopes=["https://www.googleapis.com/auth/drive"])
    return build("drive", "v3", credentials=creds)

# Upload File to Google Drive
def upload_to_drive(file_path, file_name):
    service = get_gdrive_service()
    file_metadata = {"name": file_name, "parents": [GDRIVE_FOLDER_ID]}
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return f"https://drive.google.com/file/d/{file.get('id')}"

# Handle File Uploads
@app.on_message(filters.document | filters.video | filters.audio)
async def upload_file(client, message):
    msg = await message.reply_text("📤 Uploading to Google Drive...")

    file_path = await message.download()
    file_name = message.document.file_name if message.document else message.video.file_name if message.video else message.audio.file_name

    try:
        drive_link = upload_to_drive(file_path, file_name)
        await msg.edit_text(f"✅ Uploaded Successfully: [View File]({drive_link})")
        os.remove(file_path)
    except Exception as e:
        await msg.edit_text(f"❌ Upload Failed: {str(e)}")

# Start the bot
app.run()
