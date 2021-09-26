import datetime
import jwt
import uuid
from flask import Blueprint
from flask import request, jsonify, make_response
from flask_cors import CORS
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

from rnd_api import app
from rnd_api import db
from rnd_api.models import (Commune, Candidate, GlobalResult, PartieResult, Partie, Commune, Wilaya, CandidateResult, PartieResult)
from rnd_api.schema import CommuneSchema, CandidateSchema, PartieSchema
from rnd_api.util import token_required

communes = Blueprint('communes', __name__, url_prefix='/api')
cors = CORS(communes)

# verbs implementation for commune routes-----------------------------------------------------------------

commune_schema = CommuneSchema()
communes_schema = CommuneSchema(many=True)

@communes.route('/commune', methods=['GET', 'POST'])
@token_required
def commune(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!','success':False})

    

    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            #print(1)
            try:
                if data['user_id']:
                    new_commune = Commune(name=str(data['name']),
                                        ons_code=str(data['ons_code']),
                                        number_of_voting_offices=int(data['number_of_voting_offices']),
                                        number_of_registrants=int(data['number_of_registrants']),
                                        user_id=int(data['user_id']),
                                        wilaya_code=int(data['wilaya_code']))
                    db.session.add(new_commune)
                    db.session.commit()
                else:
                    new_commune = Commune(name=str(data['name']),
                                        ons_code=str(data['ons_code']),
                                        number_of_voting_offices=int(data['number_of_voting_offices']),
                                        number_of_registrants=int(data['number_of_registrants']),
                                        user_id=None,
                                        wilaya_code=int(data['wilaya_code']))
                    db.session.add(new_commune)
                    db.session.commit()

            except Exception as e:
                #print(e)
                return jsonify({'message': 'operation failed', 'success': False})
            return jsonify({'message': f'commune {new_commune.name} has been created successfully.', 'success': True})
        else:
            return jsonify({'message': 'The request payload is not in JSON format', 'success': False })
    elif request.method == 'GET':
        communes = Commune.query.all()
        if not communes:
            return jsonify({'message': 'no communes found', 'success': False})
        results = communes_schema.dump(communes)
        return jsonify({'count': len(results), 'communes': results, 'success': True})


@communes.route('/commune/<int:ons_code>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def handle_commune(current_user, ons_code):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!', 'success': False})
    commune = db.session.query(Commune).filter_by(ons_code=ons_code).first()

    if request.method == 'GET':
        if commune is  None:
            return jsonify({'message': 'commune not found', 'success': False})
        return jsonify({'commune': commune_schema.dump(commune), 'success': True})
    elif request.method == 'PUT':
        if commune is  None:
            return jsonify({'message': 'commune not found', 'success': False})
        if request.is_json:
            data = request.get_json()
            try:
                commune.name = str(data['name'])
                commune.ons_code = str(data['ons_code'])
                commune.number_of_voting_offices = int(data['number_of_voting_offices'])
                commune.number_of_registrants = int(data['number_of_registrants'])
                commune.user_id=int(data['user_id'])
                commune.wilaya_code=int(data['wilaya_code'])
                db.session.add(commune)
                db.session.commit()
            except Exception as e:
                #print(e)
                return jsonify({'message': 'operation failed', 'success': False})

            return jsonify({'message': f'commune {commune.name} has been updated successfully.','success' : False})
        else:
            return jsonify({'message': 'The request payload is not in JSON format','success' : False})
    elif request.method == 'DELETE':
        if not commune:
            return jsonify({'message': 'commune not found', 'success': False})
        try:
            db.session.delete(commune)
            db.session.commit()
        except Exception as e:
            #print(e)
            return jsonify({'message': 'operation failed', 'success': False})
        return jsonify({"message": f"commune {commune.name} successfully deleted.",'success' : True})


# this end point save the commune global result informations-----------------------------------------------
@communes.route('/commune/result', methods=['POST'])
@token_required
def global_result(current_user):
    """if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!', 'success': False})"""

    if request.is_json:
        data = request.get_json()
        
        try:
            new_result = GlobalResult(number_of_voters=int(data['number_of_voters']),
                                      number_of_cards_canceled=int(data['number_of_cards_canceled']),
                                      number_of_voters_received=int(data['number_of_voters_received']),
                                      number_of_disputed_cards=int(data['number_of_disputed_cards']),
                                      user_id=int(data['user_id']),
                                      commune_ons_code=int(data['commune_ons_code']),
                                      post=str(data['post']))

            db.session.add(new_result)
            db.session.commit()
        except Exception as e:
            print(e)
            return jsonify({'message':'operation failed',
                                'success' : False  })
        return jsonify({'message': 'results  has been saved successfully.','success' : True})
    else:
        return jsonify({'message': 'The request payload is not in JSON format','success' : False})


# return result of specifiq commune---------------------------------------------------------------
@communes.route('/commune/<int:ons_code>/result', methods=['GET'])
@token_required
def commune_result(current_user,ons_code):
    commune = db.session.query(Commune).filter_by(ons_code=ons_code).first()
    if commune:
        commune_result = commune.results[-1]
        if commune.number_of_voting_offices:
            number_of_voting_offices=commune.number_of_voting_offices
        else:
            number_of_voting_offices=0

        if commune.number_of_registrants:
            number_of_registrants=commune.number_of_registrants
        else:
            number_of_registrants=0

        return jsonify({
            'success': True,
            'commune': {
                'id': commune.id,
                'name': commune.name,
                'ons_code': commune.ons_code,
                'number_of_voting_offices': number_of_voting_offices,
                'number_of_registrants': number_of_registrants,
                'number_of_cards_canceled': commune.results[-1].number_of_cards_canceled,
                'number_of_voters_received': commune.results[-1].number_of_voters_received,
                'number_of_disputed_cards': commune.results[-1].number_of_disputed_cards,
                'number_of_voters': commune.results[-1].number_of_voters,
                'reporter_first_name': commune.results[-1].user.first_name,
                'reporter_last_name': commune.results[-1].user.last_name,
                'reporter_id': commune.results[-1].user.id,
                'result_date': commune.results[-1].date_created
                                    }
                        })
       
    else:
        return jsonify({'message': 'commune not exist',
                        'success': False})


@communes.route('/commune/wilaya/<int:code>', methods=['GET'])
@token_required
def get_wilaya_commune(current_user, code):
    print(code)
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!', 'success': False})
    communes = db.session.query(Commune).filter_by(wilaya_code=code)
    if commune is None:
        return jsonify({'message': 'commune not found', 'success': False})
    results = communes_schema.dump(communes)
    return jsonify({'communes': results, 'success': True})



