"""
services/growth-bot/publishers.py
Multi-channel social media dispatch handlers for Telegram, Discord, and X (Twitter).
"""

import os
import logging
from typing import Optional, Dict, Any
import requests

logger = logging.getLogger("SocialPublishers")


class TelegramPublisher:
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.is_configured = bool(self.bot_token and self.chat_id)

    def publish(self, text: str, image_path: Optional[str] = None) -> bool:
        if not self.is_configured:
            logger.info("[Telegram] Not configured (missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID). Skipping live send.")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}"
        try:
            if image_path and os.path.exists(image_path):
                endpoint = f"{url}/sendPhoto"
                with open(image_path, "rb") as photo:
                    data = {"chat_id": self.chat_id, "caption": text, "parse_mode": "HTML"}
                    res = requests.post(endpoint, data=data, files={"photo": photo}, timeout=10)
            else:
                endpoint = f"{url}/sendMessage"
                payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}
                res = requests.post(endpoint, json=payload, timeout=10)

            if res.status_code == 200:
                logger.info("[Telegram] Post published successfully!")
                return True
            else:
                logger.error(f"[Telegram] Failed: {res.status_code} - {res.text}")
                return False
        except Exception as e:
            logger.error(f"[Telegram] Exception during publish: {e}")
            return False


class DiscordPublisher:
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
        self.is_configured = bool(self.webhook_url)

    def publish(self, text: str, image_path: Optional[str] = None) -> bool:
        if not self.is_configured:
            logger.info("[Discord] Not configured (missing DISCORD_WEBHOOK_URL). Skipping live send.")
            return False

        try:
            if image_path and os.path.exists(image_path):
                with open(image_path, "rb") as f:
                    files = {"file": (os.path.basename(image_path), f, "image/png")}
                    data = {"content": text}
                    res = requests.post(self.webhook_url, data=data, files=files, timeout=10)
            else:
                res = requests.post(self.webhook_url, json={"content": text}, timeout=10)

            if res.status_code in (200, 204):
                logger.info("[Discord] Post published successfully!")
                return True
            else:
                logger.error(f"[Discord] Failed: {res.status_code} - {res.text}")
                return False
        except Exception as e:
            logger.error(f"[Discord] Exception during publish: {e}")
            return False


class TwitterPublisher:
    """X (Twitter) API v2 publisher."""
    def __init__(self):
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_secret = os.getenv("TWITTER_ACCESS_SECRET")
        self.is_configured = bool(self.api_key and self.api_secret and self.access_token and self.access_secret)

    def publish(self, text: str, image_path: Optional[str] = None) -> bool:
        if not self.is_configured:
            logger.info("[X / Twitter] Not configured (credentials missing in .env). Skipping live send.")
            return False

        try:
            # Note: Requires requests-oauthlib or tweepy if credentials provided
            from requests_oauthlib import OAuth1
            auth = OAuth1(self.api_key, self.api_secret, self.access_token, self.access_secret)

            media_id = None
            if image_path and os.path.exists(image_path):
                # Upload media via v1.1 upload endpoint
                upload_url = "https://upload.twitter.com/1.1/media/upload.json"
                with open(image_path, "rb") as img_file:
                    res_media = requests.post(upload_url, auth=auth, files={"media": img_file}, timeout=15)
                if res_media.status_code == 200:
                    media_id = res_media.json().get("media_id_string")

            # Post tweet via v2 endpoint
            tweet_url = "https://api.twitter.com/2/tweets"
            payload: Dict[str, Any] = {"text": text}
            if media_id:
                payload["media"] = {"media_ids": [media_id]}

            res = requests.post(tweet_url, auth=auth, json=payload, timeout=10)
            if res.status_code in (200, 201):
                logger.info("[X / Twitter] Tweet posted successfully!")
                return True
            else:
                logger.error(f"[X / Twitter] Failed: {res.status_code} - {res.text}")
                return False
        except Exception as e:
            logger.error(f"[X / Twitter] Exception during tweet: {e}")
            return False
