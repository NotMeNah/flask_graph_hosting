from enter.extensions import db
import uuid
from datetime import datetime

class Graph(db.Model):
    __tablename__='graph'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    graph_uuid=db.Column(db.String(36),unique=True,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
    permission=db.Column(db.String(10),default='private',nullable=False)
    create_time=db.Column(db.DateTime,default=datetime.now)
    user=db.relationship('User',backref='graphs')