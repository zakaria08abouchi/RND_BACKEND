import datetime
import jwt
import uuid
from flask import Blueprint
from flask import request, jsonify, make_response
from flask_cors import CORS
from functools import wraps
from .util import get_number_of_veters_received_commune, get_number_of_veters_received_wilaya
from rnd_api import app
from rnd_api import db
from rnd_api.models import (Commune, GlobalResult,
                            Wilaya, Partie, PartieResult)
from rnd_api.schema import CommuneSchema, PartieSchema
from rnd_api.util import token_required

parties = Blueprint('parties', __name__, url_prefix='/api')
cors = CORS(parties)

# verb implementations for commune parties-------------------------------------------------
partie_schema = PartieSchema()
parties_schema = PartieSchema(many=True)


@parties.route('/partie', methods=['GET', 'POST'])
@token_required
def partie(current_user):
    if request.method == 'POST':
        if request.is_json:
            try:
                data = request.get_json()
                new_partie = Partie(name=str(data['name']), wilaya_code=int(data['wilaya_code']), code=int(data['code']))
                db.session.add(new_partie)
                db.session.commit()
                return jsonify({'message': f'partie {new_partie.name} has been created successfully.',
                                'success': True})
            except Exception as e:
                return jsonify({'message': 'operation failed in add new partie',
                                'success': False})

        else:
            return jsonify({'message': 'The request payload is not in JSON format', 'success': False})
    elif request.method == 'GET':
        parties = Partie.query.all()
        if parties:
            results = parties_schema.dump(parties)
            return jsonify({'count': len(results), 'parties': results, 'success': True})
        else:
            return jsonify({'message': 'no partie are found', 'success': False})


