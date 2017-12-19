import json
import re

import os
from pymystem3 import Mystem

BASE_PATH = os.path.dirname(os.path.realpath(__file__))


def translate_word(word, analysis):
    if not analysis:
        return word
    gr = analysis['gr']
    part, description = gr.split('=', 1)
    if part.startswith('S,'):
        part, _ = part.split(',', 1)

    _word = re.sub('и([аоиеёэыуюяй])', 'і\g<1>', word)

    if _word[-1] in {'б', 'в', 'г', 'д', 'ж', 'з', 'к', 'л', 'м', 'н',
                     'п', 'р', 'с', 'т', 'ф', 'х', 'ц', 'ч', 'ш', 'щ'}:
        _word += 'ъ'
    else:
        # прилагательное, существительное, числительное или числительное-прилагательное
        if any(part == p for p in ('A', 'S', 'NUM', 'ANUM')):
            if 'дат' in gr or 'пр' in gr and 'ед' in gr:
                if word.endswith('е'):
                    _word = _word[:-1] + 'ѣ'
        if any(part == p for p in ('A', 'S')):
            if 'жен' in gr or 'ср' in gr:
                if _word.endswith(('іе', 'ые')):
                    _word = _word[:-1] + 'я'
                elif _word.endswith('іеся'):
                    _word = _word.replace('іеся', 'іяся')

    if _word.startswith(('бес', 'черес', 'чрес')):
        _word = _word.replace('ес', 'ез', 1)

    return _word


def translate(text):
    with open(os.path.join(BASE_PATH, 'dictionary.json'), encoding='utf-8') as f:
        dictionary = json.load(f)
    mystem = Mystem()
    translated_text = ''
    for item in mystem.analyze(text):
        _text = item['text']
        analysis = item.get('analysis')
        analysis = analysis[0] if analysis else None
        lex = analysis['lex'] if analysis else _text
        if _text.isalpha():
            translation = dictionary.get(lex)
            # TODO
            if _text == lex:
                if translation and any(c in translation for c in ('ѣ', 'ѳ', 'ѵ')):
                    translated_text += translation
                else:
                    translated_text += translate_word(_text, analysis)
            else:
                if translation and any(c in translation for c in ('ѣ', 'ѳ', 'ѵ')):
                    translated_text += translation
                else:
                    translated_text += translate_word(_text, analysis)
        else:
            translated_text += _text
    return translated_text
