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

# Embedded Google Drive Credentials
GDRIVE_CREDENTIALS = {
    "type": "service_account",
    "project_id": "clonebot-451709",
    "private_key_id": "3e1c39b01a3f4f092119615e3eddcddee905d3fc",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCljsbmpVmTNkEb\nJV1M/MJf1iwoXhh6ZX71FIw+CRgYi0jWZ0cGt6PZ4YJ/k2HXNNRUII/ExnI8f0C6\nluRjKvib2NN0Ro1ibQkIaqhMwM5RYLyXrvkG8hhWoIF8+8U2vjuw4Jd7oAW+7oH4\nEvbZ/LzfEiL4y5YRdHX4N8qO3srpzJx+FoKZUuBewMuXsKXP4kTKyFjkdgFqHxJF\nQ4l6CG0xOGG5nDeCyyWwTsMpEZXSHyjTsf9w0iGuTtXVGQwrAHW5kP5geTk2XJLB\nn6fnBKCStXdBOE8i9k/0qDwErTQHGVrVerVz66x0V274sCQmEsGbwDcPf6dNSg7P\njvdaqqSvAgMBAAECggEADaYeuccqAlv3tCA5d+5iq/oBO/a99+FEPTpLcZXYWbWp\n9JshHOmo5X6U/qWM7GwbkS/6ClP9+QTYtklYXOCfDGIs1Ko4X8PzebEpXOKMX+Mk\nyTCQsUTmQsYKxt4O3TuDukpZ0sRXlO0e4+/UUBZpD87z+ST3o0rBqwwWc/7kJbAp\nyD8R/tV9fCo59o8vV67rJP3v1teA4wUX+quz4tzQmy53TcBV8H8yfvqLOEugSt6h\n0KWg7ADvcVEVV+Asjzlkcby4TlPVnPrkC1MYiJjKlVkxxZ8ZVZQf2TMxEJXoH4WI\nP8hgWV98XXS4FbDaZDVWSnuhLJBkbL9YAzD6IG76sQKBgQDP9AarSXC82hmiy/vw\nF7md5tQsoAaGO9rN0s1JbBRdtVH69+wLs6KrioNPDIuKQO3CluBGyNYCavDKuvBT\nJZKT+CkoUNduzC2+ZOrom4M4SvQxP+0mq6xsgLnc2cS3M750TFDOfnGnogQQ8pnl\n9k5kkayXcYuqODZ9jRtIzXi+2QKBgQDLzyaGb+PUUDc9OiTps+HTSm9rS25/wHxR\nuZiTOpm63I3SulBVdxH4sbWN2NLGUeU5u8eOB9fy/02eRQ/TuatNrvdyOhQr4u71\nbIZSDHknjRWC5gIZOXthqSNg7mdjUHUc9jSOgqH5N0pvG+KX+IiXnGSpUin0yLWG\n//oKHqZaxwKBgCKmXpYb3pUZIjxmEMyop10QITpuT6f+QS8aeOpK//m9RLO0q7gn\nbmt24PpC9N1MhFFwIl6pCD/O4eBl1bWFBS9yoij9j2f+zYB0AFBR2UN/+cBbDoDr\nCgfqSw3pm0WLcaifLre5ieaMsHDCe7I9oEJRo5h4avUp+Kpi4LD4y63BAoGAcdRJ\npQ47BeqjX3vo/+nqt7K8FgX0Oj/Mb2ykLZ6uG7JxN3+9vG4bSHYge4/c8MzupNce\n9lGlJ9+1fy79TvhFF8cgBtkvSO+fHM23G35B8HgYypoiE+qJ4Zqw2sNsVQir0Dgm\nVG3bfzCFTxcY8F3sFBlSE0uDiWbMFBFFmn9R1CMCgYEAmxPM0c+l1N6smU3uSs4a\n+LrYXbG84g96OTg+Ibuw9G1tHZXNb8S4UeyZ+W8rcdoqSFqhNdh/wsRa+C0TQFsw\nP2RNU9fLZCiPKWGQuMmvoxb2LiuAcN06BuOf5P6FmL0SVvq/lULvRyh4caihLgL6\nLzMllBtEKxQBij8ni4YKWo8=\n-----END PRIVATE KEY-----\n",
    "client_email": "cloneacc@clonebot-451709.iam.gserviceaccount.com",
    "client_id": "107491569406351809755",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/cloneacc%40clonebot-451709.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# Initialize Telegram Bot
app = Client("gdrive_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Setup Logging
logging.basicConfig(level=logging.INFO)

# Authenticate Google Drive API
def get_gdrive_service():
    try:
        creds = Credentials.from_service_account_info(GDRIVE_CREDENTIALS, scopes=["https://www.googleapis.com/auth/drive"])
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
