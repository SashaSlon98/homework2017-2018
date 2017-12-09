import os
from os import listdir

from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)
app.debug = True
# Корректный вывод русских символов в JSON
app.config['JSON_AS_ASCII'] = False

SWADESH_LIST = ('я', 'ты', 'он, она, оно', 'мы', 'вы (мн. число)', 'они', 'этот, эта, это (близкий предмет)',
                'тот, та, то (удалённый предмет)', 'здесь, тут (близко)', 'там (далеко)',
                'кто (об одушевлённых субъектах)', 'что (о неодушевлённых субъектах)', 'где', 'когда', 'как',
                'не (отрицательная частица)', 'всё (на свете)', 'много (большое количество)',
                'несколько, немного (среднее количество)', 'мало (малое количество)', 'другой (человек), другие (люди)',
                'один', 'два', 'три', 'четыре', 'пять', 'большой (дом, предмет)', 'длинный (предмет)', 'широкий',
                'толстый (предмет)', 'тяжёлый', 'маленький', 'короткий', 'узкий', 'тонкий (предмет)', 'женщина',
                'мужчина', 'человек', 'ребёнок', 'жена', 'муж', 'мать', 'отец', 'зверь (дикое животное)', 'рыба',
                'птица', 'собака', 'вошь', 'змея', 'червь (дождевой червяк)', 'дерево', 'лес',
                'палка («ударил палкой»)', 'плод (фрукт)', 'семя (растения)', 'лист (дерева)', 'корень (растения)',
                'кора (дерева)', 'цветок', 'трава', 'верёвка', 'кожа', 'мясо', 'кровь', 'кость', 'жир (животный)',
                'яйцо', 'рог', 'хвост', 'перо (птицы)', 'волос(ы)', 'голова', 'ухо', 'глаз', 'нос', 'рот', 'зуб',
                'язык', 'ноготь', 'стопа, ступня', 'нога (от стопы до бедра)', 'колено', 'рука (кисть)', 'крыло',
                'живот (от пупка до промежности)', 'кишки (внутренности)', 'шея', 'спина', 'грудь (часть туловища)',
                'сердце', 'печень', 'пить (воду)', 'есть (кушать)', 'кусать (зубами)', 'сосать', 'плевать',
                'рвать, блевать', 'дуть (о ветре)', 'дышать', 'смеяться')
BASE_PATH = os.path.dirname(os.path.realpath(__file__))
DICTIONARIES_FOLDER = '{}\\{}'.format(BASE_PATH, 'dictionaries')
if not os.path.exists(DICTIONARIES_FOLDER):
    os.mkdir(DICTIONARIES_FOLDER)


@app.route('/')
def index():
    if request.args:
        file_name = '{}\\{}-{}.txt'.format(DICTIONARIES_FOLDER, request.args['language'], request.args['informant'])
        with open(file_name, 'w', encoding='utf-8') as f:
            for i in range(100):
                word = request.args['w' + str(i + 1)]
                if word:
                    comment = request.args['c' + str(i + 1)]
                    f.write('{} : {} : {}\n'.format(SWADESH_LIST[i], word, comment))
        return redirect(url_for('stats'))

    return render_template(
        'index.html',
        swadesh_list=SWADESH_LIST
    )


def read_dictionaries():
    swadesh_dictionaries = {}
    for dictionary_file in listdir(DICTIONARIES_FOLDER):
        language, informant = dictionary_file[:-4].split('-')

        if language in swadesh_dictionaries:
            informant_dictionaries = swadesh_dictionaries[language]
        else:
            informant_dictionaries = {}
            swadesh_dictionaries[language] = informant_dictionaries
        if informant in informant_dictionaries:
            swadesh_dictionary = informant_dictionaries[informant]
        else:
            swadesh_dictionary = {}
            informant_dictionaries[informant] = swadesh_dictionary

        with open('{}\\{}'.format(DICTIONARIES_FOLDER, dictionary_file), encoding='utf-8') as f:
            for line in f.read().split('\n'):
                if line:
                    ru_word, foreign_word, comment = line.split(' : ')
                    swadesh_dictionary[ru_word] = (foreign_word, comment)
    return swadesh_dictionaries


@app.route('/stats')
def stats():
    swadesh_dictionaries = read_dictionaries()
    return render_template(
        'stats.html',
        dictionaries=swadesh_dictionaries
    )


@app.route('/json')
def stats_json():
    swadesh_dictionaries = read_dictionaries()
    return jsonify(swadesh_dictionaries)


@app.route('/search')
def search():
    return render_template('search.html')


@app.route('/results')
def results():
    if request.args:
        language = request.args.get('language')
        informant = request.args.get('informant')
        with10words = request.args.get('with10words')

        swadesh_dictionaries = read_dictionaries()

        if language in swadesh_dictionaries:
            informants_dicts = swadesh_dictionaries[language]
            if informant:
                if informant in informants_dicts:
                    swadesh_dictionaries = {
                        language: {
                            informant: informants_dicts[informant]
                        }
                    }
                else:
                    swadesh_dictionaries = None
            else:
                swadesh_dictionaries = {
                    language: informants_dicts
                }
        else:
            swadesh_dictionaries = None

        if with10words == 'on':
            if swadesh_dictionaries:
                for informant in list(informants_dicts):
                    informant_swadesh_dict = informants_dicts[informant]
                    if len(informant_swadesh_dict) < 10:
                        del informants_dicts[informant]
                if not informants_dicts:
                    swadesh_dictionaries = None

        return render_template(
            'stats.html',
            dictionaries=swadesh_dictionaries
        )
    return redirect(url_for('search'))


if __name__ == '__main__':
    app.run()

