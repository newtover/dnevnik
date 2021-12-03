import argparse
import json
from pathlib import Path

from dnevnik2 import Dnevnik2


def main():
    available_methods = sorted(name for name in dir(Dnevnik2) if name.startswith('fetch'))

    arg_parser = argparse.ArgumentParser(description=(
        """Call fetch methods with corresponding arguments\n\n"""
        """The first argument is the cookies file, then the name of the method and then the args.\n"""
    ))
    arg_parser.add_argument('cookies_path')
    arg_parser.add_argument('method', choices=available_methods)
    arg_parser.add_argument('method_args', nargs='*')
    parsed = arg_parser.parse_args()

    cookies_path = Path(parsed.cookies_path).expanduser()
    dnevnik = Dnevnik2.make_from_cookies_file(cookies_path)
    method = getattr(dnevnik, parsed.method)
    result = method(*parsed.method_args)
    text = json.dumps(result, indent=2, ensure_ascii=False)
    print(text)


if __name__ == '__main__':
    main()
