from rnd_api import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# creating models
# start User Model---------------------------------------------

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone_number = db.Column(db.String(12), unique=True)
    post = db.Column(db.String(50))
    password = db.Column(db.String(500))
    admin = db.Column(db.Boolean)

    commune = db.relationship('Commune', backref='user', uselist=False)
    results = db.relationship('GlobalResult', backref='user', lazy=True)
    candidates_results = db.relationship('CandidateResult', backref='user', lazy=True)
    parties_results = db.relationship('PartieResult', backref='user', lazy=True)
    wilaya = db.relationship('Wilaya', backref='user', uselist=False)

    def generate_password(self):
        return self.first_name[1] + self.last_name[1] + str( (int(self.phone_number[3:6]) * 11 ) ) + self.first_name[1] + self.last_name[1]

    def __init__(self, public_id, first_name, last_name, phone_number, post,password,with_id,id):
        if not with_id:
            self.public_id = public_id
            self.name = last_name + ' ' + first_name
            self.first_name = first_name
            self.last_name = last_name
            self.phone_number = phone_number
            self.post = post
            self.admin = False
            self.password = generate_password_hash(password)
            #self.password=generate_password_hash("admin")
        else:
            self.id=id
            self.public_id = public_id
            self.name = last_name + ' ' + first_name
            self.first_name = first_name
            self.last_name = last_name
            self.phone_number = phone_number
            self.post = post
            self.admin = False
            self.password = generate_password_hash(password)
   
    
    

    def __repr__(self):
        return f'<User {self.name}>'


# end User Model--------------------------------------------------

# start Wilaya Model--------------------------------------------------
class Wilaya(db.Model):
    __tablename__ = 'wilaya'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    commune = db.relationship('Commune', backref='wilaya', lazy='dynamic')
    candidates = db.relationship('Candidate', backref='wilaya', lazy='dynamic')
    parties = db.relationship('Partie', backref='wilaya', lazy='dynamic')
    # reporter_id=db.Column(db.Integer, db.ForeignKey('reporter.id', ondelete='CASCADE'), unique=True)
    user_wilaya_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True)
    number_of_places = db.Column(db.Integer)
    
    def __init__(self, code, name,user_wilaya_id,number_of_places):
        self.code = code
        self.name = name
        self.user_wilaya_id = user_wilaya_id
        self.number_of_places = number_of_places


    def __repr__(self):
        return f'<Wilaya {self.name}>'


# end Wilaya Model--------------------------------------------------

# start Commune Model---------------------------------------------
class Commune(db.Model):
    __tablename__ = 'commune'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    ons_code = db.Column(db.Integer, unique=True)
    number_of_voting_offices = db.Column(db.Integer)
    number_of_registrants = db.Column(db.Integer)
    wilaya_code = db.Column(db.Integer, db.ForeignKey('wilaya.code', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True)
    results = db.relationship('GlobalResult', backref='commune', lazy='dynamic')
    candidates_result = db.relationship('CandidateResult', backref='commune', lazy='dynamic')
    parties_result = db.relationship('PartieResult', backref='commune', lazy='dynamic')

    def __init__(self, name, ons_code, number_of_voting_offices, number_of_registrants, user_id, wilaya_code):
        self.name = name
        self.ons_code = ons_code
        self.number_of_voting_offices = number_of_voting_offices
        self.number_of_registrants = number_of_registrants
        self.user_id = user_id
        self.wilaya_code = wilaya_code

    def __repr__(self):
        return f'<Cummune {self.name}>'


# end Commune Model--------------------------------------------------

# start GlobalResult Model---------------------------------------------
class GlobalResult(db.Model):
    __tablename__ = 'global_result'

    id = db.Column(db.Integer, primary_key=True)
    number_of_voters = db.Column(db.Integer)
    number_of_cards_canceled = db.Column(db.Integer)
    number_of_voters_received = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    number_of_disputed_cards = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    commune_ons_code = db.Column(db.Integer, db.ForeignKey('commune.ons_code', ondelete='CASCADE'))
    status = db.Column(db.Boolean, default=False)
    post = db.Column(db.String(10))

    def __init__(self, number_of_voters, number_of_cards_canceled, number_of_voters_received, number_of_disputed_cards,
                 user_id, commune_ons_code, post):
        self.number_of_voters = number_of_voters
        self.number_of_cards_canceled = number_of_cards_canceled
        self.number_of_voters_received = number_of_voters_received
        self.number_of_disputed_cards = number_of_disputed_cards
        self.user_id = user_id
        self.commune_ons_code = commune_ons_code
        self.post=post
        self.status=True

    def __repr__(self):
        return f'<Results for{self.commune.name}>'


# end GlobalResult Model---------------------------------------------

# start Candidate Model---------------------------------------------
class Candidate(db.Model):
    __tablename__ = 'candidate'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    wilaya_code = db.Column(db.Integer, db.ForeignKey('wilaya.code', ondelete='CASCADE'))
    results = db.relationship('CandidateResult', backref='candidate', lazy=True)

    def __init__(self, first_name, last_name, wilaya_code):
        self.first_name = first_name
        self.last_name = last_name
        self.wilaya_code = wilaya_code

    def __repr__(self):
        return f'<Candidate : {self.first_name} {self.last_name} >'


# end Candidate Model---------------------------------------------
# start CandidateResult Model---------------------------------------------
class CandidateResult(db.Model):
    __tablename__ = 'candidate_result'

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    result = db.Column(db.Integer)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id', ondelete='CASCADE'))
    status = db.Column(db.Boolean, default=False)
    commune_ons_code = db.Column(db.Integer, db.ForeignKey('commune.ons_code', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    post = db.Column(db.String(10))

    def __init__(self, result, candidate_id,commune_ons_code,user_id,post):
        self.result = result
        self.candidate_id = candidate_id
        self.status=True
        self.commune_ons_code=commune_ons_code
        self.user_id=user_id
        self.post=post

    def __repr__(self):
        return f'<CandidateResult : {self.result} >'


# end CandidateResult Model---------------------------------------------

# start Partie Model---------------------------------------------
class Partie(db.Model):
    __tablename__ = 'partie'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    code=db.Column(db.Integer)
    wilaya_code = db.Column(db.Integer, db.ForeignKey('wilaya.code', ondelete='CASCADE'))
    results = db.relationship('PartieResult', backref='partie', lazy=True)


    def __init__(self, name, wilaya_code, code):
        self.name = name
        self.wilaya_code = wilaya_code
        self.code=code

    def __repr__(self):
        return f'<Partie : {self.name} >'


# end Partie Model---------------------------------------------



# start PartieResult Model---------------------------------------------
class PartieResult(db.Model):
    __tablename__ = 'partie_result'

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    result = db.Column(db.Integer)
    partie_id = db.Column(db.Integer, db.ForeignKey('partie.id', ondelete='CASCADE'))
    status = db.Column(db.Boolean, default=False)
    commune_ons_code = db.Column(db.Integer, db.ForeignKey('commune.ons_code', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    post = db.Column(db.String(10))

    def __init__(self, result,partie_id,commune_ons_code, user_id,post):
        self.result = result
        self.partie_id=partie_id
        self.status=True
        self.user_id=user_id
        self.commune_ons_code=commune_ons_code
        self.post=post

    def __repr__(self):
        return f'<PartieResult : {self.result} >'


# end PartieResult Model---------------------------------------------

# start Election Model-------------------------------------------------
class Election(db.Model):
    __tablename__ = 'election'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    date = db.Column(db.Date)

    def __init__(self, name, date):
        self.name = name
        self.date = date

    def __repr__(self):
        return f'<Election : {self.name} >'
