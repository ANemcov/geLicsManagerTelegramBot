# Readme

запуск: main.py

Настройки могут задаваться:

1. через файл config.ini (см. пример config.ini.example)
2. через переменные окружения (см. пример production.env.example)

Назначение параметров:

- **telegram_bot_token** - токен для Телеграм-бота, который будет заниматься обработкой команд
- **bitmobile_host** - адрес подключения к серверу БИТ.Мобайл
- **root_password** - пароль администратора от сервера БИТ.Мобайл

Запуск в Docker

1. Установить параметры в файле config.ini
2. либо передать их через переменные окружения (рекомендованный вариант)
3. собрать контейнер ```docker build -t license-bot .```
4. собрать на Mac с поддержкой Linux (кроссплатформенная компиляция) ```docker buildx build --platform linux/amd64 -t anemcov/ge-lic-bot:webapp --push .```
5. запустить контейнер ```docker run --rm license-bot```

Пример запуска из командной строки:  

```shell
docker run -d \
--name lic-bot \
--env-file test.env \
--label traefik.enable=true \
--label traefik.http.routers.licbot.rule=Host\(`licbot.example.com`\) \
--label traefik.http.routers.licbot.entrypoints=websecure \
--label traefik.http.routers.licbot.tls.certresolver=myresolver \
--label traefik.http.services.licbot.loadbalancer.server.port=8000 \
--network traefik \
--log-driver json-file \
--log-opt max-size=10m \
--log-opt max-file=3 \
anemcov/ge-lic-bot:webapp
```

Задай WebApp URL:

`/setdomain`

Укажи:

`licbot.example.com`

Установи WebApp URL через Bot API

```http
POST https://api.telegram.org/bot<YOUR_TOKEN>/setChatMenuButton
Content-Type: application/json

{
  "menu_button": {
    "type": "web_app",
    "text": "Открыть панель",
    "web_app": {
      "url": "https://licbot.example.com/app"
    }
  }
}
```
