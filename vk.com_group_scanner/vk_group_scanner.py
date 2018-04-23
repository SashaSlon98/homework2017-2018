import os
from collections import defaultdict
from datetime import date
from datetime import datetime
import matplotlib.pyplot as plt
import requests
import re

VK_API_URL = 'https://api.vk.com/method'
VK_API_VERSION = 5.74
SERVICE_KEY = os.getenv('VK_SERVICE_KEY')
SCANNED_GROUP = 'aleksey_vilnjusov_otzyvy'
POSTS_AMOUNT = 150


def api_request(method, **params):
    return requests.get(
        f'{VK_API_URL}/{method}',
        params={
            **params,
            'v': VK_API_VERSION,
            'access_token': SERVICE_KEY,
        }
    ).json()


def get_wall(group_id, n_posts):
    posts = []
    for offset in range(0, n_posts, 100):
        posts_left = n_posts - offset
        response = api_request(
            'wall.get',
            owner_id=group_id,
            offset=offset,
            count=100 if posts_left >= 100 else posts_left
        )['response']
        posts.extend(response['items'])
    return posts


def get_comments(group_id, post_id):
    response = api_request(
        'wall.getComments',
        owner_id=group_id,
        post_id=post_id,
        offset=0,
        count=100,
        preview_length=0,
        extended=1,
        fields='profiles',
    )['response']
    comments = response['items']
    count = response['count']
    for i in range(100, count, 100):
        response = api_request(
            'wall.getComments',
            owner_id=group_id,
            post_id=post_id,
            offset=0,
            count=100,
            preview_length=0,
            extended=1,
            fields='profiles',
        )['response']
        comments.extend(response['items'])
    print(f'[Пост {post_id}] Считано комментариев: {count}')
    return comments


def get_user_ids(posts):
    user_ids = set()
    for post in posts:
        post_owner_id = post['from_id']
        # Пропускаем пост от имены группы
        if post_owner_id >= 0:
            user_ids.add(post_owner_id)
        else:
            # id автора поста
            signer_id = post.get('signer_id')
            if signer_id is not None:
                user_ids.add(signer_id)
        for comment in post['comments']:
            comment_owner_id = comment['from_id']
            # Пропускаем комментарий от имени группы
            if comment_owner_id < 0:
                continue
            user_ids.add(comment_owner_id)
    return user_ids


def mean(x):
    return sum(x) / max(len(x), 1)


def words_len(text):
    # Удаляем пунктуационные знаки
    cleared_text = re.sub(r'[^\w\s]', '', text)
    return len(re.split('\s+', cleared_text))


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_users(user_ids):
    _user_ids = list(user_ids)
    users_info = []
    for chunk in chunks(_user_ids, 200):
        users_info.extend(api_request(
            'users.get',
            user_ids=','.join(str(user_id) for user_id in chunk),
            fields='city, bdate'
        )['response'])
    return users_info


def parse_bdate(bdate):
    if bdate and bdate.count('.') == 2:
        d, m, y = map(int, bdate.split('.'))
        return datetime.strptime(f'{d:02d}.{m:02d}.{y}', '%d.%m.%Y').date()


def count_age(bdate):
    today = date.today()
    return today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))


def get_users_info(users):
    _users = {}
    for user in users:
        city = user.get('city')
        city_id = city['id'] if city else None
        city_title = city['title'] if city else None
        bdate = parse_bdate(user.get('bdate'))
        age = count_age(bdate) if bdate else None
        _users[user['id']] = city_title, age
    return _users


def avg_posts_len_for_age(posts, users_info):
    """Средняя длина поста по возрасту"""
    age_posts = defaultdict(list)
    for post in posts:
        # Ищем пост с подписью
        signer_id = post.get('signer_id')
        if signer_id is not None:
            user = users_info.get(signer_id)
            if user:
                user_age = user[1]
                if user_age:
                    post_len = words_len(post['text'])
                    age_posts[user_age].append(post_len)

    for k, v in age_posts.items():
        age_posts[k] = mean(v)

    return age_posts


def avg_comments_len_for_age(posts, users_info):
    """Средняя длина комментария по возрасту"""
    age_comments = defaultdict(list)
    for post in posts:
        for comment in post['comments']:
            comment_owner_id = comment['from_id']
            # Пропускаем комментарий от имени группы
            if comment_owner_id < 0:
                continue
            user = users_info.get(comment_owner_id)
            if user:
                user_age = user[1]
                if user_age:
                    post_len = words_len(comment['text'])
                    age_comments[user_age].append(post_len)

    for k, v in age_comments.items():
        age_comments[k] = mean(v)

    return age_comments


def avg_posts_len_for_city(posts, users_info):
    """Средняя длина поста по городам"""
    city_posts = defaultdict(list)
    for post in posts:
        # Ищем пост с подписью
        signer_id = post.get('signer_id')
        if signer_id is not None:
            user = users_info.get(signer_id)
            if user:
                user_city = user[0]
                if user_city:
                    post_len = words_len(post['text'])
                    city_posts[user_city].append(post_len)

    for k, v in city_posts.items():
        city_posts[k] = mean(v)

    return city_posts


