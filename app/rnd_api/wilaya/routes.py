import datetime
import jwt
import uuid
from flask import Blueprint
from flask import request, jsonify, make_response
from flask_cors import CORS
from functools import wraps


from rnd_api import app
from rnd_api import db
from rnd_api.models import Wilaya
from rnd_api.schema import WilayaSchema,CandidateSchema
from rnd_api.util import token_required

wilayas = Blueprint('wilayas', __name__, url_prefix='/api')
cors = CORS(wilayas)

# verbs implementation for wilaya routes-----------------------------------------------------------------
wilaya_schema = WilayaSchema()
wilayas_schema = WilayaSchema(many=True)


@wilayas.route('/wilaya', methods=['GET', 'POST'])
@token_required
def wilaya(current_user):
    if request.method == 'POST':
        if request.is_json:
            # try:
            data = request.get_json()
            print(data)
            if not data['user_wilaya_id']:
                new_wilaya = Wilaya(name=str(data['name']),
                                    code=int(data['code']),
                                    user_wilaya_id=None,
                                    number_of_places=int(data['number_of_places']))
            else:
                new_wilaya = Wilaya(name=str(data['name']),
                                    code=int(data['code']),
                                    user_wilaya_id=int(data['user_wilaya_id']),
                                    number_of_places=int(data['number_of_places']))


            db.session.add(new_wilaya)
            db.session.commit()
                
            # except:
            #     return jsonify({'message':'operation failed in save wilaya ','success' : False})
            return jsonify({'message': f'wilaya {new_wilaya.name} has been created successfully.','success' : True})
        else:
            return jsonify({'message': 'The request payload is not in JSON format','success' : False})
    elif request.method == 'GET':
        wilayas = Wilaya.query.all()
        if wilayas:
            results = wilayas_schema.dump(wilayas)
            return jsonify({'count': len(results), 'wilayas': results,'success' : True})
        else:
            return jsonify({'message':'no wilaya found','success' : False})


