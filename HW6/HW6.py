from pymorphy2 import MorphAnalyzer
import sqlite3
import re
import random

morph = MorphAnalyzer()

signs = re.compile('[,.?()!:;"«–»…]')


def lex_base():
    d ={}
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.executescript("""DROP TABLE IF EXISTS words;

                 CREATE TABLE words
                 (lex TEXT, 
                 POS TEXT,
                 gender TEXT,
                 trans TEXT,
                 aspect TEXT);
                       """)
    with open('harrypotter.txt', 'r') as file:
        text = file.read()
    text = re.sub(signs, '', text)
    words = text.split()[1:]
    print('Creating database...')
    for word in words:
        word = morph.parse(word)[0]
        lex = word.normal_form
        if lex not in d:
            d[lex] = [word.tag.POS, word.tag.gender, word.tag.transitivity, word.tag.aspect]
    for el in d:
        c.execute('''INSERT INTO words (lex, POS, gender, trans, aspect)
                    VALUES (?, ?, ?, ?, ?)''', [el, d[el][0], d[el][1], d[el][2], d[el][3]])
    conn.commit()
    conn.close()


def parsing(phrase):
    phrase_data = []
    phrase_punct = {}
    punct_arr = re.findall(signs, phrase)
    splitted_phrase = phrase.split()
    for i, word in enumerate(splitted_phrase):
        if word[-1] in punct_arr:
            phrase_punct[i] = word[-1]
        if word[0] in punct_arr:
            phrase_punct[i+0.1] = ['first', word[-1]]
    splitted_phrase = [re.sub(signs, '', word) for word in splitted_phrase]
    stop_list = ['я', 'мы', 'ты', 'вы', 'Я', 'Мы', 'Ты', 'Вы']
    for word in splitted_phrase:
        if word in stop_list:
            phrase_data.append(word)
        else:
            parsed = morph.parse(word)[0]
            gram = [str(parsed.tag.tense), str(parsed.tag.mood), str(parsed.tag.number),
                str(parsed.tag.person), str(parsed.tag.voice), str(parsed.tag.case)]
            while 'None' in gram:
                gram.remove('None')
            gram = set(gram)
            phrase_data.append([str(parsed.tag.POS), str(parsed.tag.gender),
                            str(parsed.tag.transitivity), str(parsed.tag.aspect), gram])
    return phrase_data, phrase_punct


def prep_conj(response):
    d = {
        'gent': ['от', 'без', 'у', 'из', 'до', 'возле', 'для', 'вокруг'],
        'datv': ['по', 'к'],
        'accs': ['на', 'за', 'про', 'через'],
        'ablt': ['за', 'под', 'над', 'перед', 'с'],
        'loct': ['на', 'о', 'в', 'об', 'при', 'обо'],
        'loc2': ['в']
    }
    while 'PREP' in response:
        i = response.index('PREP')
        head = morph.parse(response[i+1])[0].tag.case
        if head == 'nomn':
            head = 'accs'
        n = random.randint(0, len(d[head]) - 1)
        prep = d[head][n]
        response[i] = prep
    return response


def base_search(data):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    response = []
    for el in data:
        if len(el) == 1:
            response.append(el)
        elif el[0] == 'PREP':
            response.append('PREP')
        else:
            if el[0] == 'NOUN':
                c.execute('''SELECT lex
                            FROM words
                            WHERE POS = ?
                            AND gender = ?
                            ''', [el[0], el[1]])
            elif el[0] == 'VERB':
                c.execute('''SELECT lex
                            FROM words
                            WHERE POS = ?
                            AND trans = ?
                            AND aspect = ?
                            ''', [el[0], el[2], el[3]])
            elif el[0] == 'NPRO':
                el[-1].discard('1per')
                el[-1].discard('2per')
                el[-1].discard('3per')
                c.execute('''SELECT lex
                            FROM words
                            WHERE POS = ?
                            ''', [el[0]])
            else:
                c.execute('''SELECT lex
                        FROM words
                        WHERE POS = ?
                        ''', [el[0]])
            result = c.fetchall()
            i = random.randint(0, len(result) - 1)
            try:
                part = result[i][0]
                parameters = morph.parse(part)[0]
                new_word = parameters.inflect(el[-1])[0]
                response.append(new_word)
            except IndexError:
                print('Что-то пошло не так!')
                print('Кажется, pymorphy не знает какое-то из ваших слов.')
                print('Попробуйте заменить слова на грамматически похожие.')
                response = []
                break
            except TypeError:
                print('Это накосячил рандом. Попробуйте вбить эту фразу еще раз!')
                break
    conn.close()
    return response


def compiling(phrase):
    data, punct = parsing(phrase)
    response = base_search(data)
    prep_conj(response)
    response[0] = response[0].capitalize()
    for i in punct:
        if len(punct[i]) > 1:
            response[int(i)] = punct[i][1] + response[int(i)]
        else:
            response[i] = response[i] + punct[i]
    response = ' '.join(response)
    print('Получилось:\n', response)


if __name__ == '__main__':
    print('Привет! Это программа основана на модуле pymorphy2, ' +
          'и он не всегда правильно парсит грамматичесие характеристики слов.' +
          '\nПоэтому иногда выход может получаться странным, но я ничего не могу с этим поделать.' +
          '\nПросто старайтесь не мучить его слишком сложным синтаксисом (а пунктуацей - можно!)')
    print('\nДавайте поиграем!\n')
    compiling(input('\nВведите какую-нибудь фразу: '))
