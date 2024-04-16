import json
import os

from bson import ObjectId
from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required, get_jwt

from db import mongo

script_dir = os.path.dirname(os.path.abspath(__file__))
yaml_file_path = os.path.join(script_dir, '..', 'config.yaml')
data = Blueprint('data', __name__, url_prefix='/data')


@data.route('/')
def papers_index():
    return "This is the data index page."


@data.route('/getdata')
def getallpapers():
    client = current_app.extensions['mongo_client']
    data = mongo.find(client, 'data')
    return data

@data.route('/replacedata', methods=['POST'])
@jwt_required()
def replacedata():
    role = get_jwt().get('role')
    if role == 'admin':
        category = request.json.get("category")
        tag = request.json.get("tag")
        client = current_app.extensions['mongo_client']
        data = mongo.find(client, 'data')
        js_data = json.loads(data)
        if js_data:
            _id = js_data[0]['_id'].get("$oid")
            categories = []
            if js_data[0].get('categories'):
                categories = js_data[0]['categories']
            tags = []
            if js_data[0].get('tags'):
                tags = js_data[0]['tags']
            if category:
                categories.append(category)
            if tag:
                tags.append(tag)
            query = {"_id": ObjectId(_id)}
            new_doc = {"_id": ObjectId(_id), "categories": categories, "tags": tags}
            res = mongo.replaceDoc(client, 'data', query, new_doc)
            return res,200
        else:
            query = {}
            if category:
                query = {
                    "categories": [category]
                }
            if tag:
                query = {
                    "tags": [tag]
                }
            print(query)
            mongo.put_object(client,'data',query)
            res = {"msg": "success"}
            return json.dumps(res),200
    else:
        return {"msg": "not admin"}, 403

