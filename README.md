!
О микросервисе
Микросервис предоставляет API для работы с Tron-адресами, включая получение информации о балансе, bandwidth и energy.

Запуск с помощью Docker (рекомендуемый способ)
Требования
 Установленный Docker

 Установленный Docker Compose

Шаги для запуска
Клонируйте репозиторий:
 git clone https://github.com/репозиторий/tron-api.git
 cd tron-api

Создайте файл .env и укажите ваш API-ключ:
 echo "TRON_API_KEY=ваш_api_ключ_здесь" > .env

Соберите и запустите контейнер:
 docker-compose up -d --build


Сервис будет доступен по адресу:
 http://localhost:8000


Запуск без Docker
Требования
 Python 3.10+

 Установленный pip


Повторите шаги по клонированию репозитория
Создайте и активируйте виртуальное окружение:
 python -m venv venv
 source venv/bin/activate  # Linux/MacOS
 venv\Scripts\activate     # Windows


Установите зависимости:
 pip install -r requirements.txt


Создайте файл .env и укажите ваш API-ключ:

 echo "TRON_API_KEY=ваш_api_ключ_здесь" > .env


Запустите сервис:
 uvicorn app.main:app --reload


Сервис будет доступен по адресу:

http://localhost:8000



Использование API
Получение информации об адресе

POST /address-info/
Body: {"address": "TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7"}
Получение истории запросов

GET /queries/
Дополнительные команды


Для Docker
Просмотр логов: docker-compose logs -f tron-api

Пересборка: docker-compose up -d --build

Очистка: docker-compose down -v

Для локального запуска
Тесты: pytest tests/

Форматирование кода: black .

Проверка стиля: flake8

Переменные окружения
TRON_API_KEY - API ключ для Tron

DATABASE_URL - URL для подключения к БД (по умолчанию SQLite)