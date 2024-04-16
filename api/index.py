from flask import Blueprint, request
from api.fileoperate import fileoperate
from api.papers import papers
from api.login import login
from api.comments import comments
from api.users import users
from api.settings import settings
from api.data import data


api = Blueprint('api', __name__, url_prefix='/api')
api.register_blueprint(fileoperate)
api.register_blueprint(papers)
api.register_blueprint(login)
api.register_blueprint(comments)
api.register_blueprint(users)
api.register_blueprint(settings)
api.register_blueprint(data)


@api.route('/')
def users_index():
    return "This is the api index page."

