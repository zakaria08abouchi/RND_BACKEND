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
from .util import (get_wilaya_parties_result, get_wilaya_global_result,
get_number_of_veters_received_wilaya,sort,get_number_of_veters_received_commune)

statistics = Blueprint('statistics', __name__, url_prefix='/api')
cors = CORS(statistics)

@statistics.route('/wilaya/<int:code>/statistic',methods=['GET'])
@token_required
def statistic(current_user,code):
    if request.method == 'GET':
        wilaya=db.session.query(Wilaya).filter_by(code=code).first()
        if wilaya is None:
            return jsonify({'message':'wilaya not found','success':False})
        communes=wilaya.commune
        if communes.first() is None:
            return jsonify({'message':'wilaya have no commune.','success':False})
        
        parties=wilaya.parties
        if parties.first() is None:
            return jsonify({'message':'wilaya have no parties'})
        
        
        # get parties who's have pourcentage less than 5% and calculate factor ----------------------------------------
        wilaya_parties_result=get_wilaya_parties_result(wilaya,parties,communes)
        #return jsonify(wilaya_parties_result)
        voters_received_less_than_5 = 0
        parties_result_list_less_than=[]   # contain partie < 5 %
        parties_result_list_greather_than=[]
        voters_received_modif=0
        for partie_result in wilaya_parties_result:
            if float(partie_result['partie_wilaya_purcentage']) < 5:
                parties_result_list_less_than.append(partie_result)
                voters_received_less_than_5 += int(partie_result['partie_result'])
                voters_received_modif+=int(partie_result['partie_result'])
            else:
                parties_result_list_greather_than.append(partie_result)
                voters_received_modif+=int(partie_result['partie_result'])
        
        number_of_place=wilaya.number_of_places
        voters_received=get_number_of_veters_received_wilaya(wilaya.code) # modified
        if number_of_place > 0:
            electoral_factor = int((voters_received_modif - voters_received_less_than_5)/number_of_place)
        else:
            return jsonify({'message':'number of place wilaya less than zero.',
                            'success':False})
        
        #---------------- Seat distribution  over partie ----------------------------------------
        partie_result_seat=[]
        partie_seat=[]
        partie_have_not_factor=[]
        number_of_place_occupied=0
        for partie in parties_result_list_greather_than:
            if int(partie['partie_result']) >= electoral_factor:
                partie_number_of_place = int( int(partie['partie_result'])/electoral_factor )
                partie_number_of_voters_rest= int(partie['partie_result']) % electoral_factor
                number_of_place_occupied+=partie_number_of_place
                partie_result_seat.append({
                    'partie_number_of_place':partie_number_of_place,
                    'partie_number_of_voters_rest':partie_number_of_voters_rest,
                    'partie_result':partie['partie_result'],
                    'partie_name':partie['partie_name'],
                    'partie_id':partie['partie_id']

                })
                partie_seat.append({
                    'partie_number_of_place':partie_number_of_place,
                    'partie_number_of_voters_rest':partie_number_of_voters_rest,
                    'partie_result':partie['partie_result'],
                    'partie_name':partie['partie_name'],
                    'partie_id':partie['partie_id']

                })
            else:
                partie_result_seat.append({
                    'partie_number_of_place':0,
                    'partie_number_of_voters_rest':int(partie['partie_result']),
                    'partie_result':partie['partie_result'],
                    'partie_name':partie['partie_name'],
                    'partie_id':partie['partie_id']

                })
                partie_seat.append({
                    'partie_number_of_place':0,
                    'partie_number_of_voters_rest':int(partie['partie_result']),
                    'partie_result':partie['partie_result'],
                    'partie_name':partie['partie_name'],
                    'partie_id':partie['partie_id']

                })
                #partie_have_not_factor.append(partie)

        #---------------------Seat distribution (the rest base for the strongest)-------------------
        #sorted_parties=dict(sorted(partie_result_seat.items(), key=lambda item: item[1]))
        #number_of_place_rested
        #partie_seat=partie_result_seat
        partie_result_seat_sorted=sort(partie_result_seat)
        #return jsonify(partie_seat)
        rest_place= number_of_place-number_of_place_occupied
        partie_rest_seat=[]
        partie_of_number_place_rest=0
        if rest_place > 0:
            
            for partie in partie_result_seat_sorted:
                if rest_place > 0 :
                    if partie['partie_number_of_voters_rest'] > 0:
                        partie['partie_of_number_place_rest'] = int(partie_of_number_place_rest + 1)
                        partie_rest_seat.append(partie)
                        rest_place = rest_place - 1
                    else:
                        partie['partie_of_number_place_rest'] = 0
                        partie_rest_seat.append(partie)
                else:
                    partie['partie_of_number_place_rest'] = 0
                    partie_rest_seat.append(partie)

        
        
        

        #return jsonify(partie_result_seat_sorted)
        
        return jsonify({'partie_less_than':parties_result_list_less_than, 
        'partie_greather_than':parties_result_list_greather_than,
        #'partie_have_not_factor':partie_have_not_factor,
        'voters_received_less_than_5':voters_received_less_than_5,
        'electoral_factor':electoral_factor,
        'partie_seat_number':partie_seat,
        'partie_sort':partie_result_seat_sorted,
        'partie_rest_seat':partie_rest_seat,
        'number_of_voters_received':voters_received_modif,     #modified
        #'number_of_voters_received_less_than':voters_received_less_than_5,
        'number_of_place':number_of_place,
        'wilaya_name':wilaya.name,
        'wilaya_code':wilaya.code,
        'success':True})
    
    
