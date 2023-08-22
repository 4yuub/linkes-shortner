import json
import re
from random import choices
from string import ascii_letters, digits

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

app_data = json.load(open('data.json'))
LINK_REGEX = re.compile(
    r"^(https?://)([a-zA-Z0-9_-]+\.)+[a-zA-Z]{2,6}(/.*)?$")


def get_random_unique_key():
    key = ''.join(choices(ascii_letters + digits, k=6))
    while key in app_data:
        key = ''.join(choices(ascii_letters + digits, k=6))
    return key


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<key>/password', methods=['POST'])
def check_password(key):
    body = request.get_json()
    data = app_data.get(key)

    if data is None:
        return {'message': 'Invalid URL.'}, 400

    if body.get('password') != data.get('password'):
        return {'message': 'Invalid Password.'}, 400

    print(data['originalUrl'])
    return {'originalUrl': data['originalUrl']}


@app.route('/<key>')
def redirect_to_original_url(key):
    data = app_data.get(key)
    if data is None:
        return redirect(url_for('index'))

    if data['isProtected']:
        return render_template('password.html', key=key)
    return redirect(data['originalUrl'])


@app.route('/create', methods=['POST'])
def create():
    global app_data
    data = request.get_json()

    is_protected = data['isProtected']
    original_url = data['originalLink']
    password = data['password']

    if original_url is None or original_url == '':
        return {'message': 'Please enter a valid URL.'}, 400

    if is_protected and (password is None or password == ''):
        return {'message': 'Please enter a valid password.'}, 400

    if not LINK_REGEX.match(original_url):
        return {'message': 'Please enter a valid URL.'}, 400

    key = get_random_unique_key()
    app_data[key] = {
        'originalUrl': original_url,
        'isProtected': is_protected,
        'password': password
    }

    json.dump(app_data, open('data.json', 'w'))

    return {'shortLink': f'{request.host_url}{key}'}


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)
