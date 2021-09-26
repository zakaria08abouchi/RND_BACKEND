import jwt
import uuid
from flask import Blueprint
from flask import request, jsonify, make_response
from flask_cors import CORS
from functools import wraps
from rnd_api import app
from rnd_api import db
from rnd_api.models import (Commune, GlobalResult,
                            Wilaya, Partie)

from rnd_api.util import token_required

from rnd_api import db

def get_voters_received_less_than_5(wilaya):
    voters_received_less_than_5 = 0
    wilaya_parties_result=get_wilaya_parties_result(wilaya,wilaya.parties,wilaya.commune)

    for partie_result in wilaya_parties_result:
        if float(partie_result['partie_wilaya_purcentage']) < 5:
            
            voters_received_less_than_5 += int(partie_result['partie_result'])
    
    return voters_received_less_than_5
        

def get_wilaya_global_result(communes):
   
    communes_results = []
    if communes.first() is not None:
       
        wilaya_number_of_registrants = 0
        wilaya_number_of_voters = 0
        wilaya_number_of_cards_canceled = 0
        wilaya_number_of_voters_received = 0
        wilaya_number_of_disputed_cards = 0
        wilaya_number_of_voting_offices=0
        for commune in communes:
            if commune.number_of_voting_offices:
                number_of_voting_offices=commune.number_of_voting_offices
            else:
                number_of_voting_offices=0

            if commune.number_of_registrants:
                number_of_registrants=commune.number_of_registrants
            else:
                number_of_registrants=0
            #print(f'length{len(commune.results.all())}/n')
            commune_result = commune.results
            if commune_result.first() is not None:
                communes_results.append({
                    'name': commune.name,
                    'ons_code': commune.ons_code,
                    'number_of_voting_offices': int(number_of_voting_offices),
                    'number_of_registrants': int(number_of_registrants),                                 
                    'number_of_voters': int(commune_result[-1].number_of_voters),
                    'number_of_cards_canceled': int(commune_result[-1].number_of_cards_canceled),
                    'number_of_voters_received': int(commune_result[-1].number_of_voters_received),
                    'number_of_disputed_cards': int(commune_result[-1].number_of_disputed_cards),
                    'reporter_id': commune_result[-1].user_id
                    #'commune_id': commune_result[-1].commune_id
                                        })
                wilaya_number_of_voting_offices += int(number_of_registrants)
                wilaya_number_of_registrants += int(number_of_registrants)
                wilaya_number_of_voters += int(commune_result[-1].number_of_voters)
                wilaya_number_of_cards_canceled += int(commune_result[-1].number_of_cards_canceled)
                wilaya_number_of_voters_received += int(commune_result[-1].number_of_voters_received)
                wilaya_number_of_disputed_cards += int(commune_result[-1].number_of_disputed_cards)
               
                
            else:
                communes_results.append({
                    'name': commune.name,
                    'ons_code': commune.ons_code,
                    'number_of_voting_offices': int(number_of_voting_offices),
                    'number_of_registrants': int(number_of_registrants),                                 
                    'number_of_voters': None,
                    'number_of_cards_canceled': None,
                    'number_of_voters_received': None,
                    'number_of_disputed_cards': None,
                    'reporter_id': None,
                    'commune_id': None
                                            })
                wilaya_number_of_voting_offices += int(number_of_registrants)
                wilaya_number_of_registrants += int(number_of_registrants)

        wilaya_global_result = {
            'wilaya_number_of_voting_offices': wilaya_number_of_voting_offices,
            'wilaya_number_of_registrants': wilaya_number_of_registrants,
            'wilaya_number_of_voters': wilaya_number_of_voters,
            'wilaya_number_of_cards_canceled': wilaya_number_of_cards_canceled,
            'wilaya_number_of_voters_received': wilaya_number_of_voters_received,
            'wilaya_number_of_disputed_cards': wilaya_number_of_disputed_cards,
            'wilaya_code': communes.first().wilaya.code,
            'wilaya_name': communes.first().wilaya.name,
            'wilaya_have_result':True
                                }
                            
    return wilaya_global_result


