from flask import Blueprint,request,jsonify
from flask_login import login_user
from Services.UserService import UserService
from flask_login import login_required,current_user
from models.graph import Graph
from enter.extensions import db
from common.response import make_response

user_bp=Blueprint('user',__name__)

@user_bp.route('/login',methods=['POST'])
def login():
    data = request.get_json()
    username=data.get('username')
    password=data.get('password')

    if not username or not password:
        return make_response(400,"缺少用户名或密码")

    user,msg=UserService.login(username,password)

    if user:
        login_user(user)
        return make_response(200,"登录成功")
    else:
        return make_response(400,"登录失败")



@user_bp.route('/register',methods=['POST'])
def register():
    data=request.get_json()
    username=data.get('username')
    password=data.get('password')

    if not username or not password:
        return make_response(400,"缺少用户名或密码")

    success,msg=UserService.register(username,password)

    code,msg=(200,"操作成功") if success else (400,"操作失败")
    return make_response(code,msg)



@user_bp.route('/graph/<string:graph_id>/permission',methods=['PUT'])
@login_required
def update_graph_permission(graph_id):
    graph=Graph.query.filter_by(graph_uuid=graph_id).first()
    if not graph:
        return make_response(404,"图片不存在")

    if graph.user_id!=current_user.id:
        return make_response(403,"仅所有者可访问权限")

    new_permission=request.json.get('permission')
    if new_permission not in['public','private']:
        return make_response(400,"权限只能是public或private")

    graph.permission=new_permission
    db.session.commit()

    return make_response(200,"权限修改成功",new_permission)
