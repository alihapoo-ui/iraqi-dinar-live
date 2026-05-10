from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os

api_id = int(os.environ["37665414"])
api_hash = os.environ["0ed2ccc8cd3f95cfd2cbd5feb2749ea7"]
string_session = os.environ["1ApWapzMBu8Crl8f0DyagRo9LgNi9LvN7wWkAWMHRPrI9HFhvIMYCK5ZGzLCkROayMSKdl3mPPxT5emlfe2rLAF4wWfdnJ8BvF8qK6MaR6XyzAqm2fwk0LF8eGin0kCbiqx-0MM3GJjtj1FseKezXKE49465rgVqbh8HO7Ra918Saig18MKZhGyCNbshsoOXvGid4FvK6FtDa7sbfwZaGwdkVIvEHOfdU-zm9DGyezUmli8mAxbBieu_K3mmxlO9ORV2MaKSRpN7UyHr7jCsO1QRww26E3sSCaYll-Kzkxr24dXinxZsvmMcPBL-Af-UHuEQk36aoV_xMuyCfSpbDO71fI6eQUVQ="]

client = TelegramClient(
    StringSession(string_session),
    api_id,
    api_hash
)

client.connect()

print("SUCCESS LOGIN")

client.disconnect()
