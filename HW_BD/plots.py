#второе задание
import sqlite3
from typing import Counter

import matplotlib.pyplot as plt
from matplotlib import style

PARTS_OF_SPEECH = {
    'noun',
    'pronoun',
    'adjective',
    'verb',
    'adverb',
    'preposition',
    'conjunction',
    'interjection'
}
CASES = {
    'nominative',
    'genitive',
    'dative',
    'accusative',
    'instrumental'
}

conn = sqlite3.connect('hittite_new.db')
c = conn.cursor()

counter = Counter()
words_glosses = c.execute("SELECT * FROM words_glosses").fetchall()
for word_id, gloss_id in words_glosses:
    gloss_parts = c.execute(
        "SELECT transcript FROM glosses WHERE id = ?", (gloss_id,)
    ).fetchone()[0].split(', ')
    counter.update(gloss_parts)

conn.commit()
conn.close()

# Стиль графиков
style.use('ggplot')

# ++++++++++++++++++ Части речи ++++++++++++++++++
data = [(part, counter[part]) for part in PARTS_OF_SPEECH]
data.sort(key=lambda x: x[1])
# Рисуем график
# Размер графика в дюймах
plt.figure(figsize=(10, 6))

# Отключаем подписи осии X
ax1 = plt.axes()
plt.setp(ax1.get_xticklabels(), visible=False)

for x, (part, frequency) in enumerate(data):
    y = frequency
    plt.scatter(part, y, s=100)
    # Текст чуть выше точки
    plt.text(x + 0.1, y + 2, part)
plt.title('Число частей речи в глоссах')
plt.ylabel('Частота части речи')
plt.xlabel('Части речи')
plt.show()

# Рисуем столбчатую диаграмму
plt.figure(figsize=(10, 6))
for x, (part, frequency) in enumerate(data):
    y = frequency
    plt.bar(part, y)
plt.title('Число частей речи в глоссах')
plt.ylabel('Частота части речи')
plt.xlabel('Части речи')
plt.show()

# ++++++++++++++++++++ Падежи ++++++++++++++++++++
data = [(part, counter[part]) for part in CASES]
data.sort(key=lambda x: x[1])

for x, (part, frequency) in enumerate(data):
    y = frequency
    plt.scatter(part, y, s=100)
plt.title('Падежи в глоссах')
plt.ylabel('Частота падежа')
plt.xlabel('Падежи')
plt.show()
