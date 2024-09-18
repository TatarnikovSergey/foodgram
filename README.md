# Foodgram

## О проекте:
Сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд

## Стек технологий:
- Python 3.9
- Django 3.2.16
- Django REST framework 3.12.4
- Nginx
- Docker
- PostgreSQL
## Как запустить проект:
### Установка
1. Склонируйте репозиторий и перейдите в него:
```console
git clone git@github.com:TatarnikovSergey/foodgram.git
```
```console
cd foodgram
```
2. Создайте файл `.env`, в нём должны быть указаны переменные окружения, образец заполнения можно посмотреть в файле `.env.example`, который лежит в корневой директории проекта.
3. Установите Docker, последовательно выполняя команды:
```console
sudo apt update
```
```console
sudo apt install curl
```
```console
curl -fsSL https://get.docker.com -o get-docker.sh
```
```console
sudo sh ./get-docker.sh
```
Обязательно проверьте что `Docker` работает:
```console
docker --version
```
Если вы увидели что-то вроде:
```
Docker version 27.1.1, build 6312585
```
Значит `Docker` установлен успешно! Можно переходить к следующему этапу.

### Создание образов Docker
1. Сбилдите образы, замените `username` на ваш логин на DockerHub:
```console
cd foodgram/backend
docker build -t username/foodgram_backend .
cd ../frontend
docker build -t username/foodgram_frontend .
cd ../infra
docker build -t username/foodgram_gateway .
```
2. Загрузите уже готовые образы на DockerHub, замените `username` на ваш логин на DockerHub:
```console
docker push username/foodgram_backend
docker push username/foodgram_frontend
docker push username/foodgram_gateway
```

### Деплой

#### Пояснение:
`ssh-path` - Путь к файлу с закрытым SSH-ключом.\
`ssh` - Файл с закрытым SSH-ключом.\
`user` - Имя вашего пользователя на сервере.\
`host` - IP-адрес вашего сервера.

1. Подключитесь к вашему серверу, например вот так:
```console
ssh -i ssh-path/ssh user@host
```
2. Создайте директорию в которой будет храниться файл с переменными окружения - `.env`,\
а также композиционный файл - `docker-compose.production.yml`:
```console
sudo mkdir foodgram
```
3. Установите на сервер Docker, как делали это на этапе установки, а затем Docker Compose:
```console
sudo apt update
```
```console
sudo apt install curl
```
```console
curl -fsSL https://get.docker.com -o get-docker.sh
```
```console
sudo sh ./get-docker.sh
```
```console
sudo apt install docker-compose
```
Проверьте что Docker Compose работает:
```console
docker-compose --version
```
Вы должны увидеть версию, если ее нет, значит возникла ошибка установки, внимательно проверьте всё ли правильно вы ввели:
```
Docker Compose version v2.29.1
```
4. Скопируйте локальные файлы `docker-compose.production.yml` и `.env` в директорию `kittygram` на сервере.\
Это можно сделать вручную, но удобнее и быстрее всего это будет сделать через консоль:
```console
sudo scp -i ssh-path/ssh docker-compose.production.yml user@host:/home/user/foodgram/docker-compose.production.yml
```
```console
sudo scp -i ssh-path/ssh .env user@host:/home/user/foodgram/.env
```
5. Скачайте все образы с вашего профиля:
```console
sudo docker-compose -f /home/user/foodgram/docker-compose.production.yml pull
```
5. Запустите Docker Compose в фоновом режиме:
```console
sudo docker-compose -f /home/user/foodgram/docker-compose.production.yml up -d
```
6. Выполните миграции, соберите статику и скопируйте ее в `/static/static/`:
```console
sudo docker-compose -f /home/user/foodgram/docker-compose.production.yml exec backend python manage.py migrate
```
```console
sudo docker-compose -f /home/user/foodgram/docker-compose.production.yml exec backend python manage.py collectstatic
```
```console
sudo docker-compose -f /home/user/foodgram/docker-compose.production.yml exec backend cp -r /app/static/. /backend_static/static/
```
7. Загрузите данные из `json` в базу данных:
```console
sudo docker-compose -f /home/user/foodgram/docker-compose.production.yml exec backend python manage.py load_ingredients
```
Вы должны увидеть статус `Success`, если всё прошло гладко:
```
SUCCESSFULLY LOADED `TAG` DATA
SUCCESSFULLY LOADED `INGREDIENT` DATA
```

### Настройка Nginx
1. Откройте конфигурационный файл `Nginx` в редакторе `Nano`:
```console
sudo nano /etc/nginx/sites-enabled/default
```
2. Измените настройки location в секции server:
```console
location / {
    proxy_set_header Host $http_host;
    proxy_pass http://127.0.0.1:8000;
}
```
Не забудьте нажать `Ctrl+S` чтобы сохранить изменения, а затем `Ctrl+X`, чтобы выйти из редактора `Nano`
3. Проверьте правильность конфигурации Nginx:
```console
sudo nginx -t
```
Вот такой ответ вы должны получить, если с конфигом всё нормально:
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```
4. Перезагрузите Nginx:
```console
sudo systemctl reload nginx
```
Провертье статус Nginx:
```console
sudo systemctl status nginx
```
Если Nginx запущен и работает как положено ждите такой ответ:
```
● nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2024-08-02 10:32:25 UTC; 22h ago
       Docs: man:nginx(8)
    Process: 38339 ExecStartPre=/usr/sbin/nginx -t -q -g daemon on; master_process on; (code=exited, status=0/SUCCESS)
    Process: 38341 ExecStart=/usr/sbin/nginx -g daemon on; master_process on; (code=exited, status=0/SUCCESS)
   Main PID: 38342 (nginx)
      Tasks: 3 (limit: 2219)
     Memory: 9.0M
        CPU: 2.152s
     CGroup: /system.slice/nginx.service
             ├─38342 "nginx: master process /usr/sbin/nginx -g daemon on; master_process on;"
             ├─38343 "nginx: worker process" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" ""
             └─38344 "nginx: worker process" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" ""
```
Nginx настроен, статика раздаётся, все страницы уже должны быть доступны в том виде, в котором они задумывались.
Теперь если вы перейдете по адресу `https://your-domain...` вам будет доступен полностью рабочий сервис `Foodgram`.


### Примеры запросов к API:
Регистрация пользователя:
```
POST  /api/users/
```
```
{
"email": "vpupkin@yandex.ru",
"username": "vasya.pupkin",
"first_name": "Вася",
"last_name": "Иванов",
"password": "Qwerty123"
}
```
Получение токена:
```
POST  /api/auth/token/login/
```
```
{
"password": "string",
"email": "string"
}
```
Получение списка рецептов:
```
GET  /api/recipes/
```
Создание рецепта:
Обратите внимание изображение передается кодировкой base64 !
```
POST  /api/recipes/
```
```
{
"ingredients": [
{
"id": 1123,
"amount": 10
}
],
"tags": [
1,
2
],
"image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
"name": "string",
"text": "string",
"cooking_time": 1
}
```

Автор: [TatarnikovSergey](https://github.com/TatarnikovSergey)