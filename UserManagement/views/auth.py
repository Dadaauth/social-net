from flask import Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask import request, jsonify
import requests


bp = Blueprint('auth', __name__)

storage_service_url = "http://127.0.0.1:5001/api/v1.0/storagemanagement/"
storage_service_url_production = "https://socialnet.clementauthority.me/api/v1.0/storagemanagement/"

@bp.route('/login', methods=['POST'], strict_slashes=False)
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    if email is None or password is None:
        return jsonify({'msg': 'missing email or password'}), 400
    users = requests.get(f'{storage_service_url}/usermanagement/users')
    if users.status_code == 404:
        return jsonify({"msg": "No users in storage"}), 404
    for user in users.json():
        if user.get("email") == email and user.get("password") == password:
            access_token = create_access_token(identity=user)
            return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad username or password!"}), 401


@bp.route('/signup', methods=['POST'], strict_slashes=False)
def signup():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    if email is None or password is None:
        return jsonify({"msg": "Missing email or password!"}), 400
    # check if the user exists before creating the user.
    response = requests.post(f'{storage_service_url}/usermanagement/create_user', json=request.json)
    return jsonify(response.json()), 201

@bp.route('/current_user', methods=['GET'], strict_slashes=False)
@jwt_required()
def user():
    current_user = get_jwt_identity()
    return jsonify(user=current_user), 200


@bp.route('/logout', methods=['GET'], strict_slashes=False)
@jwt_required()
def logout():
    pass