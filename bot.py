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
  "private_key_id": "87b18326bd469ddc304811d11a691ace2326722a",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCiGJIAvZAFePOl\nrIjjSjkJ3E8vsNxu4SW1AWz8wRVh/UYV1NJIeftjwneMLP9XN1e6IPV3XBDY4V5F\nv9H1ME7CuV8vKVsNRzLMZ7M346TepJ2D3hRZhIbkUI/YDY+njL5BqFTSqAGTvIbP\nzIxtZOpFh4+Xc5L0nzbVARq50py/wp813dBaK+3IEmQFOJ2JkMi/uONpmcTOkjCq\nyDUHHnvWir1LtH3liU9WVmHV5mfAqk4yVVceDUHAPQoVPKZX+3rzEX9oSnHRUy1r\nF0KvRV9w07ba2PJ8Pra3f1aJW7yKoNOl+bE/gGMPrGZUGNCg88HDF92cIl7DR+T0\ne4hL+zDTAgMBAAECggEAL+Q4hvV67tL8ka93RkgwsAQidUG47x2gSWlhbRATJD9z\njJGzi2xW5POY5JaK3pbgWYLRY3GVHK8BbnQtMVcTfh7My59ZYoPts0zUO6gLlyhl\nzYc41fX88MoIpdnj3qoLsFRus0qmJKMn5Y9W0h9lxCM4PpQMEDBWP/qyjcJ3Q4Rh\nWF0EZV0DcPDHD4Al71Wgzk1Xz2Z3WEApucMuCjFSaBxM1TesmiicfOtAG7UR//Gz\n34idXjAJJehCF3xon4kAApb7QrfLy9bn2m8ahuiKMNAMgntNs8C0z0ix1u5133C7\nNh+uk0hef6/h38oZAv6YtQgTN0sL1fDE3O7Lv00RaQKBgQDbTtPMDeS9FqCNgKbE\nrvOEL0NWLEaPvQXlQ/cVDR0iwszM8unAhTP3kQv1sCX8YYptblQJVpu2R9tJkncq\nP9uzTcAoRPd7DCDOFd7zaEnekXg/T1gOnv7MZ9eyaOK8QsFwWgtT95a3WrmRv6qg\n1f8R5sTV//5MChkigCGDMV+GRwKBgQC9N0yxpdvZyqDCdTDZ9Ul74dwG4+TXS4rQ\naCPnn5TZBm6jtebB8/hxYtmUf7E+176WHcGyzdZTIsvdT0uLkEuuDh8WyBxrjpj8\nP+G2SFtGk3cOHOlY9nT2ziJltwswdbBddG3A6l/ROkB1DGzoKOI1M0TkoqEGIxa9\nTV39kQ7rFQKBgDg0b5twRBsh3WvmeNcXb1mFM2C2YC8eZpBnZr+CaOErw4kTCE1K\n1hKwnbwNtO6FoRCCog7yn12L9OtaGig9zXSajJDFfBeQ+CdY+5auN6BO795p20uD\n/BEu29zhfJp7EVBWA2k1nu7G1aBA2t31ejWASxn9TZL3U5G//Na+pJipAoGAZnTu\nO3eDD3BwEjvg4vS2ALWxLa3zOT03glgRsRcxQz7/Y/hYZoeT7NnI1Wc7c7rhAWpF\ne2uH9WZvG3wXfQ/6WtpcrTpYYUlKv7RbpReTDSlGm0a+eCSj+wxthcRS87+Wa1Rj\nJcYDckjnpDnBMwkITCRh1qfVJ3ySkJi3H1mPyW0CgYEAkOB/nyeuXaPo7JuE59zI\nGCpXGt1rcyUrgeq5tQ6tTG4JmGZZPjg+XQwalhq3i9LX/BKv5dk0BByxQVMYxCZi\nOlDHQbWUx7jJOPsJn4XdVj+5xXmKc8Xf97eGcpXcdkRCea7zZINgjcrhcJp71IQQ\nTqea2JWrUtS7BpVmYBYP0kc=\n-----END PRIVATE KEY-----\n",
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
