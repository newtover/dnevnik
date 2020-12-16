#!/usr/bin/env python3
from collections import defaultdict
import datetime as dt
import json
from pathlib import Path
import pickle
import pip._vendor.requests as requests
import pip._vendor.toml as toml
import sys


SUBJECTS = {
    113703: "Английский язык",
    113704: "Немецкий язык",
}


def get_subject(item):
    return SUBJECTS.get(item['subject_id'], item['subject_name'])


def to_date(text):
    return dt.datetime.strptime(text, '%d.%m.%Y').date()


def main():
    config_path = 'app_config.toml'
    session_path = 'dnevnik.session.pkl'
    base_dir = Path(sys.argv[0]).parent.absolute()

    with (base_dir / config_path).open('r', encoding='utf-8') as f1:
        config = toml.load(f1)

    url = config['urls']['marks_for_period']['url']
    params = config['urls']['marks_for_period']['params']

    with (base_dir / session_path).open('rb') as f1:
        session = pickle.load(f1)

    with session.get(url, params=params) as res:
        res.raise_for_status()
        text = res.text
        data = res.json()

    with (base_dir / 'last_res.txt').open('w', encoding='utf-8') as f1:
        print(json.dumps(data, ensure_ascii=False, indent=2), file=f1)

    out_lines = []
    grouped = defaultdict(list)
    for item in sorted(data['data']['items'], key=lambda x: (to_date(x['date']), x['estimate_value_name'])):
        s_name = item['subject_name'] = get_subject(item)
        mark = item['estimate_value_name']
        if mark.isdigit():
            grouped[s_name].append(int(mark))
        comment = ('# ' + item['estimate_comment']) if item['estimate_comment'] else ''
        out_lines.append((
            to_date(item['date']),
            "{subject_name:25s} {estimate_value_code:5s} {estimate_value_name:9s} {estimate_type_name:20s}".format(**item),
            comment
        ))

    if not out_lines:
        exit(1)

    with (base_dir / f'marks.{dt.date.today()}.txt').open('w', encoding='utf-8') as f1:
        for date, mark, comment in sorted(out_lines):
            print(f'{date}  {mark} {comment}', file=f1)

        f1.write('\n\n')
        for s_name in sorted(grouped):
            avg = sum(grouped[s_name]) / len(grouped[s_name])
            s_marks = ' '.join(str(mark) for mark in grouped[s_name])
            print(f'{s_name:25s} : {avg:0.3f}    {s_marks}', file=f1)

    with (base_dir / session_path).open('wb') as f1:
        pickle.dump(session, f1)


if __name__ == '__main__':
    main()
