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
    try:
        # Read credentials from environment variable
        credentials_json = os.getenv("GDRIVE_CREDENTIALS")
        if not credentials_json:
            logging.error("❌ GDRIVE_CREDENTIALS environment variable is missing!")
            return None

        # Write credentials to a file
        with open("credentials.json", "w") as f:
            f.write(credentials_json)

        creds = Credentials.from_service_account_file("credentials.json", scopes=["https://www.googleapis.com/auth/drive"])
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        logging.error(f"❌ Google Drive authentication failed: {e}")
        return None

# Upload File to Google Drive
def upload_to_drive(file_path, file_name):
    service = get_gdrive_service()
    if service is None:
        return None, "Google Drive authentication failed"

    try:
        file_metadata = {"name": file_name, "parents": [GDRIVE_FOLDER_ID]}
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        file_link = f"https://drive.google.com/file/d/{file.get('id')}"
        return file_link, None
    except Exception as e:
        logging.error(f"❌ Upload failed: {e}")
        return None, str(e)

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

    # Upload to Google Drive
    drive_link, error = upload_to_drive(file_path, file_name)

    if drive_link:
        await msg.edit_text(f"✅ Uploaded Successfully: [View File]({drive_link})")
    else:
        await msg.edit_text(f"❌ Upload Failed: {error}")

    # Clean up downloaded file
    os.remove(file_path)

# Start the bot
if __name__ == "__main__":
    app.run()
