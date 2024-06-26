from StorageManagement.models.message import Message
from StorageManagement.models.conversation import Conversation, ConversationParticipants
from StorageManagement.models.user import User
from utils.verification import verify_kwargs, strip_attrs

from ..usermanagement.user import get_user

def create_message(**kwargs) -> tuple:
    """Adds new messages from users to the storage

    Arguments:
        sender_id: the user_id of the message sender
        conversation_id: the id of the conversation the user is sending the message to.
            This can be a group chat or normal inter-user messaging.

    Optional Arguments: (at least 1 must be given)
        content: text content of the message
        image: image file of a message
        video: video file of a message
    
    Return:
        a tuple. [0]: true or false, [1]: a message to return. [2] possible status code for requests
    """
    verify_kwargs(kwargs, {
        "sender_id",
        "conversation_id"
    })

    sender_id = kwargs.get('sender_id')
    conversation_id = kwargs.get('conversation_id')
    content = kwargs.get('content')
    image = kwargs.get('image', None)
    video = kwargs.get('video', None)

    if sender_id is None or conversation_id is None:
        return False, 'sender_id or conversation_id not passed', 400

    # check if the sender is in the conversation
    sender_in_conversation = False
    conv_participants = ConversationParticipants.search(conversation_id=conversation_id)
    if conv_participants is not None:
        for conv_part in conv_participants:
            conv_part = conv_part.to_dict()
            if sender_id == conv_part["user_id"]:
                sender_in_conversation = True

    if not sender_in_conversation:
        return False, "This sender id can't be found among the conversation participants", 404
    
    # create a new Message object
    new_message = Message(
        sender_id=sender_id,
        conversation_id=conversation_id,
        content=content,
        image=image,
        video=video
    )
    message_id = new_message.id
    new_message.save() # save the new message to storage
    msg = Message.search(id=message_id)
    if msg is not None:
        msg_dict = msg[0].to_dict()
        sender = get_user(msg_dict['sender_id']) # Retrieve details about each messae sender
        msg_dict['sender'] = sender[1]
    else:
        msg_dict = {"msg": "message not found"}
    return True, {"msg": msg_dict}, 201

def create_conversation(conv_name, conv_participants: list) -> tuple:
    """Creates a conversation between users
            Conversations can be between as many user. Maybe group chats.
            
    Arguments:
        conv_name: the name to be assigned to the conversation. This could be useful for group chats.
        conv_participants: The users to be in the conversation
    
    Return:
        a tuple. [0]: true or false, [1]: a message to return. [2] possible status code for requests
    """
    if conv_name is None:
        return False, 'conversation name is not given', 400
    if conv_participants is None or len(conv_participants) < 2:
        return False, 'conversation participant cannot be less than 2', 400
    
    # TODO: confirm that all conversation participants
    # sent are actual users in storage.

    exists, conv_id = confirm_conversation(conv_participants[0], conv_participants[1])
    if exists:
        return False, {
            'msg': "Conversation already exists, confirmation successful, please see the conversation id",
            'conversation_id': conv_id
        }, 200
    # Create a new Conversation object and save.
    new_conversation = Conversation(conv_name)
    new_conversation.save()

    # Create a ConversationParticipants object for each user in the conversation and save
    for conv_participant in conv_participants:
        new_conv_part = ConversationParticipants(conv_participant, new_conversation.id)
        new_conv_part.save()

    return True, {
        'msg': 'new conversation created successfully, participants added.',
        'conversation_id': new_conversation.id
    }, 201

def get_conversation(conv_id) -> tuple:
    """ Get a particular conversation (including messages) from the storage

    Arguments:
        conv_id: the id of the conversation to get

    Return:
        a tuple. [0]: true or false, [1]: a message to return. [2] possible status code for requests
    """
    conversation = Conversation.search(id=conv_id)
    messages = Message.search(conversation_id=conv_id)
    conv_participants = ConversationParticipants.search(conversation_id=conv_id)
    tmp = []

    if conversation is None:
        return False, "No conversation matched conversation_id in storage", 400
    else:
        conversation = conversation[0].to_dict() # convert conversation from an object to a dictionary
    if conv_participants is None:
        return False, "error, conversation participants not found in this conversation", 404
    
    if messages is not None:
        for message in messages:
            msg_dict = message.to_dict()
            sender = get_user(msg_dict['sender_id'])
            msg_dict['sender'] = sender[1]
            tmp.append(msg_dict)
    messages = tmp

    if len(messages) > 0:
        # sort the messages based on the time
        messages = sorted(messages, key=lambda message: message['created_at'])

    tmp = []
    for conv_participant in conv_participants:
        user = User.search(id=conv_participant.user_id)
        if user is None: # only append conversation participants that are actual users in storage.
            continue

        # Remove the user password from the object
        user_striped = strip_attrs(user[0].to_dict(), ['password'])
        if user_striped is None:
            raise Exception('Error in striping user object of sensitive values')
        # returning the user instead of just the conversation_participants dictionary, or table.
        tmp.append(user_striped)
    conv_participants = tmp

    return True, {
        "msg": "conversation retrieved successfully",
        "conversation": conversation,
        "messages": messages,
        "conversation_participants": conv_participants
    }, 200

def confirm_conversation(user_id, friend_id):
    """Checks if any conversation previously exists between two users

    Arguments:
        user_id => user_id is the id of the logged in user
        friend_id => the id of the other user

    Return: true or false
    """
    CONVERSATION_CONFIMED = False
    conv_id = ""
    user_conversations_p = ConversationParticipants.search(user_id=user_id)
    if user_conversations_p is not None:
        for usr_conv in user_conversations_p:
            conv = ConversationParticipants.search(user_id=friend_id, conversation_id=usr_conv.conversation_id)
            if conv is None:
                continue
            CONVERSATION_CONFIMED = True
            conv_id = usr_conv.conversation_id
            break

    return CONVERSATION_CONFIMED, conv_id