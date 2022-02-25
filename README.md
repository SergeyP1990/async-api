## Сервис, реализующий API кинотеатра на FastAPI согласно ТЗ


### Требования:
  - python3 >= 3.8.10
  - [docker-compose](https://docs.docker.com/compose/install/) >= 1.29.2
  - База данных с фильмами из предыдущих спринтов

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

### Задания
Задание из спринта соответствует _issue_, решение соответствует _pull request_, указанному в соответствующем issue.

Задания 5 спринта:

1) [Задание на ревью](https://github.com/SergeyP1990/async-api/issues/31) (в комментах к этому issue есть ссылки на issue с ревью)
2) [SOLID. Elastic Search](https://github.com/SergeyP1990/async-api/issues/32)
3) [SOLID. Redis](https://github.com/SergeyP1990/async-api/issues/33)
4) [SOLID. Views](https://github.com/SergeyP1990/async-api/issues/34)
5) [Функциональны тесты. Инф-ра](https://github.com/SergeyP1990/async-api/issues/35)
6) [Функциональны тесты. film](https://github.com/SergeyP1990/async-api/issues/36)
7) [Функциональны тесты. person](https://github.com/SergeyP1990/async-api/issues/37)
8) [Функциональны тесты. genre](https://github.com/SergeyP1990/async-api/issues/38)
9) [Функциональны тесты. search](https://github.com/SergeyP1990/async-api/issues/39)
10) [(Опицонально) OpenAPI документация](https://github.com/SergeyP1990/async-api/issues/40)
11) [(Опицонально) Exponential backoff](https://github.com/SergeyP1990/async-api/issues/41)




<details>
  <summary>Дефолтное сообщение из репы спринта</summary>
  # Проектная работа 4 спринта

  **Важное сообщение для тимлида:** для ускорения проверки проекта укажите ссылку на приватный репозиторий с командной работой в файле readme и отправьте свежее приглашение на аккаунт [BlueDeep](https://github.com/BigDeepBlue).

  В папке **tasks** ваша команда найдёт задачи, которые необходимо выполнить в первом спринте второго модуля.  Обратите внимание на задачи **00_create_repo** и **01_create_basis**. Они расцениваются как блокирующие для командной работы, поэтому их необходимо выполнить как можно раньше.

  Мы оценили задачи в стори поинтах, значения которых брались из [последовательности Фибоначчи](https://ru.wikipedia.org/wiki/Числа_Фибоначчи) (1,2,3,5,8,…).

  Вы можете разбить имеющиеся задачи на более маленькие, например, распределять между участниками команды не большие куски задания, а маленькие подзадачи. В таком случае не забудьте зафиксировать изменения в issues в репозитории.

  **От каждого разработчика ожидается выполнение минимум 40% от общего числа стори поинтов в спринте.**
</details>