@wilayas.route('/wilaya/<int:code_wilaya>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def handle_wilaya(current_user, code_wilaya):
    wilaya = db.session.query(Wilaya).filter_by(code=code_wilaya).first()
    print(wilaya)
    # wilaya=db.session.query(Wilaya).get(id)
    
    if request.method == 'GET':
        if wilaya is  None:
            return jsonify({'message': 'wilaya not found','success' : False})
        return jsonify({'wilaya': wilaya_schema.dump(wilaya),'success' : True})
    elif request.method == 'PUT':
        if wilaya is  None:
            return jsonify({'message': 'wilaya not found','success' : False})
        if request.is_json:
            data = request.get_json()
            wilaya.name = str(data['name'])
            wilaya.code = str(data['code'])
            wilaya.user_wilaya_id = int(data['user_wilaya_id'])
            wilaya.number_of_places = int(data['number_of_places'])
            db.session.add(wilaya)
            db.session.commit()
            return jsonify({'message': f'wilaya {wilaya.name} has been updated successfully.','success' : True})
        else:
            return jsonify({'message': 'The request payload is not in JSON format','success' : False})
    elif request.method == 'DELETE':
        if wilaya is  None:
            return jsonify({'message': 'wilaya not found','success' : False})
        db.session.delete(wilaya)
        db.session.commit()
        return jsonify({"message": f"wilaya {wilaya.name} successfully deleted.",'success':True})
    else:
        return jsonify({"message": "you not allowed for this method",'success':False})






# return global results of a specific wilaya-------------------------------------------------------------------

@wilayas.route('/wilaya/<int:code_wilaya>/result', methods=['GET'])
@token_required
def wilaya_result(current_user, code_wilaya):
    wilaya = db.session.query(Wilaya).filter_by(code=code_wilaya).first()
    if wilaya is  None :
        return jsonify({'message':'wilaya not found','success':False})
    
    communes = wilaya.commune
    communes_results = []
    if communes.first() is not None:
        wilaya_number_of_voting_offices = 0
        wilaya_number_of_registrants = 0
        wilaya_number_of_voters = 0
        wilaya_number_of_cards_canceled = 0
        wilaya_number_of_voters_received = 0
        wilaya_number_of_disputed_cards = 0
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

            if commune.parties_result.first() is not None:
                commune_have_parties_result=True
            else:
                commune_have_parties_result=False
            if commune.candidates_result.first() is not None:
                commune_have_candidates_result=True
            else:
                commune_have_candidates_result=False
            
            if commune.number_of_voting_offices:
                number_of_voting_offices=commune.number_of_voting_offices
            else:
                number_of_voting_offices=0

            if commune.number_of_registrants:
                number_of_registrants=commune.number_of_registrants
            else:
                number_of_registrants=0

            commune_result = commune.results
            if commune_result.first() is not None:
                communes_results.append({'name': commune.name,
                                        'ons_code': commune.ons_code,
                                        'number_of_voting_offices': int(number_of_voting_offices),
                                        'number_of_registrants': int(number_of_registrants),                                 
                                        'number_of_voters': int(commune_result[-1].number_of_voters),
                                        'number_of_cards_canceled': int(commune_result[-1].number_of_cards_canceled),
                                        'number_of_voters_received': int(commune_result[-1].number_of_voters_received),
                                        'number_of_disputed_cards': int(commune_result[-1].number_of_disputed_cards),
                                        'reporter_id': commune_result[-1].user_id,
                                        'reporter_phone_number':reporter_phone_number,
                                        'reporter_first_name':reporter_first_name,
                                        'reporter_last_name':reporter_last_name,
                                        'commune_have_result':True,
                                        'commune_have_parties_result':commune_have_parties_result,
                                        'commune_have_candidates_result':commune_have_candidates_result
                                        #'commune_id': commune_result[-1].commune_id
                                        })
                wilaya_number_of_voting_offices += int(number_of_voting_offices)
                wilaya_number_of_registrants += int(number_of_registrants)
                wilaya_number_of_voters += int(commune_result[-1].number_of_voters)
                wilaya_number_of_cards_canceled += int(commune_result[-1].number_of_cards_canceled)
                wilaya_number_of_voters_received += int(commune_result[-1].number_of_voters_received)
                wilaya_number_of_disputed_cards += int(commune_result[-1].number_of_disputed_cards)
            else:
                communes_results.append({'name': commune.name,
                                            'ons_code': commune.ons_code,
                                            'number_of_voting_offices': int(number_of_voting_offices),
                                            'number_of_registrants': int(number_of_registrants),                                 
                                            'number_of_voters': None,
                                            'number_of_cards_canceled': None,
                                            'number_of_voters_received': None,
                                            'number_of_disputed_cards': None,
                                            'reporter_id': None,
                                            'reporter_phone_number':reporter_phone_number,
                                            'reporter_first_name':reporter_first_name,
                                            'reporter_last_name':reporter_last_name,
                                            'commune_id': None,
                                            'commune_have_result':False,
                                            'commune_have_parties_result':False,
                                            'commune_have_candidates_result':False
                                            })
                wilaya_number_of_voting_offices += int(number_of_voting_offices)
                wilaya_number_of_registrants += int(number_of_registrants)

        wilaya_global_result = {'wilaya_number_of_voting_offices': wilaya_number_of_voting_offices,
                                'wilaya_number_of_registrants': wilaya_number_of_registrants,
                                'wilaya_number_of_voters': wilaya_number_of_voters,
                                'wilaya_number_of_cards_canceled': wilaya_number_of_cards_canceled,
                                'wilaya_number_of_voters_received': wilaya_number_of_voters_received,
                                'wilaya_number_of_disputed_cards': wilaya_number_of_disputed_cards,
                                'wilaya_code': wilaya.code,
                                'wilaya_name': wilaya.name,
                                'wilaya_reporter_phone_number':wilaya.user.phone_number,
                                'wilaya_reporter_first_name':wilaya.user.first_name,
                                'wilaya_reporter_last_name':wilaya.user.last_name
                                }
        return jsonify({'wilaya': wilaya_global_result,
                        'communes': communes_results,
                        'success': True})
    return jsonify({'message': 'no commune for this wilaya','success':False})


