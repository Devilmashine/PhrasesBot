from pydantic import SecretStr
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    bot_token: SecretStr = SecretStr(os.getenv("BOT_TOKEN"))
    sqlalchemy_url: SecretStr = SecretStr(os.getenv("SQLALCHEMY_URL"))
    openai_tokens: str = os.getenv("OPENAI_TOKENS")


config = Settings()
