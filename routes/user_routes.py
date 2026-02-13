from flask import Blueprint,request,jsonify
from flask_login import login_user
from Services.UserService import UserService
from flask_login import login_required,current_user
from models.graph import Graph
from enter.extensions import db

user_bp=Blueprint('user',__name__)

@user_bp.route('/login',methods=['POST'])
def login():
    data = request.get_json()
    username=data.get('username')
    password=data.get('password')

    if not username or not password:
        return jsonify ({"code":400,"msg":"缺少用户名或密码"}),400

    user,msg=UserService.login(username,password)

    if user:
        login_user(user)
        return jsonify({"code":200,"msg":msg}),200
    else:
        return jsonify({"code":400,"msg":msg}),400



@user_bp.route('/register',methods=['POST'])
def register():
    data=request.get_json()
    username=data.get('username')
    password=data.get('password')

    if not username or not password:
        return jsonify({"code":400,"msg":"缺少用户名或密码"}),400

    success,msg=UserService.register(username,password)

    code=200 if success else 400
    return jsonify({"code":code,"msg":msg}),code



@user_bp.route('/graph/<string:graph_id>/permission',methods=['PUT'])
@login_required
def update_graph_permission(graph_id):
    graph=Graph.query.filter_by(graph_uuid=graph_id).first()
    if not graph:
        return jsonify({"code":404,"msg":"图片不存在"}),404

    if graph.user_id!=current_user.id:
        return jsonify({"code":403,"msg":"仅所有者可访问权限"}),403

    new_permission=request.json.get('permission')
    if new_permission not in['public','private']:
        return jsonify({"code":400,"msg":"权限只能是public或private"}),400

    graph.permission=new_permission
    db.session.commit()

    return jsonify({"code":200,"msg":"权限修改成功","data":new_permission}),200
