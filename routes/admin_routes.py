from os import listdir
from uuid import uuid4
from flask import request,send_from_directory,Blueprint
from flask_login import login_required,current_user
from common.response import make_response

from common.profile import Profile
from pathlib import Path
import base64

from models.graph import Graph
from enter.extensions import db

from storage import get_storage
import config

admin_bp=Blueprint('admin',__name__)

def file_to_base(file):
    data=file.read()
    base64_data=base64.b64encode(data).decode('utf-8')
    return base64_data

@admin_bp.errorhandler(413)
def file_too_large(_):
    return make_response(413,"文件过大啦！最大支持200MB的图片捏！")

@admin_bp.route('/graph',methods=['GET','POST'])
@login_required
def upload_graph():
    graph_file =request.files.get('graph')
    if not graph_file:
        return make_response(400,"未上传有效图片")

    graph_id=str(uuid4())
    graph_suffix=Path(graph_file.filename).suffix

    graph_suffix_lower=graph_suffix.lower()
    ALLOW_SUFFIX={'.png','.jpeg','.gif','.jpg'}
    if graph_suffix_lower not in ALLOW_SUFFIX:
        return make_response(400,"文件类型错误，仅支持png、jpeg、gif、jpg文件")

    permission=request.form.get('permission','private')
    if permission not in ['public','private']:
        return make_response(400,"权限只能是public或private")

    graph_filename=f'{graph_id}{graph_suffix}'
    storage =get_storage()
    file_identifier=storage.save_image(graph_file,graph_filename)
    new_graph=Graph(
        graph_uuid=graph_id,
        permission=permission,
        user_id=current_user.id,
        file_identifier = file_identifier,
        storage_type = config.STORAGE_TYPE
    )
    db.session.add(new_graph)
    db.session.commit()

    return make_response(200,f"图片上传成功，id：{graph_id}")



@admin_bp.route('/graph/<string:graph_id>')
def download_graph(graph_id):

    graph = Graph.query.filter_by(graph_uuid=graph_id).first()
    if not graph:
        return make_response(404, "未找到对应图片")


    if graph.permission == 'private':
        if not current_user.is_authenticated:
            return make_response(401, "请先登录")
        if graph.user_id != current_user.id:
            return make_response(403, "无权限访问私有图片")

    storage = get_storage()
    return_format = request.args.get('format', 'stream').lower()


    if graph.storage_type == "local":
        file_identifier = graph.file_identifier
        project_root = Path(__file__).parent.parent
        full_file_path = project_root / file_identifier

        if not full_file_path.exists():
            return make_response(404, f"本地图片不存在：{str(full_file_path)}")

        if return_format != 'base64':
            return send_from_directory(str(full_file_path.parent), full_file_path.name)

        try:
            with open(full_file_path, 'rb') as f:
                base64_str = file_to_base(f)
        except Exception as e:
            return make_response(500, f"转换Base64失败：{str(e)}")

        return make_response(200, "获取base64成功：", {
            "graph_id": graph_id,
            "base64_str": base64_str,
            "file_format": full_file_path.suffix[1:]
        })


    elif graph.storage_type == "minio":
        try:
            obj_name = graph.file_identifier
            response = storage.client.get_object(storage.bucket_name, obj_name)
            file_data = response.read()


            if return_format != 'base64':
                from flask import make_response as flask_make_response
                res = flask_make_response(file_data)
                res.headers['Content-Type'] = f'image/{obj_name.split(".")[-1]}'
                return res


            base64_str = base64.b64encode(file_data).decode('utf-8')
            return make_response(200, "获取base64成功：", {
                "graph_id": graph_id,
                "base64_str": base64_str,
                "file_format": obj_name.split(".")[-1]
            })
        except Exception as e:
            return make_response(404, f"MinIO 图片不存在/读取失败：{str(e)}")

    return make_response(400, "不支持的存储类型")