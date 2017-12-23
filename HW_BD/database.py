import json
import sqlite3


def transcript_notation(notation):
    transcript = []
    for n in notation.split('.'):
        _notation = n.split(' ', 1)[0]
        if _notation.isupper():
            _transcript = glossing_abbreviations.get(_notation)
            if _transcript:
                transcript.append(n.replace(_notation, _transcript))
        else:
            transcript.append(n)
    return transcript


with open('glossing_abbreviations.json', encoding='utf-8') as f:
    glossing_abbreviations = json.load(f)

# подключаемся к базе данных
conn = sqlite3.connect('hittite.db')

# создаем объект "курсор", которому будем передавать запросы
c = conn.cursor()

rows = []
for row in c.execute("SELECT * FROM wordforms"):
    rows.append(row)

# сохраняем изменения
conn.commit()

# отключаемся от БД
conn.close()

# Создаем новую БД
conn = sqlite3.connect('hittite_new.db')
c = conn.cursor()

c.execute('''
CREATE TABLE words(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lemma TEXT,
    wordform TEXT,
    glosses INTEGER
);''')

c.execute('''
CREATE TABLE glosses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notation TEXT,
    transcript TEXT
);''')

c.execute('''
CREATE TABLE words_glosses(
    word_id INTEGER,
    gloss_id INTEGER
);''')

gloss_index = 1
word_id = 1
for row in rows:
    lemma, word_form, glosses_notation = row
    if '[…]' in word_form or '[…]' in glosses_notation:
        continue
    glosses_transcript = ', '.join(transcript_notation(glosses_notation))
    if not glosses_transcript:
        continue
    c.execute('INSERT INTO words VALUES (?, ?, ?, ?)', (word_id, lemma, word_form, glosses_notation))
    word_id += 1
    c.execute('SELECT * FROM glosses WHERE notation = ?', (glosses_notation,))
    gloss = c.fetchone()
    if gloss:
        gloss_id = gloss[0]
    else:
        c.execute('INSERT INTO glosses VALUES (?, ?, ?)', (gloss_index, glosses_notation, glosses_transcript))
        gloss_id = gloss_index
        gloss_index += 1
    c.execute('INSERT INTO words_glosses VALUES (?, ?)', (word_id, gloss_id))

conn.commit()
conn.close()
