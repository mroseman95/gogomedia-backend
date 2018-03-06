from flask import request, jsonify, current_app

from models.media import mediums, consumed_states

from logic.media import get_media, upsert_media, remove_media
from logic.user import get_user
from logic.login import login_required

# Note: It may seem like pluggable view with method based dispatching would make sense here. But because of how
# I implement login_required, and add a parameter logged_in_user, it would not work. The ViewMethod class would
# have methods that need to accept self as the first argument, which would screw up the login_required implementation


@login_required
def media(logged_in_user, username):
    """
    media accepts a PUT request with formdata that matches
        {
            'name': a string representing the name of the media to insert/update
            'medium': a string indicating the type of this media
                represents an Enum of possible values ('film', 'audio', 'literature', 'other')
            'consumed_state': a string indicating the current consumed state of this media
                represents an Enum of possible values ('not started', 'started', 'finished')
        }

    media accepts a GET request and returns all the media associated with the user specified by username
        a request arg 'consumed-state' can be set to 'not-started', 'started', or 'finished', and only media with the
            same consumed state will be returned
        a request arg 'medium' can be set to 'film', 'audio', 'literature', or 'other' and only media with the same
            medium will be returned
        if no request arg is present, all media will be returned

    media accepts a DELETE request with formdata that matches
        {
            'name': a string representing the name of the media to delete
        }
    """
    body = request.get_json()

    # This user is the one specified in url parameters, must match the auth token user
    user = get_user(username)
    validation_result = validate_url_username(logged_in_user, user)
    if validation_result is not None:
        return validation_result

    if request.method == 'GET':
        validation_result = validate_get_url_parameters()
        if validation_result is not None:
            return validation_result

        medium = request.args.get('medium')

        consumed_state = request.args.get('consumed-state')
        if consumed_state == 'not-started':
            consumed_state = 'not started'

        media_list = get_media(username, medium, consumed_state)

        return jsonify({
            'success': True,
            'message': 'successfully got media for the logged in user',
            'data': [media.as_dict() for media in media_list]
        })
    elif request.method == 'PUT':
        validation_result = validate_put_body_parameters(body)
        if validation_result is not None:
            return validation_result

        medianame = body['name']

        medium = None
        if 'medium' in body:
            medium = body['medium']

        consumed_state = None
        if 'consumed_state' in body:
            consumed_state = body['consumed_state']

        media = upsert_media(username, medianame, medium, consumed_state)

        return jsonify({
            'success': True,
            'message': 'successfully added/updated media element',
            'data': media.as_dict()
        })
    else:  # request.method == 'DELETE'
        validation_result = validate_delete_body_parameters(body)
        if validation_result is not None:
            return validation_result

        medianame = body['name']

        media = remove_media(username, medianame)
        return jsonify({
            'success': True,
            'message': 'successfully deleted media element'
        })


def validate_url_username(logged_in_user, url_user):
    """

    validate_url_username checks to see if url_user exists, and if it matches the logged_in_user.
    @param logged_in_user: a user model representing the currently logged in user
    @param url_user: a user model representing the user specified in the url
    @return: None if there is no issue, otherwise a JSON response with a detailed message on what was wrong
    """
    if url_user is None:
        # there is no user with this name, return incorrect parameters response
        return jsonify({
            'success': False,
            'message': 'user doesn\'t exist'
        }), 422

    if logged_in_user != url_user and not current_app.config['LOGIN_DISABLED']:
        # you can't get media for a user you are not logged in as
        return jsonify({
            'success': False,
            'message': 'not logged in as this user'
        }), 401


def validate_get_url_parameters():
    """
    validate_get_url_parameters checks the url parameters specified on a GET request
    @return: None if there is no issue, otherwise a JSON response with a detailed message on what was wrong
    """
    if 'consumed-state' in request.args and request.args.get('consumed-state') not in ['not-started', 'started', 'finished']:
        return jsonify({
            'success': False,
            'message': 'consumed-state url parameter must be \'not-started\', \'started\',  or \'finished\''
        }), 422

    if 'medium' in request.args and request.args.get('medium') not in mediums:
        return jsonify({
            'success': False,
            'message': 'medium url parameter must be \'film\', \'audio\', \'literature\', or \'other\''
        }), 422


def validate_put_body_parameters(body):
    """
    validate_put_body_parameters checks the body JSON, and makes sure the parameters are the correct type
    @return: None if there is no issue, otherwise a JSON response with a detailed message on what was wrong
    """
    if 'name' not in body:
        # return malformed parameters response if 'name' isn't present
        return jsonify({
            'success': False,
            'message': 'missing parameter \'name\''
        }), 422
    elif not isinstance(body['name'], str):
        # return malformed parameters response if 'name' isn't of type string
        return jsonify({
            'success': False,
            'message': 'parameter \'name\' must be type string'
        }), 422

    if 'medium' in body and body['medium'] not in mediums:
        # return malformed parameters response if 'medium' isn't a valid medium type
        return jsonify({
            'success': False,
            'message': 'medium parameter must be \'film\', \'audio\', \'literature\', or \'other\''
        }), 422

    if 'consumed_state' in body and body['consumed_state'] not in consumed_states:
        # return malfromed parameters response if 'consumed_state' isn't a valid consumed state
        return jsonify({
            'success': False,
            'message': 'consumed_state parameter must be \'not started\', \'started\', or \'finished\''
        }), 422


def validate_delete_body_parameters(body):
    """
    validate_delete_body_parameters checks the body JSON, and makes sure the parameters are the correct type
    @return: None if there is no issue, otherwise a JSON response with a detailed message on what was wrong
    """
    if 'name' not in body:
        # return malformed parameters response if 'name' isn't present
        return jsonify({
            'success': False,
            'message': 'missing parameter \'name\''
        }), 422
    elif not isinstance(body['name'], str):
        # return malformed parameters response if 'name' ins't of type string
        return jsonify({
            'success': False,
            'message': 'parameter \'name\' must be type string'
        }), 422