# handle partie add or delete or modif partie
@parties.route('/partie/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def handle_partie(current_user, id):
    partie = Partie.query.get(id)
    if not candidate:
        return jsonify({'message': 'this partie id not found', 'success': False})
    if request.method == 'GET':
        return jsonify({'partie': partie_schema.dump(partie), 'success': True})
    elif request.method == 'PUT':
        if request.is_json:
            try:
                data = request.get_json()
                partie.name = data['name']
                partie.commune_id = data['commune_id']
                db.session.add(partie)
                db.session.commit()
                return jsonify({'message': f'partie {partie.name} has been updated successfully.', 'success': True})
            except:
                return jsonify({'message': 'operation failed', 'success': False})
        else:
            return jsonify({'message': 'The request payload is not in JSON format', 'success': False})
    elif request.method == 'DELETE':
        try:
            db.session.delete(partie)
            db.session.commit()
            return jsonify({"message": f"partie {partie.name} successfully deleted.", 'success': True})
        except:
            return jsonify({'message': 'operation failed', 'success': False})


# return parties list for specific wilaya--------------------------------------------------------------
@parties.route('/wilaya/<int:code_wilaya>/partie', methods=['GET'])
@token_required
def handle_commune_partie(current_user, code_wilaya):
    wilaya = db.session.query(Wilaya).filter_by(code=code_wilaya).first()
    if not wilaya:
        return jsonify({'message': 'this wilaya id not found', 'success': False})
    if request.method == 'GET':
        parties = wilaya.parties
        if parties:
            res = parties_schema.dump(parties)
            return jsonify({'count': len(res), 'wilaya_parties': res, 'success': True})
        else:
            return jsonify({'message': 'no parties for this wilaya', 'success': False})


# this end point save the commune partie result informations [results for multiples partie]-----------------------------------------------
@parties.route('/commune/partie/result', methods=['POST'])
@token_required
def add_partie_result(current_user):
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()  # data = {'results:[{},{}]}
            try:
                for results in data['results']:
                    new_partie_result = PartieResult(result=int(results['result']),
                                                     partie_id=int(results['partie_id']),
                                                     commune_ons_code=int(results['commune_ons_code']),
                                                     user_id=int(results['reporter_id']),
                                                     post=str(results['post']))
                    db.session.add(new_partie_result)
                    db.session.commit()

            except Exception as e:
                #print(e)
                return jsonify({'message': 'operation failed in partie add result', 'success': False})
            return jsonify({'message': 'parti results saved succesfuly', 'success': True})
        else:
            return jsonify({'message': 'The request payload is not in JSON format',
                            'success': False})


# return partie results for a specific commune
@parties.route('/commune/<int:ons_code>/partie/result', methods=['GET'])
@token_required
def return_partie_commune_results(current_user, ons_code):
    if request.method == 'GET':
        commune = db.session.query(Commune).filter_by(ons_code=ons_code).first()
        if commune:
            wilaya = db.session.query(Wilaya).filter_by(code=commune.wilaya.code).first()
            parties = wilaya.parties
            commune_results = commune.parties_result
            partie_results = []
            commune_parties_result = []
            
            if commune_results.first() is not None:
                for partie in parties.all():
                    
                    for result in commune_results.all():
                        
                        if result.partie_id == partie.id:
                            partie_results.append(result)
                   
                    commune_parties_result.append({
                        #'commune_id': int(partie_results[-1].commune_id),
                        'partie_id': int(partie_results[-1].partie_id),
                        'partie_result': int(partie_results[-1].result),
                        'reporter_id': int(partie_results[-1].user_id),
                        'partie_name': partie_results[-1].partie.name,
                        'post': partie_results[-1].post,
                        'commune_ons_code': commune.ons_code,
                        'wilaya_name': commune.wilaya.name,
                        'wilaya_code': commune.wilaya.code,
                        'partie_purcentage': float(
                            partie_results[-1].result / get_number_of_veters_received_commune(commune.ons_code)) * 100
                    })
                    
                    partie_results = []
                return jsonify({'commune_parties_result': commune_parties_result, 'success': True})
            else:
                return jsonify({'message': 'commune have no result yet', 'success': False})



        else:
            return jsonify({'message': 'commune not found', 'success': False})


# return partie result for specific wilaya------------------------------------------------------------
@parties.route('/wilaya/<int:code>/partie/result')
@token_required
def return_partie_wilaya_result(current_user, code):
    wilaya = db.session.query(Wilaya).filter_by(code=code).first()
    if not wilaya:
        return jsonify({'message': 'wilaya not found', 'success': False})
    communes = wilaya.commune.all()
    if not communes:
        return jsonify({'message':'wilaya have no commune','success':False})
    
    parties=wilaya.parties
    if parties.first() is None:
        return jsonify({'message':'wilaya have no parties','success':False})
    wilaya_communes_parties_result=[]

    #commune------------------------------
    for commune in communes:
        if commune.user:
            reporter_phone_number=commune.user.phone_number
            reporter_first_name=commune.user.first_name
            reporter_last_name=commune.user.last_name
            reporter_id=commune.user_id
        else:
            reporter_phone_number=None
            reporter_first_name=None
            reporter_last_name=None
            reporter_id=None

        commune_results=commune.parties_result
        partie_results=[]
        commune_parties_result=[]

        if commune_results.first() is not None:

            for partie in parties:
                for result in commune_results:
                    if result.partie_id == partie.id:
                            partie_results.append(result)
                commune_parties_result.append({
                    'commune_ons_code':int(partie_results[-1].commune_ons_code),
                    'partie_id':int(partie_results[-1].partie_id),
                    'partie_result':int(partie_results[-1].result),
                    'reporter_id':int(partie_results[-1].user_id),
                    'partie_name':partie_results[-1].partie.name,
                    'post':partie_results[-1].post,
                    'reporter_phone_number': reporter_phone_number,
                    'reporter_first_name': reporter_first_name,
                    'reporter_last_name': reporter_last_name
                    #'ons_code':commune.ons_code,
                    #'wilaya_name':commune.wilaya.name,
                    #'wilaya_code':commune.wilaya.code,
                    #'partie_commune_purcentage':round(float(partie_results[-1].result/get_number_of_veters_received_commune(commune.ons_code) )*100,2),
                    })
                partie_results=[]

            wilaya_communes_parties_result.append({
                'commune_ons_code':commune.ons_code,
                'commune_name':commune.name,
                'commune_have_result':True,
                'commune_parties_result':commune_parties_result
            })

            #commune_parties_result=[]
        else:
            for partie in parties:    
                commune_parties_result.append({
                    #'commune_ons_code':int(commune.ons_code),
                    'partie_id':None,
                    'partie_result':None,
                    'reporter_id':reporter_id,
                    'partie_name':None,
                    'post':None,
                    'reporter_phone_number': reporter_phone_number,
                    'reporter_first_name': reporter_first_name,
                    'reporter_last_name': reporter_last_name
                    #'ons_code':commune.ons_code,
                    #'wilaya_name':commune.wilaya.name,
                    #'wilaya_code':commune.wilaya.code,
                    #'partie_commune_purcentage':round(float(partie_results[-1].result/get_number_of_veters_received_commune(commune.ons_code) )*100,2),
                    })
                partie_results=[]

            wilaya_communes_parties_result.append({
                'commune_ons_code':commune.ons_code,
                'commune_name':commune.name,
                'commune_have_result':False,
                'commune_parties_result':commune_parties_result
            })
            
            #commune_parties_result=[]
            '''commune_parties_result.append({
                    'commune_ons_code':commune.ons_code,
                    'partie_id':None,
                    'partie_result':None,
                    'reporter_id':commune.user.id,
                    'partie_name':None,
                    'post':None
                    #'ons_code':commune.ons_code,
                    #'wilaya_name':commune.wilaya.name,
                    #'wilaya_code':commune.wilaya.code
                    })
            
            wilaya_communes_parties_result.append({
                'commune_ons_code':commune.ons_code,
                'commune_name':commune.name,
                'commune_have_result':False,
                'commune_parties_result':commune_parties_result
            })'''
    # wilaya -----------------------------------
    wilaya_parties_result = []

    for partie in parties:
        partie_result = 0
        for commune in wilaya_communes_parties_result:
            for p in commune['commune_parties_result']:
                if p['partie_id'] == partie.id and p['partie_result'] is not None:
                    partie_result += p['partie_result']
                else:
                    partie_result += 0
        wilaya_parties_result.append({
            'partie_id': partie.id,
            'partie_name': partie.name,
            'partie_result': partie_result,
            'partie_wilaya_purcentage': round(
                float(partie_result / get_number_of_veters_received_wilaya(wilaya.code)) * 100, 2),
        })

    return jsonify({'commune_results': wilaya_communes_parties_result,
                    'wilaya_results': wilaya_parties_result,
                    'wilaya_name': wilaya.name,
                    'wilaya_code': wilaya.code,
                    'success': True})





