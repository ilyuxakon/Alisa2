from flask import Flask, request, jsonify
import logging
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

cities = {
    '��᪢�': ['1540737/daa6e420d33102bf6947', '213044/7df73ae4cc715175059e'],
    '���-���': ['1652229/728d5c86707054d4745f', '1030494/aca7ed7acefde2606bdc'],
    '��ਦ': ["1652229/f77136c2364eb90a3ea8", '123494/aca7ed7acefd12e606bdc']
}

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return jsonify(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = '�ਢ��! ������ ᢮� ���!'
        sessionStorage[user_id] = {
            'first_name': None,
            'game_started': False
        }
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = '�� ����蠫� ���. �����, ��������!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            sessionStorage[user_id]['guessed_cities'] = []
            res['response']['text'] = f'���⭮ �������������, {first_name.title()}. � ����. �⣠����� ��த �� ��?'
            res['response']['buttons'] = [
                {
                    'title': '��',
                    'hide': True
                },
                {
                    'title': '���',
                    'hide': True
                }
            ]
    else:
        if not sessionStorage[user_id]['game_started']:
            if '��' in req['request']['nlu']['tokens']:
                if len(sessionStorage[user_id]['guessed_cities']) == 3:
                    res['response']['text'] = '�� �⣠��� �� ��த�!'
                    res['end_session'] = True
                else:
                    sessionStorage[user_id]['game_started'] = True
                    sessionStorage[user_id]['attempt'] = 1
                    play_game(res, req)
            elif '���' in req['request']['nlu']['tokens']:
                res['response']['text'] = '�� � �����!'
                res['end_session'] = True
            else:
                res['response']['text'] = '�� ���﫠 �⢥�! ��� �� ��� ���?'
                res['response']['buttons'] = [
                    {
                        'title': '��',
                        'hide': True
                    },
                    {
                        'title': '���',
                        'hide': True
                    }
                ]
        else:
            play_game(res, req)


def play_game(res, req):
    user_id = req['session']['user_id']
    attempt = sessionStorage[user_id]['attempt']
    if attempt == 1:
        city = random.choice(list(cities))
        while city in sessionStorage[user_id]['guessed_cities']:
            city = random.choice(list(cities))
        sessionStorage[user_id]['city'] = city
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = '�� �� �� ��த?'
        res['response']['card']['image_id'] = cities[city][attempt - 1]
        res['response']['text'] = '����� ��ࠥ�!'
    else:
        city = sessionStorage[user_id]['city']
        if get_city(req) == city:
            res['response']['text'] = '�ࠢ��쭮! ��ࠥ� ���?'
            sessionStorage[user_id]['guessed_cities'].append(city)
            sessionStorage[user_id]['game_started'] = False
            return
        else:
            if attempt == 3:
                res['response']['text'] = f'�� ��⠫���. �� {city.title()}. ��ࠥ� ���?'
                sessionStorage[user_id]['game_started'] = False
                sessionStorage[user_id]['guessed_cities'].append(city)
                return
            else:
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card']['title'] = '���ࠢ��쭮. ��� ⥡� �������⥫쭮� ��'
                res['response']['card']['image_id'] = cities[city][attempt - 1]
                res['response']['text'] = '� ��� � �� 㣠���!'
    sessionStorage[user_id]['attempt'] += 1


def get_city(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return entity['value'].get('city', None)


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
       if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()