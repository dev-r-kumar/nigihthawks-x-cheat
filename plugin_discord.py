import aiohttp
import ssl


class DCPlugin:
    def __init__(self, url):
        self.url = url
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en",
            "Content-Type": "application/json",
            "Origin": "https://discord.org",
            "Referer": "https://discohook.org/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
        }

    async def sendMessageToDiscord(self, title, message):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        payload = {
            "content": None,
            "embeds": [
                {
                    "title": title,
                    "description": message,
                    "color": 16711680
                }
            ]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url=self.url, headers=self.headers, json=payload, ssl=ssl_context) as response:
                return "message sent !" if response.status in (200, 204) else "error, failed to send message !"


