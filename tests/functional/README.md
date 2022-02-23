## Тесты для сервиса FastAPI

Тесты работают отдельно от основных сервисов. Для тестирования собирается конейнер FastAPI из корневой директории проекта.
Тестовые данные содержатся в [директории](https://github.com/SergeyP1990/async-api/tree/main/tests/functional/docker/elasticsearch), из которой собирается тестовый сервис Elasticsearch. Данные разворачиваются в контейнер при сборке.

### Требования:
  - python3 >= 3.8.10
  - [docker-compose](https://docs.docker.com/compose/install/) >= 1.29.2


### Запуск:
1) На примере .env_example создать в директории с тестами файл .env и заполнить его необходимыми данными
2) Запустить docker-compose
  ```
  docker-compose up -d --build
  ```
3) Результаты тестов можно посмотреть командой `docker-compose logs tests`
