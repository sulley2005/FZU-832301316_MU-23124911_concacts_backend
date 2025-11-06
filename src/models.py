from exts import db
from datetime import datetime

# 用户主表
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    versions = db.relationship('UserVersion', backref='user', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'phone': self.phone,
            'email': self.email,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None
        }

# 用户版本记录表
class UserVersion(db.Model):
    __tablename__ = "user_version"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    update_time = db.Column(db.DateTime, default=datetime.now)
    operator = db.Column(db.String(50), default="system")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'phone': self.phone,
            'email': self.email,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S'),
            'operator': self.operator
        }
