from models.user import User
from enter.extensions import db

class UserService:
    @staticmethod
    def register(username,password):
            if User.query.filter_by(username=username).first():
                return False,"用户已存在"

            new_user=User(username=username)
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            return True,"注册成功"

    @staticmethod
    def login(username,password):

        user=User.query.filter_by(username=username).first()
        if not user:
            return None,"用户名不存在"
        if not user.check_password(password):
            return None,"密码错误"

        return user,"登陆成功"

