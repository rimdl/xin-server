import json
import time
import os

import requests
from bson import ObjectId
from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from db import mongo

script_dir = os.path.dirname(os.path.abspath(__file__))
yaml_file_path = os.path.join(script_dir, '..', 'config.yaml')
comments = Blueprint('comments', __name__, url_prefix='/comments')


@comments.route('/')
def comments_index():
    client = current_app.extensions['mongo_client']
    count_filter = request.args.get('count_filter')
    if count_filter is None:
        count_filter = {}
    else:
        count_filter = json.loads(count_filter)
    data = mongo.count(client, 'comments', count_filter=count_filter)
    return data


@comments.route('/getcommentsbypaperid')
def getcommentsbypaperid():
    client = current_app.extensions['mongo_client']
    id = request.args.get('_id')
    comments_data = mongo.find(client, 'comments', query={'paperid': id},sort={'key': 'date','order': 'desc'})
    return comments_data


@comments.route('/publishcomment', methods=['POST'])
def publishcomment():
    client = current_app.extensions['mongo_client']
    form_data = request.get_json()
    access_token = form_data['logininfo']['access_token']
    user_data = requests.get("https://gitee.com/api/v5/user?access_token=" + access_token)
    if user_data.status_code == 200:
        remote_userid = user_data.json().get('id')
        db_user = mongo.find(client,'users', query={'userid':form_data['comment']['login']+':'+str(remote_userid)})
        if db_user:
            comment = form_data.get('comment')
            comment['date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            location_data = requests.get("https://searchplugin.csdn.net/api/v1/ip/get?ip="+comment['ip'])
            if location_data.status_code == 200:
                comment['location'] = location_data.json().get('data')['address']
            else:
                comment['location'] = '未知'
            print(comment['location'])
            mongo.put_object(client,'comments', comment)
            return {"success":True}
        else:
            return {"success":False}
    return {"success":False}



@comments.route('/getrecentcomments')
def getrecentcomments():
    client = current_app.extensions['mongo_client']
    comments_data = mongo.find(client, 'comments',sort={'key': 'date','order': 'desc'},limit=10)
    return comments_data


@comments.route('/getcommentslimit')
def getcommentslimit():
    client = current_app.extensions['mongo_client']
    limit = request.args.get('limit')
    skip = request.args.get('skip')
    if limit is not None:
        if skip is not None:
            papers_data = mongo.find(client, 'comments', sort={'key': 'date', 'order': 'desc'}, limit=int(limit),skip=int(skip))
        else:
            papers_data = mongo.find(client, 'comments', sort={'key': 'date', 'order': 'desc'}, limit=int(limit))
        return papers_data
    else:
        res = {"msg":"Please input the limit number!"}
        return json.dumps(res)

@comments.route('/hiddencomment',methods=['GET'])
@jwt_required()
def hiddencomment():
    role = get_jwt().get('role')
    if role == 'admin':
        commentid = request.args.get("id")
        flag = request.args.get("flag")
        client = current_app.extensions['mongo_client']
        query = {"_id": ObjectId(commentid)}
        if flag == 'true':
            update_query = {"$set": {"hidden":True}}
        else:
            update_query = {"$set": {"hidden":False}}
        print(query,update_query)
        res = mongo.updateDoc(client, 'comments', query=query, update_query=update_query)
        return res
    else:
        return {"msg": "not admin"}, 403


@comments.route('/deletecomment', methods=['DELETE'])
@jwt_required()
def deletecomment():
    role = get_jwt().get('role')
    if role == 'admin':
        client = current_app.extensions['mongo_client']
        idList = request.get_json()
        print(idList)
        deleted_count = 0
        for item in idList:
            _id = item['_id']
            delete_res = mongo.deleteDoc(client, 'comments', query={'_id': ObjectId(_id.get('$oid'))})
            deleted_count += json.loads(delete_res).get("deleted_count")
        return json.dumps({"deleted_count": deleted_count})
    else:
        return {"msg": "not admin"}, 403