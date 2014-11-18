
##Overview
* Реализация API для приложения на Flask
* Python 2.7

##Information
1. Используем SQLite для девелопинга.
2. Используем pip и requirements.txt для установки всех зависимостей (`$ pip install -r requirements.txt`).
3. Файл **run.py** необходим для запуска сервера.
4. Файл **shell.py** позволяет запускать консоль для отладки со всеми переменными окружения.
5. Файл **manage.py** используется для вызова скриптов-хелперов. Сейчас используется для просмотра всех путей, определнных в проекте.
 
##Structure
Структура проекта имеет следующий вид:
For every module (or sub app... ) we'll have this file structure (here for the `users` module):

```
app/users/__init__.py
/app/users/views.py
/app/users/forms.py
/app/users/constants.py
/app/users/models.py
/app/users/decorators.py
```

* models - описание модели
* decorators - декораторы (если нужно)
* constants - список констант
* views - вьюхи, в нашем случае контроллеры

> Мы используем [Blueprint!](http://flask.pocoo.org/docs/0.10/blueprints/) для модульности.

####Для создания модуля нового мы должны создать новую папку!

##Миграции

```
(env)user@Machine:~/cling_api/$ python shell.py 
>>> from app import db
>>> db.create_all()
>>> exit()
```

Это создаст SQLite файл app.db в корне.
 


