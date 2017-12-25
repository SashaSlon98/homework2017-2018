import json
import os
import re


def thai_pages_to_dict():
    dictionary = {}
    for file_name in os.listdir('thai_pages'):
        with open(os.path.join('thai_pages', file_name), encoding='utf-8') as file:
            file_html = file.read()
        file_html = re.sub("<a [^<]+>", '', file_html)
        file_html = re.sub("</a>", '', file_html)
        file_html = re.sub("<img [^<]+>", '', file_html)
        for matches in re.findall(
                "<tr>"
                "<td (rowspan=\d )?class=th>([^<]+)</td>"
                "<td( rowspan=\d)?>(\w+<span class='tt'>\w</span> ?)+</td>"
                "<td class=pos>[\w\s,]+</td>"
                "<td>([^<]+)</td>"
                "</tr>",
                file_html
        ):
            word, translation = matches[1].strip(), matches[-1].replace('&#34;', '"').replace('&#39;', '’')
            dictionary[word] = translation.split('; ')
    return dictionary


# 1 задание
thai_eng_dictionary = thai_pages_to_dict()

# 2 задание
thai_eng_dictionary_json = json.dumps(thai_eng_dictionary, indent=4, ensure_ascii=False)
with open('thai_eng_dictionary_json.json', 'w', encoding='utf-8') as f:
    f.write(thai_eng_dictionary_json)

eng_thai_dictionary = {}
for key, values in thai_eng_dictionary.items():
    for value in values:
        if value in eng_thai_dictionary:
            eng_thai_dictionary[value].append(key)
        else:
            eng_thai_dictionary[value] = [key]

eng_thai_dictionary_json = json.dumps(eng_thai_dictionary, indent=4, ensure_ascii=False)
with open('eng_thai_dictionary.json', 'w', encoding='utf-8') as f:
    f.write(eng_thai_dictionary_json)
