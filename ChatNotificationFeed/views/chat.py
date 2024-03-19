from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
import requests

bp = Blueprint('chat', __name__)

storage_service_url = "http://127.0.0.1:5001/api/v1.0/storagemanagement/"
storage_service_url_production = "https://socialnet.clementauthority.me/api/v1.0/storagemanagement/"


@bp.route('/create_message', methods=["POST"], strict_slashes=False)
@jwt_required()
def create_message():
    sender_id = request.form.get('sender_id')
    conversation_id = request.form.get('conversation_id')
    content = request.form.get('content', None)
    image = request.files.get('image', None)
    video = request.files.get('video', None)

    # Check that the sender_id belongs to an actual user
    # in storage
    response = requests.post(
        f"{storage_service_url}/contentmanagement/chat/create_message",
        data={
            "sender_id": sender_id,
            "conversation_id": conversation_id,
            "content": content,
        },
        files={
            "image": image,
            "video": video
        },
        headers={"Authorization": request.headers.get('Authorization')}
    )
    return jsonify(response.json()), response.status_code

@bp.route('/create_conversation', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_conversation():
    name = request.json.get('name', None)
    participants = request.json.get('participants', None)
    response = requests.post(
        f'{storage_service_url}/contentmanagement/chat/create_conversation',
        json={
            "name": name,
            "participants": participants
        },
        headers={"Authorization": request.headers.get('Authorization')}
    )
    return jsonify(response.json()), response.status_code

@bp.route('/get_conversation/<conv_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_conversation(conv_id):
    response = requests.get(
        f'{storage_service_url}/contentmanagement/chat/get_conversation/{conv_id}',
        headers={"Authorization": request.headers.get('Authorization')}
    )
    return jsonify(response.json()), response.status_code