from rnd_api.models import Wilaya, Commune, GlobalResult
from rnd_api import db

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

def get_commune_result(commune):
    commune_result = commune.results[-1]
    return {
        'commune': {
            'id': commune.id,
            'name': commune.name,
            'ons_code': commune.ons_code,
            'number_of_voting_offices': commune.number_of_voting_offices,
            'number_of_registrants': commune.number_of_registrants,
            'number_of_cards_canceled': commune.results[-1].number_of_cards_canceled,
            'number_of_voters_received': commune.results[-1].number_of_voters_received,
            'number_of_disputed_cards': commune.results[-1].number_of_disputed_cards,
            'number_of_voters': commune.results[-1].number_of_voters,
            'reporter_first_name': commune.results[-1].user.first_name,
            'reporter_last_name': commune.results[-1].user.last_name,
            'reporter_id': commune.results[-1].user.id,
            'reporter_phone_number':commune.user.phone_number,
            'result_date': commune.results[-1].date_created},
        'have_result':True
                        }

def get_commune_candidate_result(commune):

    wilaya = db.session.query(Wilaya).filter_by(code=commune.wilaya.code).first()
    candidates = wilaya.candidates
    commune_results = commune.candidates_result
    candidate_result = []
    candidate_final_result = []
    
    for candidate in candidates:
        for result in commune_results:
            if result.candidate.id == candidate.id:
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
            'have_result':True,
            'candidate_purcentage': float(
                candidate_result[-1].result / get_number_of_veters_received_commune(commune.ons_code)) * 100
        })
        candidate_result = []
    return candidate_final_result

def get_commune_partie_result(commune):

    wilaya = db.session.query(Wilaya).filter_by(code=commune.wilaya.code).first()
    parties = wilaya.parties
    commune_results = commune.parties_result
    partie_results = []
    commune_parties_result = []
    for partie in parties:
        for result in commune_results:
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
            'have_result':True,
            'partie_purcentage': float(
                partie_results[-1].result / get_number_of_veters_received_commune(commune.ons_code)) * 100
        })
        partie_results = []
    return commune_parties_result

