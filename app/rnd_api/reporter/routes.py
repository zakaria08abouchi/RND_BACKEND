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
from rnd_api.models import User, GlobalResult, Commune, Wilaya
from rnd_api.schema import ReporterSchema, ReporterWilayaSchema, CommuneSchema, WilayaSchema
from rnd_api.util import token_required

reporters = Blueprint('reporters', __name__, url_prefix='/api')
cors = CORS(reporters)

commune_schema = CommuneSchema()
wilaya_schema = WilayaSchema()

# verbs implementation for reporter routes-----------------------------------------------------------------
reporter_schema = ReporterSchema()
reporters_schema = ReporterSchema(many=True)


@reporters.route('/reporter', methods=['GET'])
@token_required
def reporter(current_user):
    reporters = None
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!', 'success': False})
    if request.method == 'GET':

        reporter_results = []
        users = User.query.all()
        if users:
            for reporter in users:
                if reporter.post == 'reporter':
                    reporter_object = {
                        'id': reporter.id,
                        'public_id': reporter.public_id,
                        'first_name': reporter.first_name,
                        'last_name': reporter.last_name,
                        'phone_number': reporter.phone_number,
                        'post': reporter.post,
                        'commune': commune_schema.dump(db.session.query(Commune).get(reporter.commune.id)),
                    }
                    reporter_results.append(reporter_object)

            # results = reporters_schema.dump(reporters)
            return jsonify({'count': len(reporter_results), 'reporters': reporter_results, 'success': True})
        else:
            return jsonify({'message': 'no reporters are found', 'success': False})


@reporters.route('/reporter/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def handle_reporter(current_user, id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!','success': False})
    reporter = User.query.get(id)
    if not reporter:
        return jsonify({'message': 'reporter not found','success': False})
    if request.method == 'GET':
        if reporter.post == 'reporter':
            return jsonify({'reporter': reporter_schema.dump(reporter), 'success': True})
        else:
            return jsonify({'message': 'reporter not found', 'success': False})
    elif request.method == 'PUT':
        if request.is_json:
            data = request.get_json()
            reporter.name = data['last_name'] + ' ' + data['first_name']
            reporter.first_name = data['first_name']
            reporter.last_name = data['last_name']
            reporter.phone_number = data['phone_number']
            if data['commune']:
                reporter.commune = data['commune']
            db.session.add(reporter)
            db.session.commit()
            return jsonify({'message': f'reporter {reporter.name} has been updated successfully.', 'success': True})
    elif request.method == 'DELETE':
        db.session.delete(reporter)
        db.session.commit()
        return jsonify({"message": f"reporter {reporter.name} successfully deleted.", 'success': True})


# verbs implementation for reporter wilaya routes-----------------------------------------------------------------
reporter_wilaya_schema = ReporterWilayaSchema()
reporters_wilaya_schema = ReporterWilayaSchema(many=True)


@reporters.route('/reporter_wilaya', methods=['GET'])
@token_required
def reporter_wilaya(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!', 'success': False})

    reporters = User.query.all()
    if reporters:
        if reporter.post == 'reporter_wilaya':
            results = reporters_wilaya_schema.dump(reporters)
            return jsonify({'count': len(results), 'result': results, 'success': True})
    else:
        return jsonify({'message': 'no wilaya reporters are found', 'success': False})


@reporters.route('/reporter_wilaya/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def handle_reporter_wilaya(current_user, id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!', 'success': False})
    reporter = User.query.get(id)
    if not reporter:
        return jsonify({'message': 'wilaya reporter not found', 'success': False})
    if request.method == 'GET':
        if reporter.post == 'reporter_wilaya':
            return jsonify({'reporter': reporter_wilaya_schema.dump(reporter)})
        else:
            return jsonify({'message': 'wilaya reporter not found'})
    elif request.method == 'PUT':
        if request.is_json:
            data = request.get_json()
            reporter.name = data['last_name'] + ' ' + data['first_name']
            reporter.first_name = data['first_name']
            reporter.last_name = data['last_name']
            reporter.phone_number = data['phone_number']
            if data['wilaya']:
                reporter.wilaya = data['wilaya']
            db.session.add(reporter)
            db.session.commit()
            return jsonify({'message': f'wilaya reporter {reporter.name} has been updated successfully.', 'success': True})
    elif request.method == 'DELETE':
        db.session.delete(reporter)
        db.session.commit()
        return jsonify({"message": f"reporter {reporter.name} successfully deleted.", 'success': True})

# end -------------------------------------------------------------------------------------------------