def avg_comments_len_for_city(posts, users_info):
    """Средняя длина комментария по городам"""
    city_comments = defaultdict(list)
    for post in posts:
        for comment in post['comments']:
            comment_owner_id = comment['from_id']
            # Пропускаем комментарий от имени группы
            if comment_owner_id < 0:
                continue
            user = users_info.get(comment_owner_id)
            if user:
                user_city = user[0]
                if user_city:
                    post_len = words_len(comment['text'])
                    city_comments[user_city].append(post_len)

    for k, v in city_comments.items():
        city_comments[k] = mean(v)

    return city_comments


# %% Получение постов с комментариями
response = api_request('groups.getById', group_id=SCANNED_GROUP)
group_id = -int(response['response'][0]['id'])
posts = get_wall(group_id, POSTS_AMOUNT)

for post in posts:
    post_id = post['id']
    post['comments'] = get_comments(group_id, post_id)

posts_comments = defaultdict(list)
for post in posts:
    post_text_len = words_len(post['text'])
    comments_text_len = [words_len(comment['text']) for comment in post['comments']]
    posts_comments[post_text_len].extend(comments_text_len)

for k, v in posts_comments.items():
    posts_comments[k] = mean(v)

# %% Построение графика зависимости средней длины комментария от длины поста
posts_comments = sorted(((k, v) for k, v in posts_comments.items()), key=lambda x: x[0])

post_text_lens = [pc[0] for pc in posts_comments]
avg_comments_text_lens = [pc[1] for pc in posts_comments]

fig, ax = plt.subplots(figsize=(20, 10))
ax.plot(post_text_lens, avg_comments_text_lens)

ax.set(xlabel='Длина поста', ylabel='Средняя длина комментария',
       title='Зависимость средней длины комментария от длины поста')
fig.autofmt_xdate()
ax.grid()
fig.savefig('Средняя длина комментария от длины поста.png')
plt.show()

# %% Получение информации о пользователях
user_ids = get_user_ids(posts)
users = get_users(user_ids)
users_info = get_users_info(users)

# %% Построение графика зависимости средней длины поста от возраста
age_posts = avg_posts_len_for_age(posts, users_info)
sorted_age_posts = sorted(((k, v) for k, v in age_posts.items() if k < 100), key=lambda x: x[0])

ages = [ap[0] for ap in sorted_age_posts]
avg_comments_len = [ap[1] for ap in sorted_age_posts]

fig, ax = plt.subplots(figsize=(20, 10))
ax.set(xlabel='Возраст', ylabel='Средняя длина поста',
       title='Зависимость средней длины поста от возраста')
ax.plot(ages, avg_comments_len)
ax.set_xticks(ages)
fig.savefig('Средняя длина поста от возвраста.png')
plt.show()

# %% Построение графика зависимости средней длины комментария от возраста
age_comments = avg_comments_len_for_age(posts, users_info)
sorted_age_comments = sorted(((k, v) for k, v in age_comments.items() if k < 100), key=lambda x: x[0])

ages = [ac[0] for ac in sorted_age_comments]
avg_comments_len = [ac[1] for ac in sorted_age_comments]

fig, ax = plt.subplots(figsize=(20, 10))
ax.set(xlabel='Возраст', ylabel='Средняя длина комментария',
       title='Зависимость средней длины комментария от возраста')
ax.plot(ages, avg_comments_len)
ax.set_xticks(ages)
fig.savefig('Средняя длина комментария от возвраста.png')
plt.show()

# %% Построение графика зависимости средней длины поста от города
city_posts = avg_posts_len_for_city(posts, users_info)
sorted_city_posts = sorted(((k, v) for k, v in city_posts.items()), key=lambda x: x[1])

cities = [sp[0] for sp in sorted_city_posts]
avg_comments_len = [sp[1] for sp in sorted_city_posts]

fig, ax = plt.subplots(figsize=(40, 10))
ax.set(xlabel='Город', ylabel='Средняя длина поста',
       title='Зависимость средней длины поста от города')
ax.plot(cities, avg_comments_len)
fig.autofmt_xdate()
fig.savefig('Средняя длина поста от города.png')
plt.show()

# %% Построение графика зависимости средней длины комментария от города
city_comments = avg_comments_len_for_city(posts, users_info)
sorted_city_comments = sorted(((k, v) for k, v in city_comments.items()), key=lambda x: x[1])

cities = [cc[0] for cc in sorted_city_comments]
avg_comments_len = [cc[1] for cc in sorted_city_comments]

fig, ax = plt.subplots(figsize=(120, 10))
ax.set(xlabel='Город', ylabel='Средняя длина комментария',
       title='Зависимость средней длины комментария от города')
ax.plot(cities, avg_comments_len)
fig.autofmt_xdate()
fig.savefig('Средняя длина комментария от города.png')
plt.show()

