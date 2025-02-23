import os
import logging
import json
from pyrogram import Client, filters
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Setup Logging
logging.basicConfig(level=logging.INFO)

# Telegram API Config
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Google Drive Config
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")  # Google Drive Folder ID where files will be uploaded
GDRIVE_CREDENTIALS = os.getenv("GDRIVE_CREDENTIALS")  # Google Drive Service Account JSON

# Write credentials.json file from the environment variable
if GDRIVE_CREDENTIALS:
    try:
        with open("credentials.json", "w") as f:
            f.write(GDRIVE_CREDENTIALS)
        logging.info("✅ Google Drive credentials.json created successfully.")
    except Exception as e:
        logging.error(f"❌ Error writing credentials.json: {str(e)}")
else:
    logging.error("❌ GDRIVE_CREDENTIALS environment variable is missing!")

# Authenticate Google Drive API
def get_gdrive_service():
    try:
        creds = Credentials.from_service_account_file("credentials.json", scopes=["https://www.googleapis.com/auth/drive"])
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        logging.error(f"❌ Google Drive Authentication Failed: {str(e)}")
        return None

# Upload File to Google Drive
def upload_to_drive(file_path, file_name):
    service = get_gdrive_service()
    if not service:
        return "❌ Google Drive authentication failed!"

    file_metadata = {"name": file_name, "parents": [GDRIVE_FOLDER_ID]}
    media = MediaFileUpload(file_path, resumable=True)

    try:
        file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        return f"https://drive.google.com/file/d/{file.get('id')}"
    except Exception as e:
        logging.error(f"❌ Upload Failed: {str(e)}")
        return f"❌ Upload Failed: {str(e)}"

# Initialize Telegram Bot
app = Client("gdrive_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Handle File Uploads
@app.on_message(filters.document | filters.video | filters.audio)
async def upload_file(client, message):
    msg = await message.reply_text("📤 Uploading to Google Drive...")

    # Download the file
    file_path = await message.download()
    
    # Extract file name
    file_name = (
        message.document.file_name if message.document else
        message.video.file_name if message.video else
        message.audio.file_name if message.audio else
        os.path.basename(file_path)
    )

    try:
        drive_link = upload_to_drive(file_path, file_name)
        await msg.edit_text(f"✅ Uploaded Successfully: [View File]({drive_link})")
        os.remove(file_path)  # Delete the file after upload
    except Exception as e:
        await msg.edit_text(f"❌ Upload Failed: {str(e)}")

# Start the bot
if __name__ == "__main__":
    app.run()
