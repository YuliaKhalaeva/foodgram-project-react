# Foodgram

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
- SQLite3

## Установка:<a class="anchor" id="setup">
[к оглавлению](#contents)

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:YuliaKhalaeva/foodgram-project-react.git
```

```
cd foodgram-project-react
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

