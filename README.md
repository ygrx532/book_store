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

For running the recommendation service(running on port 80):
```
$ docker run -d -p 80:8080 pmerson/book-recommendations-ms --delay=5000
```
and go to localhost:80/swagger-ui.html