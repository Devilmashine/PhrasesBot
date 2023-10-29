BOT_TOKEN = "6629254913:AAGvBgdxJZMwS7mXx4kvhAiV3hZ1Hm3xvsQ"
OPENAI_TOKEN = "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"
SQLALCHEMY_URL = "sqlite+aiosqlite:///db.sqlite3"

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    # Желательно вместо str использовать SecretStr 
    # для конфиденциальных данных, например, токена бота
    bot_token: SecretStr

    # Начиная со второй версии pydantic, настройки класса настроек задаются
    # через model_config
    # В данном случае будет использоваться файла .env, который будет прочитан
    # с кодировкой UTF-8
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


# При импорте файла сразу создастся 
# и провалидируется объект конфига, 
# который можно далее импортировать из разных мест
config = Settings()