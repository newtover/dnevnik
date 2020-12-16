# dnevnik
A python CLI tool to fetch school marks from https://dnevnik2.petersburgedu.ru/


# Что это такое?

Скрипт dnevnik.py, который ходит по http на https://dnevnik2.petersburgedu.ru/api/journal/estimate/table и достаёт оттуда оценки за период
и форматирует результат в текстовый файл на текущий день. Потом файлы удобно сравнивать при помощи diff -u.

Чтобы ходить по http на этот url, нужен параметр education_id для ученика, и даты начала и конца периода (настраивается в app_config.toml) и всякие куки с авторизацией.

Я открыл в браузере панель Web Developer / Network, перезагрузил страницу со сводкой оценок, сохранил результат сетевой активности в har-файл, там поискал `dnevnik2.petersburgedu.ru/api/journal/estimate/table`,
скопировал массив заголовков запроса в файл `headers.json` и запустил скрипт `session_from_headers.py`. Скрипт сгенерировал файлик `dnevnik.session.pkl`, который и используется основным скриптом `dnevnik.py`.

Правильное значение параметра education_id тоже можно посмотреть в har-файле.

Пример файла `headers.json` прриложен, но там пустой заголовок Cookie.

Выглядит сыровато, но работает. Единственная зависимость - pip.
