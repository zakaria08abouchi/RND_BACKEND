import datetime
import jwt
import json
import uuid
from flask import Blueprint
from flask import request, jsonify, make_response
from flask_cors import CORS
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

from rnd_api import app
from rnd_api import db
from rnd_api.models import User, Commune, Wilaya
from rnd_api.schema import ReporterSchema, ReporterWilayaSchema, CommuneSchema, WilayaSchema
from rnd_api.util import token_required
from sqlalchemy import and_

users = Blueprint('users', __name__, url_prefix='/api')
cors = CORS(users)

commune_schema = CommuneSchema()
wilaya_schema = WilayaSchema()

@users.route('/health', methods=['GET', 'POST'])
def healthCheck():
    return jsonify({
        'status': '200',
        'message': 'healthy'
    })


# users routes--------------------------------------------------------------------------------------------

@users.route('/user/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data['phone_number'] or not data['password']:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    
    #user = User.query.filter_by(phone_number=data['phone_number']).first()
    user=db.session.query(User).filter_by(phone_number=data["phone_number"]).first()
    print(user)
    if not user:
        return make_response('Could not verify user', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    if check_password_hash(user.password, data['password']):
        token = jwt.encode(
            {'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1440)},
            app.config['SECRET_KEY']).decode('utf-8')
        response = {'id': user.id,
                    'public_id': user.public_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone_number': user.phone_number,
                    'post': user.post,
                    'admin': user.admin}
        if user.post == 'commune':
            if user.commune:
                response['commune'] = commune_schema.dump(db.session.query(Commune).filter_by(ons_code=user.commune.ons_code).first())
                response['wilaya'] = wilaya_schema.dump(db.session.query(Wilaya).filter_by(code=user.commune.wilaya.code).first())
            else:
                response['commune']=None 
                response['wilaya']=None   
        if user.post == 'wilaya':
            if user.wilaya:
                response['wilaya'] = wilaya_schema.dump(db.session.query(Wilaya).filter_by(code=user.wilaya.code).first())
            else:
                response['wilaya']=None
        response['token'] = token
        if user.post=='admin':
            return jsonify(response)
        return jsonify(response)
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@users.route('/user', methods=['POST'])
@token_required
def create_user(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!', 'success': False})
    data = request.get_json()
    
    
    new_user = User(
        with_id=False,
        id=None,
        public_id=str(uuid.uuid4()),
        first_name=str(data['first_name']),
        last_name=str(data['last_name']),
        phone_number=str(data['phone_number']),
        post=str(data['post']),
        password=data['first_name'][1] + data['last_name'][1] + str(  data['phone_number'][3:6]  ) + data['first_name'][1] + data['last_name'][1])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created! 1', 'success': True})

@users.route('/user/csv', methods=['POST'])
@token_required
def create_user_csv(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!', 'success': False})
    data = request.get_json()
    
    
    new_user = User(
        with_id=True,
        id=int(data['id']),
        public_id=str(uuid.uuid4()),
        first_name=str(data['first_name']),
        last_name=str(data['last_name']),
        phone_number=str(data['phone_number']),
        post=str(data['post']),
        password=data['first_name'][1] + data['last_name'][1] + str( data['phone_number'][3:6]   ) + data['first_name'][1] + data['last_name'][1])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created! with id', 'success': True})



        


@users.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    #print(current_user)
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!', 'success': False})
    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['public_id'] = user.public_id
        user_data['first_name'] = user.first_name
        user_data['last_name'] = user.last_name
        user_data['post'] = user.post
        user_data['admin'] = user.admin
        user_data['password'] = user.password
        user_data['phone_number'] = user.phone_number
        user_data['commune'] = {}
        user_data['wilaya'] = {}
        if user_data['post'] == 'commune' and user.commune:
            user_data['commune'] = commune_schema.dump(db.session.query(Commune).filter_by(ons_code=user.commune.ons_code).first())
            user_data['wilaya'] = wilaya_schema.dump(db.session.query(Wilaya).filter_by(code=user.commune.wilaya.code).first())
        if user_data['post'] == 'wilaya' and user.wilaya:
            user_data['wilaya'] = wilaya_schema.dump(db.session.query(Wilaya).filter_by(code=user.wilaya.code).first())

        output.append(user_data)

    return jsonify({'users': output, 'success': True})


@users.route('/user/<id>', methods=['GET'])
@token_required
def get_one_user(current_user, id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!', 'success': False})

    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({'message': 'No user found!', 'success': False})

    user_data = {}
    user_data['id'] = user.id
    user_data['public_id'] = user.public_id
    user_data['first_name'] = user.first_name
    user_data['last_name'] = user.last_name
    user_data['post'] = user.post
    user_data['phone_number'] = user.phone_number
    user_data['admin'] = user.admin
    user_data['commune'] = {}
    user_data['wilaya'] = {}
    if user_data['post'] == 'reporter':
        user_data['commune'] = commune_schema.dump(db.session.query(Commune).get(user.commune.id))
        user_data['wilaya'] = wilaya_schema.dump(db.session.query(Wilaya).get(user.commune.wilaya.id))
    if user_data['post'] == 'reporter_wilaya':
        user_data['wilaya'] = wilaya_schema.dump(db.session.query(Wilaya).get(user.wilaya.id))

    return jsonify({'result': user_data, 'success': True})


@users.route('/user/<id>', methods=['PUT'])
@token_required
def promote_user(current_user, id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!', 'success': False})

    data = request.get_json()
    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({'message': 'No user found!', 'success': False})
    user.first_name = data['first_name']
    user.last_name = data['last_name']
    user.name = data['last_name'] + ' ' + data['first_name']
    user.post = data['post']
    user.phone_number = data['phone_number']
    user.admin = data['admin']
    db.session.add(user)
    db.session.commit()

    return jsonify({'result': 'The user has been updated!', 'success': True})


@users.route('/user/<id>', methods=['DELETE'])
@token_required
def delete_user(current_user, id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!', 'success': False})

    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({'message': 'No user found!', 'success': False})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'result': 'The user has been deleted!', 'success': True})

@users.route('/user/autocomplete', methods=['POST'])
@token_required
def autocomplete_user(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!', 'success': False})
    data = request.get_json()

    if not data['value'] or data['value'] == '':
        users = User.query.filter_by(post=data['query'])
    else:
        # users = User.query.filter_by(post=data['query'], name=data['value'])
        users = User.query.filter(and_(User.name.ilike('%'+data['value']+'%'), User.post == data['query'])).all()

    output = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['first_name'] = user.first_name
        user_data['last_name'] = user.last_name
        user_data['post'] = user.post
        user_data['admin'] = user.admin
        user_data['phone_number'] = user.phone_number
        user_data['commune'] = {}
        user_data['wilaya'] = {}
        if user_data['post'] == 'commune' and user.commune:
            user_data['commune'] = commune_schema.dump(
                db.session.query(Commune).filter_by(ons_code=user.commune.ons_code).first())
            user_data['wilaya'] = wilaya_schema.dump(
                db.session.query(Wilaya).filter_by(code=user.commune.wilaya.code).first())
        if user_data['post'] == 'wilaya' and user.wilaya:
            user_data['wilaya'] = wilaya_schema.dump(db.session.query(Wilaya).filter_by(code=user.wilaya.code).first())

        output.append(user_data)

    return jsonify({'result': output, 'success': True})



