# Проект Мини Витрина

Домашнее задание по курсу Choco Python Bootcamp 2022

## Инструкции для запуска без докера

1. Клонируем репозиторий и переходим в корневую директорию проекта
```bash

cd mini_showcase
```
2. Создаем изолированную среду python, например с помощью [virtualenv](https://pypi.org/project/virtualenv)
```bash
virtualenv .venv
source .venv/bin/activate
```
3. Устанавливаем нужные пакеты через pip
```bash
pip install -r requirements/dev.txt
```
4. Запускаем веб сервис
```bash
python code/app.py
```
5. Увидем в консоли текст как ниже.  
```bash
[2022-01-30 20:57:07 +0600] [11880] [INFO] 
  ┌───────────────────────────────────────────────────────────────────────────────┐
  │                                 Sanic v21.12.1                                │
  │                        Goin Fast @ http://0.0.0.0:8000                       │
  ├───────────────────────┬───────────────────────────────────────────────────────┤
  │                       │     mode: production, single worker                   │
  │     ▄███ █████ ██     │   server: sanic                                       │
  │    ██                 │   python: 3.10.1                                      │
  │     ▀███████ ███▄     │ platform: Linux-5.15.11-arch2-1-x86_64-with-glibc2.33 │
  │                 ██    │ packages: sanic-routing==0.7.2                        │
  │    ████ ████████▀     │                                                       │
  │                       │                                                       │
  │ Build Fast. Run Fast. │                                                       │
  └───────────────────────┴───────────────────────────────────────────────────────┘

[2022-01-30 20:57:07 +0600] [11880] [WARNING] Sanic is running in PRODUCTION mode. Consider using '--debug' or '--dev' while actively developing your application.
[2022-01-30 20:57:07 +0600] [11880] [INFO] Starting worker [11880]
```
6. Делаем HTTP GET запрос на http://0.0.0.0:8000
```bash
curl -X 'GET' http://0.0.0.0:8000
```
7. Увидем ответ от веб сервиса
```json
{"test":true}
```

## Инструкции для запуска с докером

1. Клонируем репозиторий и переходим в корневую директорию проекта
```bash
cd mini_showcase
```
2. С помощью [docker-compose](https://docs.docker.com/compose/install/) собираем сервис.
```bash
docker-compose build
```
3. Поднимаем сервис
```bash
docker-compose up
```
4. Делаем HTTP GET запрос на http://127.0.0.1:8000/test
```bash
curl -X 'GET' http://127.0.0.1:8000/test
```
7. Увидем ответ от веб сервиса
```json
{"test":true}
```
