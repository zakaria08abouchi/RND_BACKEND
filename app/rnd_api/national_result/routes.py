import datetime
import jwt
import uuid
from flask import Blueprint
from flask import request, jsonify, make_response
from flask_cors import CORS
from functools import wraps
from rnd_api import app
from rnd_api import db
from rnd_api.models import User, GlobalResult, Commune, Wilaya
from rnd_api.schema import ReporterSchema, ReporterWilayaSchema, CommuneSchema, WilayaSchema
from rnd_api.util import token_required
from .util import (get_wilaya_global_result, get_number_of_veters_received_commune,
get_number_of_veters_received_wilaya,get_wilaya_parties_result,get_voters_received_less_than_5,
get_wilaya_partie_result)


national = Blueprint('national', __name__, url_prefix='/api')
cors = CORS(national)

@national.route('/national/result', methods=['GET'])
def national_result():
    if request.method=='GET':
        wilayas=db.session.query(Wilaya).all()
        if not wilayas:
            return jsonify({'message':'no wilaya found', 'success':False})
        national_global_result=[]
        national_rnd_result=[]
        #voters_received=get_number_of_veters_received_wilaya(wilaya.code)
        
        #---------------------------------------------
       
        #--------------------------------------------
        for wilaya in wilayas:
            parties=wilaya.parties           
            communes=wilaya.commune

            voters_received = get_number_of_veters_received_wilaya(wilaya.code)
            voters_received_less_than_5 = get_voters_received_less_than_5(wilaya)
            electoral_factor = int((voters_received - voters_received_less_than_5)/wilaya.number_of_places)

            if communes.first() is not None:
                #print("#")
                #national_rnd_result.append(get_wilaya_partie_result(wilaya.code))
                #print(get_wilaya_partie_result(wilaya.code))
                
                wilaya_result=get_wilaya_global_result(communes)
                #print("#####")
                national_global_result.append({
                    'wilaya_number_of_voting_offices': wilaya_result['wilaya_number_of_voting_offices'],
                    'wilaya_number_of_registrants': wilaya_result['wilaya_number_of_registrants'],
                    'wilaya_number_of_voters': wilaya_result['wilaya_number_of_voters'],
                    'wilaya_number_of_cards_canceled': wilaya_result['wilaya_number_of_cards_canceled'],
                    'wilaya_number_of_voters_received': wilaya_result['wilaya_number_of_voters_received'],
                    'wilaya_number_of_disputed_cards': wilaya_result['wilaya_number_of_disputed_cards'],
                    'wilaya_code': wilaya.code,
                    'wilaya_name': wilaya.name,
                    'number_of_place':wilaya.number_of_places,
                    'number_of_commune':len(communes.all()),
                    'number_of_parties':len(wilaya.parties.all()),
                    'electoral_factor':electoral_factor,
                    'voters_received_less_than_5':voters_received_less_than_5,
                    'participation_rate':round(float(wilaya_result['wilaya_number_of_voters'] / wilaya_result['wilaya_number_of_registrants'])*100,2),
                    #'electoral_factor':
                    'wilaya_have_result':True
                })
            else:
                national_global_result.append({
                    'wilaya_number_of_voting_offices': None,
                    'wilaya_number_of_registrants': None,
                    'wilaya_number_of_voters': None,
                    'wilaya_number_of_cards_canceled': None,
                    'wilaya_number_of_voters_received': None,
                    'wilaya_number_of_disputed_cards': None,
                    'wilaya_code': wilaya.code,
                    'number_of_parties':None,
                    'wilaya_name': wilaya.name,
                    'number_of_place':wilaya.number_of_places,
                    'number_of_commune':None,
                    'participation_rate':None,
                    'wilaya_have_result':False
                })
        return jsonify({'nationa_global_result':national_global_result,
        'nationa_rnd_result':national_rnd_result})

        