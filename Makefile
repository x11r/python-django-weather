daily:
	python ./manage.py weather_data_download --daily 1
get:
	cd py && python ./get.py
register:
	cd py %&& python ./register.py
init:
	# django-admin startproject config .
	# python manage.py startapp weather_data
install:
	python -m pip install -r docker/gunicorn/requirements.txt
	# Python ライブラリーをインストール
jupyter:
	# python manage.py shell_plus --notebook
	python -m jupyter notebook
migrate:
	python manage.py migrate
server:
	python manage.py runserver
up:
	docker-compose up -d