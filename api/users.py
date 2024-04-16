import json
import os
import time
import datetime
from flask import Blueprint, current_app, request
from db import mongo
from utils import cacheutil
import bcrypt

script_dir = os.path.dirname(os.path.abspath(__file__))
yaml_file_path = os.path.join(script_dir, '..', 'config.yaml')
users = Blueprint('users', __name__, url_prefix='/users')


@users.route('/')
def users_index():
    client = current_app.extensions['mongo_client']
    count_filter = request.args.get('count_filter')
    if count_filter is None:
        count_filter = {}
    else:
        count_filter = json.loads(count_filter)
    data = mongo.count(client, 'users', count_filter=count_filter)
    return data


@users.route('/getuserbyuserid')
def getuserbyuserid():
    client = current_app.extensions['mongo_client']
    id = request.args.get('userid')
    users_data = mongo.find(client, 'users', {'userid': id})
    return users_data


@users.route('/getuserbyemail')
def getuserbyemail():
    client = current_app.extensions['mongo_client']
    email = request.args.get('email')
    users_data = mongo.find(client, 'users', {'email': email})
    return users_data


@users.route('/checkuserbyemail')
def checkuserbyemail():
    client = current_app.extensions['mongo_client']
    email = request.args.get('email')
    users_data = mongo.find(client, 'users', {'email': email})
    if len(json.loads(users_data)) > 0:
        res = {
            "code": 200,
            "msg": "Registered"
        }
        return json.dumps(res)
    else:
        res = {
            "code": 200,
            "msg": "UnRegistered"
        }
        return json.dumps(res)


@users.route("/register", methods=['POST'])
def register():
    client = current_app.extensions['mongo_client']
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')
    captcha = request.json.get('captcha')
    key = str(captcha.get('id'))
    code = str(captcha.get('code'))
    cache_result = cacheutil.get_from_global_cache(key)
    if cache_result.lower() != code.lower():
        res = {
            "code": 200,
            "msg": "Wrong captcha"
        }
        return json.dumps(res)
    else:
        users_data = mongo.find(client, 'users', {'email': username})
        if len(json.loads(users_data)) > 0:
            res = {
                "code": 200,
                "msg": "Registered"
            }
            return json.dumps(res)
        else:
            userid = 'xin:'+str(int(time.time()))
            role = "user"
            now_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            user = {"userid":userid,"username":username,"email":email,"password":hash_password(password),"role":role,"register_time":now_time}
            mongo.put_object(client,'users',user)
            res = {
                "code": 200,
                "msg": "success"
            }
            return json.dumps(res)


def hash_password(password: str):
    salt = bcrypt.gensalt(rounds=12)  # 生成盐，可调整计算强度（轮数）
    hashed_password = bcrypt.hashpw(password.encode(), salt)  # 加密密码
    return hashed_password



@users.route('/countusergtedate')
def countusergtedate():
    client = current_app.extensions['mongo_client']
    register_time = request.args.get('register_time')
    papers_data = mongo.find(client, 'users',query={"register_time":{'$gte':register_time}},query2={"_id":1},sort={'key': 'date','order': 'desc'})
    return papers_data

@users.route("/getusers")
def getusers():
    client = current_app.extensions['mongo_client']
    user_data = mongo.find(client, 'users',query={},query2={"_id":1,"username":1,"userid":1,"avatar":1,"email":1,"role":1,"register_time":1}, sort={'key': 'date', 'order': 'desc'})
    print(user_data)
    return user_data