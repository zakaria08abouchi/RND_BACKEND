from rnd_api import ma


class WilayaSchema(ma.Schema):
    class Meta:
        fields = ('code', 'name', 'id', 'user_wilaya_id', 'number_of_places')


class CommuneSchema(ma.Schema):
    class Meta:
        fields = ('name', 'user_id', 'ons_code', 'number_of_voting_offices', 'number_of_registrants', 'id')

class UserSchema(ma.Schema):
    class Meta:
        fields=('first_name', 'last_name', 'phone_number', 'post', 'public_id', 'id')

class ReporterSchema(ma.Schema):
    class Meta:
        fields = ('first_name', 'last_name', 'phone_number', 'post', 'public_id', 'id')


class ReporterWilayaSchema(ma.Schema):
    class Meta:
        fields = ('first_name', 'last_name', 'phone_number', 'post', 'public_id', 'id')


class GlobalResultSchema(ma.Schema):
    class Meta:
        fields = ('user_id', 'commune_id', 'number_of_voters', 'number_of_cards_canceled', 'number_of_voters_received',
                  'number_of_disputed_cards')


class CandidateSchema(ma.Schema):
    class Meta:
        fields = ('first_name', 'last_name', 'id', 'wilaya_code')


class PartieSchema(ma.Schema):
    class Meta:
        fields = ('id', 'wilaya_code', 'name')


class CandidateResultSchema(ma.Schema):
    class Meta:
        fields = ('result', 'id')


class PartieResultSchema(ma.Schema):
    class Meta:
        fields = ('result', 'id')


class ElectionSchema(ma.Schema):
    class Meta:
        fields = ('name', 'date')

# init schema
