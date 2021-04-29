# flask_project
Flask-based project for Yandex Liceym

main.py - главный исполняемый файл. Запускать надо его
все html формы хранятся в папке templates, а картинки в static/img
restful-api: users_resources.py и games_resources.py
классы sqlalchemy: users.py, games.py, genres.py, comments.py

Если у вас не запускается проект, то необходимо скачать python-Levenshtein
Вот ссылка: http://www.lfd.uci.edu/~gohlke/pythonlibs/#python-levenshtein.
Выберите последнюю версию, подходящую под вашу систему (32 или 64 бит).
После загрузки необходимо перейти в директорию, где лежит скачаный файл и запустить
через консоль команду: pip install <название скачанного файла>.
Без этого поиск по играм не заработает, а через репо устанавливать бесполезно - выдаёт ошибку.