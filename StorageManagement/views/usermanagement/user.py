from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from models.User_Management.user import User


#TODO: Authenticate all database queries. Authenticate the source making those queries first
# Remember that soeone can easily sniff out information sent between the services so password based authentication
# might not be the best.

bp = Blueprint('user', __name__)

@bp.route('/create_user', methods=['POST'], strict_slashes=False)
def create_user():
    email = request.form.get('email', None)
    first_name = request.form.get('first_name', None)
    last_name = request.form.get('last_name', None)
    password = request.form.get('password', None)
    profile_pic = request.files.get('profile_pic', None)
    new_user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        profile_pic=profile_pic,
        password=password
    )
    new_user.save()
    return jsonify({"msg": "The user has been created successfully"}), 201

@bp.route('/user/<user_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_user(user_id):
    """ Get a particular user based on an id"""
    user = User.search(id=user_id)
    if user is None:
        return jsonify({"msg": "User not found"}), 404
    return jsonify(user[0].to_dict())

@bp.route('/user/email/<user_email>', methods=['GET'], strict_slashes=False)
def get_user_by_email(user_email):
    """ Get a particular user based on their email"""
    user = User.search(email=user_email)
    if user is None:
        return jsonify({"msg": "User not found"}), 404
    return jsonify(user[0].to_dict())

@bp.route('/users', methods=['GET'], strict_slashes=False)
def get_all_users():
    users = User.all()
    if len(users) == 0:
        return jsonify({'msg': "No users found"}), 404
    list_of_users = []
    for user in users:
        list_of_users.append(user.to_dict())
    return jsonify(list_of_users), 200