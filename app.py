import json
import base64
import bcrypt
from flask import Flask,request,jsonify
from api.index import api
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from flask_cors import CORS
import os
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity, create_refresh_token,get_jwt
)
from db import mongo
from utils import cacheutil

load_dotenv()


MONGO_URL = os.environ.get('MONGO_URL')
JWT_SECRET = os.environ.get('JWT_SECRET')

# client = MongoClient(MONGO_URL, server_api=ServerApi('1'))
client = MongoClient(MONGO_URL)


app = Flask(__name__)
app.register_blueprint(api)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['JWT_SECRET_KEY'] = JWT_SECRET
jwt = JWTManager(app)


app.extensions['mongo_client'] = client

@app.route('/')
def hello_world():
    print("=============")
    print(request.remote_addr)
    return 'Hi,this is xin\'s back server.'


def verify_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password)


@app.route('/adminLogin', methods=['POST'])
def admin_login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    captcha = request.json.get('captcha')
    key = str(captcha.get('id'))
    code = str(captcha.get('code'))
    print(key, code)
    cache_result = cacheutil.get_from_global_cache(key)
    if cache_result.lower() != code.lower():
        res = {
            "code": 200,
            "msg": "Wrong captcha"
        }
        return json.dumps(res)
    else:
        users_data = mongo.find(client, 'users', {'email': email})
        if len(json.loads(users_data)) > 0:
            bytes_data = base64.b64decode(json.loads(users_data)[0].get('password').get('$binary').get('base64'))
            res = verify_password(password, bytes_data)
            if not res:
                return jsonify({"msg": "Bad username or password"}), 401
            token = create_access_token(identity=email,additional_claims={"role":json.loads(users_data)[0].get('role')})
            refresh_token = create_refresh_token(identity=email,additional_claims={"role":json.loads(users_data)[0].get('role')})
            return jsonify(token=token,refresh_token=refresh_token)
        else:
            return jsonify({"msg": "No user find"}), 401

# 需要JWT保护的路由
@app.route('/admin', methods=['GET'])
@jwt_required()
def admin():
    # 获取当前用户的身份
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user,role=get_jwt().get('role')), 200


@app.route("/refreshToken", methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    print("zhix")
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user,additional_claims={"role":get_jwt().get('role')})
    return jsonify(token=new_token)


if __name__ == '__main__':
    app.run(host="0.0.0.0")
