# Foodgram
![my badge](https://github.com/YuliaKhalaeva/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg) </p>
[foodgram доступен по ссылке](http://158.160.26.246/)<p></p>
[/admin доступен по ссылке](http://158.160.26.246/admin/)<p></p>
[документация доступна по ссылке](http://158.160.26.246/api/docs/redoc.html)<p></p>

* /admin email : yulia@foodgram.ru
* /admin username : yulia
* /admin password : 1



## Описание:<a class="anchor" id="about">
[к оглавлению](#contents)
[к следующему разделу](#tech)
Проект Foodgram представляет собой готовый API для разворачивания и поддержания приложения, собирающего отзывы
пользователей на различные произведения.
Приложение/API позволяет:
* публиковать рецепты
* подписываться на публикации других пользователей
* возможность добавлять в избранное рецепты
* создавать список покупок ингредиентов

## Технологии:<a class="anchor" id="tech">
[к оглавлению](#contents)
[к следующему разделу](#setup)
- Python
- Django
- DRF
- PostgreSQL

## Установка:<a class="anchor" id="setup">
[к оглавлению](#contents)

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:YuliaKhalaeva/foodgram-project-react.git
```
* Cоздать файл `.env` в директории `/infra/` с содержанием:

```
SECRET_KEY=секретный ключ django
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

* Перейти в директирию backend, обновить менеджер пакетов и установить зависимости из файла requirements.txt:

```bash
cd backend/
```

```bash
python -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

* Выполнить миграции:

```bash
python manage.py migrate
```

* Загрузить ингридиенты и теги:

```bash
python manage.py load_ingrs
```

```bash
python manage.py load_tags
```

* Собрать статику:

```bash
python manage.py collectstatic --noinput
```

