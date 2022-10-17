# quiz_bot
```sh
sudo apt install redis-server
```
## Чат-боты с технологией Dialogflow

Репозиторий содержит чат-боты для Телеграмма и социальной сети ВКонтакте. С помощью технологии Dialogflow от Google чат-боты позволяют автоматизировать ответы на наиболее частые вопросы. Это может быть использовано для снижения нагрузки на операторов техподдержки.  
Пример бота:

![alt tag](https://github.com/Corwin74/boltun_bot/blob/0d1e3c65fb870b1f2f85fd0ec71896ecbad29b8f/bot.gif)

## Как установить
Для начала работы необходимо:
- Скопировать репозиторий к себе на компьютер:
```
git clone git@github.com:Corwin74/https://github.com/Corwin74/boltun_bot.git
```
Далее, в корневой папке проекта необходимо создать файл `.env` и записать в него настройки в виде:
```
TLGM_TOKEN_BOT=<токен для бота, полученный от BotFather>
ADMIN_TLGM_CHAT_ID=<id пользователя в Телеграмм, которому будут отправляться уведомления о работе ботов>
PROJECT_ID=<имя вашего проекта в Dialogflow>
VK_API_TOKEN=<токен с полномочиями отправлять сообщения в сообщество ВКонтакте>
```
Зарегистрировать свой проект Dialogflow можно [здесь](https://dialogflow.cloud.google.com)

Затем используйте `pip` для установки зависимостей. Рекомендуется использовать отдельное виртуальное окружение.  
[Инструкция по установке виртуального окружения](https://dvmn.org/encyclopedia/pip/pip_virtualenv/)

```
pip install -r requirements.txt
```
Для использования Dialogflow необходимо выполнить следующие настройки:
 - Установить gcloud CLI по [инструкции](https://cloud.google.com/sdk/docs/install)
 - Из под аккаунта под которым будут запущены сервисы исполнить команду:
```
gcloud auth application-default login
```
далее выполнить вход под аккаунтом Google, к которому привязан Dialogflow
- Подключить свой проект Dialogflow командами:
```
gcloud auth application-default set-quota-project <имя проекта в Dialogflow>
gcloud config set project <имя проекта в Dialogflow>
gcloud auth login
```

## Запуск и использование
Для запуска бота необходимо ввести команду:
```sh
python boltun_tlgm.py
```
или
```sh
python boltun_vk.py
```
## Обучение Dialogflow новым событиям
Для добавления новых событий служит скрипт `add_intent.py`. Данные берутся из файла `questions.json`. Образец файла выложен в репозитории. 
При добавлении скрипт проверит, не добавляется ли событие повторно, в этом случае выдаст предупреждение и перейдет к обработке следующего события.
## Deploy на VPS под Linux
Необходимо на VPS выполнить все шаги описанные выше.  
Для того, чтобы запускать нашего бота при старте системы автоматически, воспользуемся системным менеджером `systemd`.
Пример будет показан для бота `boltun_tlgm.py` и названия сервиса `bot.service`. Для второго бота выполнить аналогичные действия, но с другими именами.  
Создадим файл `bot.service` в директории `/etc/systemd/system` :
```
$ sudo touch /etc/systemd/system/bot.service
```
Затем откроем его:
```
$ sudo nano /etc/systemd/system/bot.service
```
и вставим следующее содержимое и сохраняем файл:
```
[Unit]
Description=Telegram bot %name%
After=syslog.target
After=network.target

[Service]
Type=simple
#Пользователя user заменить на актуального
User=user
# замените на свой путь к каталогу, где находится `boltun_tlgm.py`
WorkingDirectory=/home/user/boltun_bot/
# замените на свои пути к виртуальному окружению и папке с ботом
ExecStart=/home/envs/tlgm_env/bin/python3 /home/user/boltun_bot/boltun_tlgm.py
RestartSec=10
Restart=always

[Install]
WantedBy=multi-user.target
```
в консоли выполним:
```
# перечитываем конфигурацию 
# (обнаружит файл `bot.service`)
$ sudo systemctl daemon-reload

# подключаем демон `bot.service`
$ sudo systemctl enable bot

# запускаем демон `bot.service`
$ sudo systemctl start bot

# смотрим статус демона `bot.service`
$ sudo systemctl status bot
```
Теперь перезапустить/остановить телеграмм-бота можно системными командами Linux:
```
# перезапуск
$ sudo systemctl restart bot

# остановка
$ sudo systemctl stop bot

# запуск после остановки
$ sudo systemctl start bot
```
Логи бота можно просмотреть командой:
```
$sudo journalctl -u bot.service
```
## Цель проекта
Код написан в образовательных целях на онлайн-курсе [dvmn.org](https://dvmn.org/).
