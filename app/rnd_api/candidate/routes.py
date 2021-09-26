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
from rnd_api.models import (Commune, Candidate, GlobalResult, Wilaya, CandidateResult)
from rnd_api.schema import CommuneSchema, CandidateSchema
from rnd_api.util import token_required

candidates = Blueprint('candidates', __name__, url_prefix='/api')
cors = CORS(candidates)

# verbs implementation for candidate routes-----------------------------------------------------------------
candidate_schema = CandidateSchema()
candidates_schema = CandidateSchema(many=True)


# add candidate
@candidates.route('wilaya/candidate', methods=['POST'])
@token_required
def candidate(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            try:
                new_candidate = Candidate(first_name=str(data['first_name']), last_name=str(data['last_name']), wilaya_code=int(data['wilaya_id']))
                db.session.add(new_candidate)
                db.session.commit()
            except:
                return jsonify({'message': 'operation failed',
                                'success': False})
            return jsonify({'message': f'candidate {new_candidate.first_name} has been created successfully.',
                            'success': True})
        else:
            return jsonify({'message': 'The request payload is not in JSON format', 'success': False})


# return wilaya candidates--------------------------------------------------------------------
@candidates.route('/wilaya/<int:wilaya_code>/candidate', methods=['GET'])
@token_required
def get_all_candidate(current_user, wilaya_code):
    wilaya = db.session.query(Wilaya).filter_by(code=wilaya_code).first()
    if not wilaya:
        return jsonify({'message': 'wilaya not found', 'success': False})
    if request.method == 'GET':
        candidates = wilaya.candidates
        if candidates.first() is not None:
            res = candidates_schema.dump(candidates)
            return jsonify({'count': len(res), 'candidates': res, 'success': True})
        return jsonify({'message': 'candidates not found', 'success': False})
    return jsonify({'message': 'method not allowed', 'success': False})


# return candidates for specific commune


# handle specific candidate
@candidates.route('/candidate/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def handle_candidate(current_user, id):
    '''if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})'''

    candidate = Candidate.query.get(id)
    if not candidate:
        return jsonify({'message': 'candidate not found', 'success': False})
    if request.method == 'GET':
        return jsonify({'candidate': candidate_schema.dump(candidate), 'success': True})
    elif request.method == 'PUT':
        if request.is_json:
            data = request.get_json()
            try:
                candidate.first_name = data['first_name']
                candidate.last_name = data['last_name']
                candidate.wilaya_code = data['wilaya_code']
                db.session.add(candidate)
                db.session.commit()
                return jsonify(
                    {'message': f'candidate {candidate.first_name} has been updated successfully.', 'success': True})
            except Exception as e:
                return jsonify({'message': 'operation failed.', 'success': False})
        else:
            return jsonify({'message': 'The request payload is not in JSON format', 'success': False})
    elif request.method == 'DELETE':
        try:
            db.session.delete(candidate)
            db.session.commit()
            return jsonify({"message": f"reporter {candidate.first_name} successfully deleted.", 'success': True})
        except Exception as e:
            return jsonify({'message': 'operation failed.', 'success': False})


# this end point save the commune candidates result informations [results for multiples candidates]-----------------------------------------------
@candidates.route('/commune/candidate/result', methods=['POST'])
@token_required
def add_candidate_result(current_user):
    if request.is_json:
        data = request.get_json()  # data = {'results:[{},{}]}
        try:
            for result in data['results']:
                new_candidate_result = CandidateResult(result=int(result['result']),
                                                       candidate_id=int(result['candidate_id']),
                                                       commune_ons_code=int(result['commune_ons_code']),
                                                       user_id=int(result['reporter_id']),
                                                       post=str(result['post']))
                db.session.add(new_candidate_result)
                db.session.commit()


        except Exception as e:
            print(e)
            return jsonify({'message': 'operation failed in candidate add result', 'success': False})
        return jsonify({'message': 'candidates results saved succesfuly', 'success': True})
    else:
        return jsonify({'message': 'The request payload is not in JSON format', 'success': False})


# return candidate results for specific commune------------------------------------------------------------
@candidates.route('/commune/<int:ons_code>/candidate/result', methods=['GET'])
@token_required
def cadidate_commune_result(current_user, ons_code):
    if request.method == 'GET':
        commune = db.session.query(Commune).filter_by(ons_code=ons_code).first()
        if not commune:
            return jsonify({'message': 'commune not found', 'success': False})
        wilaya = db.session.query(Wilaya).filter_by(code=commune.wilaya.code).first()
        candidates = wilaya.candidates.all()
        commune_results = commune.candidates_result
        candidate_result = []
        candidate_final_result = []

        if commune_results.first() is not None:
            for candidate in candidates:
                for result in commune_results:
                    if result.candidate_id == candidate.id:
                        candidate_result.append(result)
                # candidate_final_result.append(candidate_result[-1])
                candidate_final_result.append({
                    #'commune_id': int(candidate_result[-1].commune_id),
                    'candidate_result': int(candidate_result[-1].result),
                    'candidate_id': candidate_result[-1].candidate_id,
                    'commune_name': candidate_result[-1].commune.name,
                    'commune_ons_code': candidate_result[-1].commune.ons_code,
                    'reporter_id': candidate_result[-1].user_id,
                    'post': candidate_result[-1].post,
                    'candidate_name': candidate_result[-1].candidate.first_name,
                    'candidate_last_name': candidate_result[-1].candidate.last_name,
                    'wilaya_name': candidate_result[-1].candidate.wilaya.name,
                    'wilaya_code': candidate_result[-1].candidate.wilaya.code,
                    'candidate_purcentage': float(
                        candidate_result[-1].result / get_number_of_veters_received_commune(commune.ons_code)) * 100
                })
                candidate_result = []
            return jsonify({'commune_candidate_result': candidate_final_result, 'success': True})

        return jsonify({'message': 'commune have no result', 'success': False})


# return candidate result for specific wilaya --------------------------------------------------------
@candidates.route('/wilaya/<int:code>/candidate/result', methods=['GET'])
@token_required
def candidate_wilaya_result(current_user, code):
    if request.method == 'GET':
        wilaya = db.session.query(Wilaya).filter_by(code=code).first()
        if not wilaya:
            return jsonify({'message': 'wilaya not found', 'success': False})
        communes = wilaya.commune.all()
        if not communes:
            return jsonify({'message': 'wilaya have no commune', 'success': False})

        candidates = wilaya.candidates.all()
        wilaya_communes_candidates_results = []
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

            commune_results = commune.candidates_result
            candidate_result = []
            commune_candidate_final_result = []

            if commune_results.first() is not None:

                for candidate in candidates:
                    for result in commune_results:
                        if result.candidate_id == candidate.id:
                            candidate_result.append(result)
                    #candidate_final_result.append(candidate_result[-1])
                    if candidate_result[-1].commune.results.first() is not None:
                        commune_candidate_final_result.append({
                            #'commune_ons_code':candidate_result[-1].commune_id,
                            'candidate_result':candidate_result[-1].result,
                            'candidate_id':candidate_result[-1].candidate_id,
                            #'commune_name':candidate_result[-1].commune.name,
                            'reporter_phone_number': reporter_phone_number,
                            'reporter_first_name': reporter_first_name,
                            'reporter_last_name':reporter_last_name,
                            #'commune_ons_code':candidate_result[-1].commune.ons_code,
                            'reporter_id': candidate_result[-1].user_id,
                            'post': candidate_result[-1].post,
                            'candidate_first_name': candidate_result[-1].candidate.first_name,
                            'candidate_last_name': candidate_result[-1].candidate.last_name,
                            #'wilaya_name':candidate_result[-1].candidate.wilaya.name,
                            'candidate_commune_purcentage':round(float(candidate_result[-1].result/get_number_of_veters_received_commune(commune.ons_code) )*100,2)
                            #'wilaya_code':candidate_result[-1].candidate.wilaya.code
                            })
                        candidate_result=[]
                    else:
                        commune_candidate_final_result.append({
                            #'commune_ons_code':candidate_result[-1].commune_id,
                            'candidate_result':candidate_result[-1].result,
                            'candidate_id':candidate_result[-1].candidate_id,
                            #'commune_name':candidate_result[-1].commune.name,
                            'reporter_phone_number': reporter_phone_number,
                            'reporter_first_name': reporter_first_name,
                            'reporter_last_name': reporter_last_name,
                            #'commune_ons_code':candidate_result[-1].commune.ons_code,
                            'reporter_id': candidate_result[-1].user_id,
                            'post': candidate_result[-1].post,
                            'candidate_first_name': candidate_result[-1].candidate.first_name,
                            'candidate_last_name': candidate_result[-1].candidate.last_name,
                            #'wilaya_name':candidate_result[-1].candidate.wilaya.name,
                            'candidate_commune_purcentage':None
                            #'wilaya_code':candidate_result[-1].candidate.wilaya.code
                            })
                        candidate_result=[]

                wilaya_communes_candidates_results.append({'commune_name':commune.name,
                                                           'commune_ons_code':commune.ons_code,
                                                           'commune_have_result':True,
                                                           'commune_candidate_result':commune_candidate_final_result})
                candidate_final_result=[]
            else:
                for candidate in candidates:
                    '''for result in commune_results:
                        if result.candidate.id == candidate.id:
                            candidate_result.append(result)'''
                    #candidate_final_result.append(candidate_result[-1])
                    commune_candidate_final_result.append({
                        #'commune_ons_code':candidate_result[-1].commune_id,
                        'candidate_result':None,
                        'candidate_id':None,
                        #'commune_name':candidate_result[-1].commune.name,
                        'reporter_phone_number': reporter_phone_number,
                        'reporter_first_name': reporter_first_name,
                        'reporter_last_name': reporter_last_name,
                        #'commune_ons_code':candidate_result[-1].commune.ons_code,
                        'reporter_id': reporter_id,
                        'post': None,
                        'candidate_first_name': None,
                        'candidate_last_name': None
                        #'wilaya_name':candidate_result[-1].candidate.wilaya.name,
                        #'candidate_commune_purcentage':round(float(candidate_result[-1].result/get_number_of_veters_received_commune(commune.ons_code) )*100,2)
                        #'wilaya_code':candidate_result[-1].candidate.wilaya.code
                        })
                    candidate_result=[]
                wilaya_communes_candidates_results.append({'commune_name':commune.name,
                                                           'commune_ons_code':commune.ons_code,
                                                           'commune_have_result':False,
                                                           'commune_candidate_result':commune_candidate_final_result})
                candidate_final_result=[]
                
                """commune_candidate_final_result.append({
                    #'commune_ons_code':commune.ons_code,
                    'candidate_result':None,
                    'candidate_id':None,
                    #'commune_name':commune.name,
                    #'commune_ons_code':commune.ons_code,
                    'reporter_id':commune.user_id,
                    'reporter_phone_number':commune.user.phone_number,
                    'reporter_first_name':commune.user.first_name,
                    'reporter_last_name':commune.user.last_name,
                    'post':None,
                    'candidate_name':None,
                    'candidate_last_name':None,
                    #'wilaya_name':commune.wilaya.name,
                    #'wilaya_code':commune.wilaya.code
                    })"""

                '''wilaya_communes_candidates_results.append({'commune_name':commune.name,
                                                           'commune_ons_code':commune.ons_code,
                                                           'commune_have_result':False,
                                                           'commune_candidate_result':commune_candidate_final_result})'''
        
        wilaya_candidates_result=[]  #calculate candidate result in wilaye
        for candidate in candidates:
            candidate_result = 0

            for commune in wilaya_communes_candidates_results:

                for c in commune['commune_candidate_result']:
                    if c['candidate_id'] == candidate.id and c['candidate_result'] is not None:
                        candidate_result += c['candidate_result']
                    else:
                        candidate_result += 0
            wilaya_candidates_result.append({
                'candidate_id': candidate.id,
                'candidate_first_name': candidate.first_name,
                'candidate_last_name': candidate.last_name,
                'candidate_result': candidate_result,
                'candidate_wilaya_purcentage': round(float(candidate_result / get_number_of_veters_received_wilaya(wilaya.code)) * 100, 2),
            })

        return jsonify({'communes_result': wilaya_communes_candidates_results,
                        'wilaya_result': wilaya_candidates_result,
                        'wilaya_name': wilaya.name,
                        'wilaya_code': wilaya.code,
                        'success': True})




