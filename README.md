## Сервис, реализующий API кинотеатра на FastAPI согласно ТЗ


### Требования:
  - python3 >= 3.8.10
  - [docker-compose](https://docs.docker.com/compose/install/) >= 1.29.2

### Установка:
1) Склонировать репозиторий
`git clone https://github.com/SergeyP1990/async-api`
2) Подправить путь до базы данных с фильмами, с которой будет работать ETL. Для этого в docker-compose.yaml в [строке](https://github.com/SergeyP1990/async-api/blob/7e64193e9a6775699b55ad7e125b1f1fe93d4056/docker-compose.yaml#L7), описывающей volume для базы, надо заменить `postgres_data` на путь до базы с фильмами.
3) На примере .env_example создать в корне репозитория файл .env и заполнить его необходимыми данными для авторизации в базе
4) Далее перейти в директорию с репозиторием и запустить docker-compose
  ```
  cd async-api
  docker-compose up -d --build
  ```
После успешного запуска потестировать API можно по адресу http://localhost/api/openapi
