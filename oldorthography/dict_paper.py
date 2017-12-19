import json
import re
from itertools import islice

from lxml import html
from requests import Session

dictionary = {}
with Session() as session:
    for page in range(int('c0', 16), int('df', 16) + 1):
        print(f'Скаринование слов на букву {chr(ord("а") + page - int("c0", 16))}...')
        dict_html = session.get('http://www.dorev.ru/ru-index.html', params={'l': f'{page:x}'}).text
        tree = html.fromstring(dict_html)
        table = tree.cssselect('table')[4]
        rows = table.cssselect('tr')
        for tr in islice(table.cssselect('tr'), 6, len(rows) - 2):
            _, word, _, translated_word, _ = tr.getchildren()
            word = word.text
            translated_word = re.split('[,(—]| и ', translated_word.text_content().replace("'", ''), 1)[0].rstrip()
            dictionary[word] = translated_word

with open('dictionary.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(dictionary, indent=4, ensure_ascii=False))
