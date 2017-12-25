import json
import os

from flask import Flask, render_template, request, redirect, url_for

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
ENG_THAI_DICTIONARY = None

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/translate')
def translate():
    word = request.args.get('word')
    if word:
        return render_template('display.html', word=word, translation=ENG_THAI_DICTIONARY.get(word))
    return redirect(url_for('index'))


def load_dictionary():
    global ENG_THAI_DICTIONARY
    with open(os.path.join(BASE_PATH, 'eng_thai_dictionary.json'), encoding='utf-8') as f:
        ENG_THAI_DICTIONARY = json.load(f)


if __name__ == '__main__':
    load_dictionary()
    app.run()
