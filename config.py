from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: SecretStr
    sqlalchemy_url: SecretStr
    openai_tokens: str


config = Settings()
