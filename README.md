# dnevnik
A python CLI tool to fetch school marks from https://dnevnik2.petersburgedu.ru/


# Что это такое?

Скрипт, который ходит по http на https://dnevnik2.petersburgedu.ru/api/journal/estimate/table и достаёт оттуда оценки за период
и форматирует результат в текстовый файл на текущий день. Потом файлы удобно сравнивать при помощи diff -u.

Чтобы ходить по http на этот url, нужен параметр education_id для ученика, и даты начала и конца периода (настраивается в app_config.toml) и всякие куки с авторизацией.

Если у вас стоит авторизация по почте и паролю (а не через Госуслуги), то файл с кукой можно создать с помощью следующего скрипта:

```
$ python -m dnevnik2.scripts.login_with_email_and_save_cookies cookies.json
Email for https://dnevnik2.petersburgedu.ru/: newtover@example.com
Password:
Saved cookies into cookies.json
```
Эта команда сходит с логином и паролем на сайт и сохранит в `cookies.json` куку с авторизацией. Если не хочется вводить 
пароль в чужие скрипты (или в случае авторизации через Госуслуги), куку можно скопировать из браузера и подставить 
в файл такого содержимого (вместо COOKIE_VALUE_HERE).

```
[
  {
    "name": "X-JWT-Token",
    "value": "COOKIE_VALUE_HERE",
    "domain": "dnevnik2.petersburgedu.ru",
    "path": "/",
    "expires": null
  }
]
```

Далее можно вызывать основной скрипт с этим файлом с кукой:

```
python -m dnevnik2.scripts.render_marks_for_current_quarter cookies.json
```

Скрипт создаёт в текущей директории (конфигурируется через `--output_dir`) файл с оценками за текущую четверть.
В конце файла рисуется статистика по предметам. Файлы за разные дни удобно сравнивать между собой через `diff -u`.
Не знаю, как у вас, а у нас учителя любят ставить оценки задним числом, поэтому лучше доставать все оценки за четверть.

Кроме того, есть скрипт, который позволяет делать некоторые запросы к их api. Запросы делаются 
через медоды 'fetch_...' объекта Dnevnik2 (см. `dnevnik2/__init__.py`).

Например, так можно сделать запрос к оценкам для произвольного периода. Нужно знать education_id (который можно 
получить через `fetch_children_list`). В примере формат даты, который ждёт api. Результатом будет соответствующий json.

```
$ python -m dnevnik2.scripts.fetch_response cookies.json fetch_marks_for_period 427455 01.09.2021 01.10.2021
```

Выглядит сыровато, но работает. Единственная зависимость - pip.
