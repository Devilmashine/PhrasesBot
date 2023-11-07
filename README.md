# PhrasesBot
Semantic core generation with ChatGPT
Создано https://t.me/Devilmashine

## Инструкция настройки
Все команды вводятся в Терминале.

Для запуска бота на локальной машине:

`
python -m venv myenv  # Создание виртуального окружения
source myenv/bin/activate  # Активация виртуального окружения
pip install -r requirements.txt  # Установка зависимостей
python main.py
`

## Установка на сервер
Пример настройки и запуска бота на сервисе https://www.pythonanywhere.com: https://youtu.be/mYlM4RWTHnk?si=5vCSCJp7Kc-ozJ3C

Требования: Убедитесь, что ваш сервер соответствует следующим требованиям:

Установленный интерпретатор Python версии 3.10+.
Установленный менеджер виртуальных окружений, например, `venv` или `virtualenv`.
Доступ к интернету для установки зависимостей.
Подготовка: Создайте новую директорию на сервере для проекта и перейдите в нее, загрузите и распакуйте в эту папку архив с ботом.

1. Создать виртуальное окружение

`
python -m venv myenv  # Создание виртуального окружения
source myenv/bin/activate  # Активация виртуального окружения
pip install -r requirements.txt  # Установка зависимостей
`

2. Изменить файл .env на свои значения

Пример файла .env:

`
BOT_TOKEN = "bot_token"
OPENAI_TOKENS = "token1,token2" #без пробелов через запятую
SQLALCHEMY_URL = "sqlite+aiosqlite:///db.sqlite3"
`

3. Запустить бота
`python main.py`

4. Отсановка бота
 В терминале нажимаем сочетание клавиш `Ctrl + C`

5. Деактивация виртуального окружения
`deactivate`


