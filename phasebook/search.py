from flask import Blueprint, request, jsonify, make_response
from .data.search_data import USERS
import hashlib

bp = Blueprint("search", __name__, url_prefix="/search")

@bp.route("")
def search():
    try:
        args = request.args.to_dict()
        results = search_users(args)

        response_body = jsonify(results).get_data(as_text=True)
        etag = hashlib.md5(response_body.encode('utf-8')).hexdigest()

        if_none_match = request.headers.get('If-None-Match')
        if if_none_match == etag:
            return '', 304

        response = make_response(jsonify(results), 200)
        response.headers['ETag'] = etag

        return response
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

def search_users(args):
    """Search users database

    Parameters:
        args: a dictionary containing the following search parameters:
            id: string
            name: string
            age: string
            occupation: string

    Returns:
        a list of users that match the search parameters
    """
    try:
        id_param = args.get('id')
        name_param = args.get('name')
        age_param = args.get('age')
        occupation_param = args.get('occupation')

        results = []
        priority_map = {}

        if id_param:
            for user in USERS:
                if user['id'] == id_param:
                    results.append(user)
                    priority_map[user['id']] = 0
                    break

        for user in USERS:
            if user['id'] in priority_map:
                continue

            match = False
            priority_score = 4 

            if name_param and name_param.lower() in user['name'].lower():
                match = True
                priority_score = min(priority_score, 1)

            if age_param:
                try:
                    age_param_int = int(age_param)
                    if user['age'] in range(age_param_int - 1, age_param_int + 2):
                        match = True
                        priority_score = min(priority_score, 2)
                except ValueError:
                    pass

            if occupation_param and occupation_param.lower() in user['occupation'].lower():
                match = True
                priority_score = min(priority_score, 3)

            if match:
                results.append(user)
                priority_map[user['id']] = priority_score

        results.sort(key=lambda x: priority_map.get(x['id'], 4))

        return results
    except Exception as e:
        print(f"Error occurred in search_users: {e}")
        raise e 

@bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error"}), 500
