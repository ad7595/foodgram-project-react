# Foodgram

Foodgram - это онлайн-платформа, где пользователи публикуют рецепты блюд, могут подписываться на других пользователей, добавлять рецепты в  «Избранное» и и выгружать продуктовые списки рецептов.

# Технологии:
- Pyhton 
- Django 
- Djoser 
- DRF
- PostgreSQL
- NGINX
- Gunicorn
- Docker

# Как развернуть проект локально:
Клонируйте проект из репозитория:

```
git clone https://github.com/ad7595/foodgram-project-react.git
```

Создайте и активируйте виртуальное окружение:
```
python -m venv venv
source venv/scripts/activate
```

Установите зависимости:
```
cd backend/foodgram
pip install -r requirements.txt
```

Создайте .env файл в директории infra/, с следующими переменными PostgreSQL, которые можно взять из файла settings.py:
```
DB_ENGINE=
DB_NAME=
POSTGRES_USER=
POSTGRES_PASSWORD=
DB_HOST=
DB_PORT=
TOKEN=
DEBUG=
```
Запустите Docker-контейнеры:
```
docker-compose up -d
```
Создайте и примините миграции:

```
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

Соберите статику: 
```
docker-compose exec backend python manage.py collectstatic --noinput
```

Импортируйте базу данных ингридиентов: 
```
docker-compose exec backend python manage.py import_ingredients
```

Создайте superuser'a:

```
docker-compose exec backend python manage.py createsuperuser
```
Проект доступен локально!
```
http://localhost/
http://127.0.0.1/
```
Проект доступен по домену:
```
http://foodgram-ad.hopto.org/
```

Для ревьюера Яндекс.Практикум создан суперпользователь с раннее указанными им раннее.
