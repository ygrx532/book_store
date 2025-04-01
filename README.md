## Bookstore App
Implemented as a course project for CMU course 17647 Engineering Data Intensive Scalable Systems. Programmed using Django. 

To start the server, use command:
```
# Base URL: 127.0.0.1:8000/book_store_app
python manage.py runserver
```

For building the docker image
```
docker build --rm --tag ygrx532/bookstore_backend:<tag> .
```

For running the docker image in the background
```
$ docker run -d -p 8000:8000 ygrx532/bookstore_backend:<tag>
```

For entering the shell
```
$ docker run -p 80:8000 -it --entrypoint /bin/sh ygrx532/bookstore_backend:<tag>
```
