daily:
	cd py && python ./get.py
get:
	cd py && python ./get.py
register:
	cd py %&& python ./register.py
up:
	docker-compose up -d
init:
	# django-admin startproject config .
	# python manage.py startapp weather_data
	
migrate:
	python manage.py migrate