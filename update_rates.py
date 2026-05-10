from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os

api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]
string_session = os.environ["STRING_SESSION"]

client = TelegramClient(
    StringSession(string_session),
    api_id,
    api_hash
)

client.connect()

print("SUCCESS LOGIN")

client.disconnect()