#return number of voters received for wilaya and commune ------------------------------------------------
def get_number_of_veters_received_wilaya(code):
    wilaya=db.session.query(Wilaya).filter_by(code=code).first()
    communes=wilaya.commune
    number_of_voters_received=0
    for commune in communes:
        if commune.results.first() is not None:
            number_of_voters_received+=commune.results[-1].number_of_voters_received
        else:
            number_of_voters_received+=0
    return int(number_of_voters_received)

def get_number_of_veters_received_commune(ons_code):
    commune=db.session.query(Commune).filter_by(ons_code=ons_code).first()
    return int(commune.results[-1].number_of_voters_received)


def get_wilaya_parties_result(wilaya,parties,communes):
    wilaya_communes_parties_result=[]

    #commune------------------------------
    for commune in communes:
        commune_results=commune.parties_result
        partie_results=[]
        commune_parties_result=[]

        if commune_results.first() is not None:

            for partie in parties:
                for result in commune_results:
                    if result.partie_id == partie.id:
                            partie_results.append(result)
                if partie_results[-1].commune.results.first() is not None:
                    commune_parties_result.append({
                        'commune_ons_code':int(partie_results[-1].commune_ons_code),
                        'partie_id':int(partie_results[-1].partie_id),
                        'partie_result':int(partie_results[-1].result),
                        'reporter_id':int(partie_results[-1].user_id),
                        'partie_name':partie_results[-1].partie.name,
                        'post':partie_results[-1].post,
                        #'ons_code':commune.ons_code,
                        #'wilaya_name':commune.wilaya.name,
                        #'wilaya_code':commune.wilaya.code,
                        'partie_commune_purcentage':round(float(partie_results[-1].result/get_number_of_veters_received_commune(commune.ons_code) )*100,2),
                        })
                    partie_results=[]
                else:
                    commune_parties_result.append({
                        'commune_ons_code':int(partie_results[-1].commune_ons_code),
                        'partie_id':int(partie_results[-1].partie_id),
                        'partie_result':int(partie_results[-1].result),
                        'reporter_id':int(partie_results[-1].user_id),
                        'partie_name':partie_results[-1].partie.name,
                        'post':partie_results[-1].post,
                        #'ons_code':commune.ons_code,
                        #'wilaya_name':commune.wilaya.name,
                        #'wilaya_code':commune.wilaya.code,
                        'partie_commune_purcentage':None,
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
            if commune.user:
                reporter_id=commune.user.id
            else:
                reporter_id=None
            
            commune_parties_result=[]
            commune_parties_result.append({
                    'commune_ons_code':commune.ons_code,
                    'partie_id':None,
                    'partie_result':None,
                    'reporter_id':reporter_id,
                    'partie_name':None,
                    'post':None
                    #'ons_code':commune.ons_code,
                    #'wilaya_name':commune.wilaya.name,s
                    #'wilaya_code':commune.wilaya.code
                    })
            
            wilaya_communes_parties_result.append({
                'commune_ons_code':commune.ons_code,
                'commune_name':commune.name,
                'commune_have_result':False,
                'commune_parties_result':commune_parties_result
            })
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
    
    return wilaya_parties_result


def get_wilaya_partie_result(code):
    wilaya = db.session.query(Wilaya).filter_by(code=code).first()
    """ if not wilaya:
        return jsonify({'message': 'wilaya not found', 'success': False})
    communes = wilaya.commune
    if not communes:
        return jsonify({'message':'wilaya have no commune','success':False})
    """
    communes = wilaya.commune
    parties=wilaya.parties
    if parties.first() is None:
        return jsonify({'message':'wilaya have no parties','success':False})
    wilaya_communes_parties_result=[]

    #commune------------------------------
    for commune in communes:
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
                    'reporter_phone_number': commune.user.phone_number,
                    'reporter_first_name': commune.user.first_name,
                    'reporter_last_name': commune.user.last_name
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
                    'reporter_id':int(commune.user_id),
                    'partie_name':None,
                    'post':None
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
            
            commune_parties_result=[]
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
            
            'partie_result': partie_result,
            'wilaya_name':wilaya.name
            
        })

    return jsonify({'wilaya_result':
                     wilaya_parties_result,
                    
                  })