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

