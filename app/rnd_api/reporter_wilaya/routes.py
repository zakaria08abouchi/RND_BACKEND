import datetime
import jwt
import uuid
from flask import Blueprint
from flask import request, jsonify, make_response
from flask_cors import CORS
from functools import wraps
from .util import get_commune_result,get_commune_candidate_result,get_commune_partie_result
from rnd_api import app
from rnd_api import db
from rnd_api.models import (Commune, Candidate, GlobalResult, Wilaya, CandidateResult)
from rnd_api.schema import CommuneSchema, CandidateSchema,PartieSchema
from rnd_api.util import token_required

wilaya_reporter = Blueprint('wilaya_reporter', __name__, url_prefix='/api')
cors = CORS(wilaya_reporter)

candidates_schema=CandidateSchema(many=True)
commune_schema=CommuneSchema()
parties_schema=PartieSchema(many=True)

@wilaya_reporter.route('/wilaya_reporter/commune/<int:ons_code>/result', methods=['GET'])
@token_required
def commune_reporter_result(current_user,ons_code):
    commune=db.session.query(Commune).filter_by(ons_code=ons_code).first()
    if commune is None:
        return jsonify({'message': 'commune not found','success':False})

    if commune.results.first() is None:
        commune_result = {
            'commune': {
            'id': commune.id,
            'name': commune.name,
            'ons_code': commune.ons_code,
            'number_of_voting_offices': None,
            'number_of_registrants': None,
            'number_of_cards_canceled': None,
            'number_of_voters_received': None,
            'number_of_disputed_cards':None,
            'number_of_voters': None,
            'reporter_first_name': commune.user.first_name,
            'reporter_last_name': commune.user.last_name,
            'reporter_id': commune.user_id,
            'result_date': None},
            'have_result': False
        }
    else:
        commune_result = get_commune_result(commune)
        commune_result['have_result'] = True
    
    if commune.candidates_result.first() is not None:
        commune_candidates_result = {
            'have_result': True,
            'candidates': get_commune_candidate_result(commune)
        }
    else:
        commune_candidates_result = {
            'have_result': False,
            'candidates': []
        }
        candidats = candidates_schema.dump(commune.wilaya.candidates.all())
        for candidat in candidats:
            obj = {
                "candidate_id": candidat['id'],
                "candidate_last_name": candidat['last_name'],
                "candidate_name": candidat['first_name'],
                "candidate_result": None
            }
            commune_candidates_result['candidates'].append(obj)
    
    if commune.parties_result.first() is not None:
        commune_parties_result = {
            'have_result': True,
            'parties': get_commune_partie_result(commune)
        }
    else:
        commune_parties_result = {
            'have_result': False,
            'parties': []
        }
        parties = parties_schema.dump(commune.wilaya.parties.all())
        for partie in parties:
            obj = {
                "partie_id": partie['id'],
                "partie_name": partie['name'],
                "partie_result": None
            }
            commune_parties_result['parties'].append(obj)
    
    
    return jsonify({
            'commune_result': commune_result,
            'commune_candidate_result': commune_candidates_result,
            'commune_partie_result': commune_parties_result
        })
    

@wilaya_reporter.route('/wilaya_reporter/<int:code>/result', methods=['GET'])
@token_required
def wilaya_reporter_result(current_user,code):
    wilaya=db.session.query(Wilaya).filter_by(code=code).first()
    #commune=db.session.query(Commune).filter_by(ons_code=ons_code).first()
    if wilaya is None:
        return jsonify({'message':'wilaya not found','success':False})
    communes=wilaya.commune
    if communes.first() is None:
        return jsonify({'message':'wilaya have no commune ','success':False})
    wilaya_communes_result=[]
    wilaya_candidates_result=[]
    wilaya_parties_result=[]
    for commune in communes:    
        if commune.results.first() is None:
            commune_result={
                'commune': {
                'id': commune.id,
                'name': commune.name,
                'ons_code': commune.ons_code,
                'number_of_voting_offices': None,
                'number_of_registrants': None,
                'number_of_cards_canceled': None,
                'number_of_voters_received': None,
                'number_of_disputed_cards':None,
                'number_of_voters': None,
                'reporter_first_name': commune.user.first_name,
                'reporter_last_name': commune.user.last_name,
                'reporter_phone_number':commune.user.phone_number,
                'reporter_id': commune.user_id,
                'result_date': None},
            'have_result':False
            }
            wilaya_communes_result.append(commune_result)
        else:
            commune_result=get_commune_result(commune)
            wilaya_communes_result.append(commune_result)
        
        if commune.candidates_result.first() is not None:
            commune_candidates_result = get_commune_candidate_result(commune)
            wilaya_candidates_result.append(commune_candidates_result)
        else:
            commune_candidates_result={
                'have_result':False,
                'candidates':candidates_schema.dump(commune.wilaya.candidates.all()) 
            
            }
            wilaya_candidates_result.append(commune_candidates_result)
        
        if commune.parties_result.first() is not None:
            commune_parties_result=get_commune_partie_result(commune)
            wilaya_parties_result.append(commune_parties_result)
        else:
            commune_parties_result={
                'have_result':False,
                'parties':parties_schema.dump(commune.wilaya.parties.all()) 
                
            }
            wilaya_parties_result.append(commune_parties_result)
    
    
    return jsonify({
            'commune_result':commune_result,
            'commune_candidate_result':commune_candidates_result,
            'commune_partie_result':commune_parties_result
            
        })
    

    
    
