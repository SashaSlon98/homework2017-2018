import json
import random
import re
from collections import Counter, OrderedDict
from urllib import request as req

import os
from flask import Flask, render_template, request, redirect, url_for

from translator import translate as translate_text

BASE_PATH = os.path.dirname(os.path.realpath(__file__))

# Погода в Скопье
WEATHER_URL = 'https://yandex.ru/pogoda/10463'
LENTA_URL = 'https://lenta.ru/'

E_DICTIONARY = None

app = Flask(__name__)
app.debug = True


def get_weather():
    with req.urlopen(WEATHER_URL) as response:
        html = response.read().decode('utf-8')
    degrees = re.search('<div class="temp fact__temp"><span class="temp__value">([+−]\d+)</span>', html).group(1)
    weather_condition = re.search(
        '<div class="fact__condition day-anchor i-bem" data-bem=\'{"day-anchor":{"anchor":\d+}}\'>([\w\s]+)</div>',
        html
    ).group(1)
    return degrees, weather_condition


@app.route('/')
def index():
    degrees, weather_condition = get_weather()
    return render_template('index.html', degrees=degrees, weather_condition=weather_condition)


@app.route('/translate')
def translate():
    text = request.args.get('text')
    if text:
        return render_template('display.html', original_text=text, text=translate_text(text))

    return redirect(url_for('index'))


@app.route('/old-lenta.ru')
def old_lenta():
    with req.urlopen(LENTA_URL) as response:
        html = response.read().decode('utf-8')

    counter = Counter()
    source_text = ''
    first = True
    for word in re.finditer('[а-яА-Я]+', html):
        _word = word.group()
        if first:
            source_text += _word
            first = False
        else:
            source_text += ', ' + _word
        counter[_word.lower()] += 1

    most_common = counter.most_common(10)
    most_common_words = ', '.join(f'{translate_text(word)} ({count})' for word, count in most_common)

    translated_text = translate_text(source_text)

    return render_template('old-lenta.html', most_common_words=most_common_words, translated_text=translated_text)


@app.route('/test')
def test():
    questions = []
    for index, words in enumerate(E_DICTIONARY):
        first_index = random.randint(0, 1)
        questions.append((index, words[first_index], words[0 if first_index else 1]))

    random.shuffle(questions)
    return render_template('test.html', questions=questions[:10])


@app.route('/test-results')
def test_results():
    if not request.args:
        return redirect(url_for('test'))

    question_items_amount = len(request.args)
    correct_answers_counter = 0
    for q, value in request.args.items():
        index = int(q[1:])
        if E_DICTIONARY[index][0] == value:
            correct_answers_counter += 1
    return render_template(
        'test-results.html',
        questions_amount=question_items_amount,
        corret_answers=correct_answers_counter
    )


def load_dictionary():
    global E_DICTIONARY
    with open(os.path.join(BASE_PATH, 'e-dictionary.json'), encoding='utf-8') as f:
        dictionary = json.load(f, object_pairs_hook=OrderedDict)
    E_DICTIONARY = [(k, v) for k, v in dictionary.items()]


if __name__ == '__main__':
    load_dictionary()
    app.run()
