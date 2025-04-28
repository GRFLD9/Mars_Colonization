import base64

import requests
from flask import Blueprint, make_response, jsonify, request, render_template
from datetime import datetime
from . import db_session
from .users import User

blueprint = Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify({
        'users': [
            item.to_dict(only=(
                'id', 'surname', 'name', 'age',
                'position', 'speciality', 'address',
                'email', 'modified_date'
            ))
            for item in users
        ]
    })


@blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify({
        'user': user.to_dict(only=(
            'id', 'surname', 'name', 'age',
            'position', 'speciality', 'address',
            'email', 'modified_date'
        ))
    })


@blueprint.route('/api/users', methods=['POST'])
def create_user():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)

    required_fields = [
        'surname', 'name', 'age',
        'position', 'speciality', 'address',
        'email'
    ]

    if not all(key in request.json for key in required_fields):
        return make_response(jsonify({
            'error': 'Bad request',
            'required_fields': required_fields
        }), 400)

    try:
        db_sess = db_session.create_session()

        user = User(
            surname=request.json['surname'],
            name=request.json['name'],
            age=request.json['age'],
            position=request.json['position'],
            speciality=request.json['speciality'],
            address=request.json['address'],
            email=request.json['email'],
            modified_date=datetime.now()
        )

        db_sess.add(user)
        db_sess.commit()

        return jsonify({
            'success': True,
            'id': user.id,
            'user': user.to_dict(only=(
                'id', 'surname', 'name', 'age',
                'position', 'speciality', 'address',
                'email', 'modified_date'
            ))
        }), 201

    except Exception as e:
        db_sess.rollback()
        return make_response(jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500)


@blueprint.route('/api/users/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)

    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)

    if not user:
        return make_response(jsonify({'error': 'User not found'}), 404)

    try:
        if 'surname' in request.json:
            user.surname = request.json['surname']
        if 'name' in request.json:
            user.name = request.json['name']
        if 'age' in request.json:
            user.age = request.json['age']
        if 'position' in request.json:
            user.position = request.json['position']
        if 'speciality' in request.json:
            user.speciality = request.json['speciality']
        if 'address' in request.json:
            user.address = request.json['address']
        if 'email' in request.json:
            user.email = request.json['email']

        user.modified_date = datetime.now()

        db_sess.commit()

        return jsonify({
            'success': True,
            'user': user.to_dict(only=(
                'id', 'surname', 'name', 'age',
                'position', 'speciality', 'address',
                'email', 'modified_date'
            ))
        })

    except Exception as e:
        db_sess.rollback()
        return make_response(jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500)


@blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:user_id>/city')
def get_user_city_data(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)

    if not user:
        return make_response(jsonify({'error': 'User not found'}), 404)

    if not user.city_from:
        return make_response(jsonify({'error': 'City not specified'}), 400)

    try:
        geocoder_response = requests.get(
            "http://geocode-maps.yandex.ru/1.x/",
            params={
                "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
                "geocode": user.city_from,
                "format": "json"
            }
        )

        geo_data = geocoder_response.json()
        features = geo_data["response"]["GeoObjectCollection"]["featureMember"]
        if not features:
            return make_response(jsonify({
                'error': 'City not found',
                'message': f'Город "{user.city_from}" не найден на карте'
            }), 400)

        toponym = features[0]["GeoObject"]
        coords = toponym["Point"]["pos"]
        longitude, latitude = coords.split(" ")

        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'name': user.name,
                'surname': user.surname,
                'city_from': user.city_from
            },
            'coordinates': {
                'longitude': longitude,
                'latitude': latitude
            },
            'address': toponym.get('metaDataProperty', {}).get('GeocoderMetaData', {}).get('text', '')
        })

    except requests.exceptions.RequestException as e:
        return make_response(jsonify({
            'error': 'Map service error',
            'message': str(e)
        }), 500)
