from flask import Blueprint, request, jsonify
from exts import db
from models import User, UserVersion
from datetime import datetime
import traceback

bp = Blueprint('user', __name__, url_prefix='/api/user')

# 创建用户
@bp.route('/create', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        phone = data.get('phone', '').strip() or None
        email = data.get('email', '').strip() or None

        if not username:
            return jsonify({'code': 400, 'message': '用户名不能为空！'})

        if User.query.filter_by(username=username).first():
            return jsonify({'code': 400, 'message': f'用户名「{username}」已存在！'})

        if email and User.query.filter_by(email=email).first():
            return jsonify({'code': 400, 'message': f'邮箱「{email}」已被使用！'})

        new_user = User(
            username=username,
            phone=phone,
            email=email
        )
        db.session.add(new_user)
        db.session.flush()

        initial_version = UserVersion(
            user_id=new_user.id,
            username=username,
            phone=phone,
            email=email
        )
        db.session.add(initial_version)
        db.session.commit()

        return jsonify({
            'code': 200,
            'message': f'用户「{username}」创建成功',
            'data': new_user.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'code': 500, 'message': f'创建失败：{str(e)}'})

# 获取所有用户
@bp.route('/all', methods=['GET'])
def get_all_users():
    users = User.query.order_by(User.create_time.desc()).all()
    return jsonify({
        'code': 200,
        'data': [user.to_dict() for user in users]
    })

# 获取单个用户
@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'code': 200,
        'data': user.to_dict()
    })

# 更新用户
@bp.route('/edit/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        data = request.get_json()
        new_username = data.get('username', '').strip()
        new_phone = data.get('phone', '').strip() or None
        new_email = data.get('email', '').strip() or None

        if not new_username:
            return jsonify({'code': 400, 'message': '用户名不能为空！'})

        if User.query.filter(User.username == new_username, User.id != user_id).first():
            return jsonify({'code': 400, 'message': f'用户名「{new_username}」已被使用！'})

        if new_email and User.query.filter(User.email == new_email, User.id != user_id).first():
            return jsonify({'code': 400, 'message': f'邮箱「{new_email}」已被使用！'})

        old_username = user.username
        old_phone = user.phone
        old_email = user.email

        user.username = new_username
        user.phone = new_phone
        user.email = new_email
        user.update_time = datetime.now()

        if (old_username != new_username) or (old_phone != new_phone) or (old_email != new_email):
            new_version = UserVersion(
                user_id=user.id,
                username=new_username,
                phone=new_phone,
                email=new_email
            )
            db.session.add(new_version)

        db.session.commit()
        return jsonify({
            'code': 200,
            'message': f'用户「{new_username}」更新成功！',
            'data': user.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'code': 500, 'message': f'更新失败：{str(e)}'})

# 删除用户
@bp.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': f'用户「{user.username}」已成功删除！'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除失败：{str(e)}'})

# 获取版本历史
@bp.route('/versions/<int:user_id>', methods=['GET'])
def user_versions(user_id):
    User.query.get_or_404(user_id)  # 验证用户存在
    versions = UserVersion.query.filter_by(user_id=user_id).order_by(UserVersion.update_time.desc()).all()
    return jsonify({
        'code': 200,
        'data': [version.to_dict() for version in versions]
    })