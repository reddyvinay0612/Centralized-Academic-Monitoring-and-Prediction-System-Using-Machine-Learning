from datetime import datetime
from flask import Blueprint, jsonify, request
from backend.extensions import db
from backend.app.services.auth_middleware import authenticate, require_role
from backend.app.models import User, Student, Teacher, Notification, Class, Parent

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/status', methods=['GET'])
def notifications_status():
    return jsonify({
        'module': 'Notifications & In-Portal Communications Service',
        'status': 'active',
        'endpoints': [
            '/api/notifications',
            '/api/notifications/unread-count',
            '/api/notifications/<id>/read',
            '/api/notifications/read-all',
            '/api/notifications/broadcast'
        ]
    }), 200


@notifications_bp.route('', methods=['GET'])
@authenticate()
def get_user_notifications():
    """
    Fetch notifications for the authenticated user with unread counts and pagination.
    """
    user_id = request.current_user.user_id
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    query = Notification.query.filter_by(recipient_user_id=user_id)
    unread_count = Notification.query.filter_by(recipient_user_id=user_id, status='sent').count()

    if unread_only:
        query = query.filter_by(status='sent')

    notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()

    return jsonify({
        'success': True,
        'unread_count': unread_count,
        'count': len(notifications),
        'data': [n.to_dict() for n in notifications]
    }), 200


@notifications_bp.route('/unread-count', methods=['GET'])
@authenticate()
def get_unread_count():
    """
    Fast lightweight endpoint for polling badge counters in UI navbars.
    """
    user_id = request.current_user.user_id
    unread_count = Notification.query.filter_by(recipient_user_id=user_id, status='sent').count()

    return jsonify({
        'success': True,
        'unread_count': unread_count
    }), 200


@notifications_bp.route('/<int:notification_id>/read', methods=['PATCH'])
@authenticate()
def mark_notification_as_read(notification_id):
    """
    Mark an individual notification as read.
    """
    notif = db.session.get(Notification, notification_id)
    if not notif:
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Notification not found.'}), 404

    # Authorization: only recipient can mark as read
    if notif.recipient_user_id != request.current_user.user_id and request.current_user.role not in ('admin', 'principal'):
        return jsonify({'success': False, 'error': 'FORBIDDEN', 'message': 'You do not own this notification.'}), 403

    notif.status = 'read'
    notif.read_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Notification marked as read.',
        'data': notif.to_dict()
    }), 200


@notifications_bp.route('/read-all', methods=['POST'])
@authenticate()
def mark_all_notifications_as_read():
    """
    Mark all pending notifications for the current user as read.
    """
    user_id = request.current_user.user_id
    unread_notifs = Notification.query.filter_by(recipient_user_id=user_id, status='sent').all()

    now = datetime.utcnow()
    for n in unread_notifs:
        n.status = 'read'
        n.read_at = now

    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Marked {len(unread_notifs)} notifications as read.",
        'marked_count': len(unread_notifs)
    }), 200


@notifications_bp.route('/broadcast', methods=['POST'])
@authenticate()
@require_role('teacher', 'hod', 'admin', 'principal')
def broadcast_notification():
    """
    Transmit circulars or bulletins to students and parents of an entire class or college-wide.
    """
    payload = request.get_json() or {}
    title = payload.get('title', '').strip()
    message = payload.get('message', '').strip()
    channel = payload.get('channel', 'in_app')
    target_role = payload.get('target_role', 'all')  # 'student', 'parent', 'all'
    class_id = payload.get('class_id')

    if not title or not message:
        return jsonify({
            'success': False,
            'error': 'BAD_REQUEST',
            'message': 'Title and message are required.'
        }), 400

    query = Student.query
    if class_id:
        query = query.filter_by(class_id=class_id)
    students = query.all()

    dispatched = 0
    now = datetime.utcnow()

    for s in students:
        # Deliver to student user account
        if target_role in ('student', 'all') and s.user_id:
            n_st = Notification(
                sender_id=request.current_user.user_id,
                recipient_user_id=s.user_id,
                student_id=s.student_id,
                title=title,
                message=message,
                channel=channel,
                status='sent',
                created_at=now
            )
            db.session.add(n_st)
            dispatched += 1

        # Deliver to linked parent accounts
        if target_role in ('parent', 'all'):
            for p in s.parents:
                n_pr = Notification(
                    sender_id=request.current_user.user_id,
                    recipient_user_id=p.user_id,
                    student_id=s.student_id,
                    title=f"[Student: {s.name}] {title}",
                    message=message,
                    channel=channel,
                    status='sent',
                    created_at=now
                )
                db.session.add(n_pr)
                dispatched += 1

    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Broadcast transmitted to {dispatched} recipients.",
        'dispatched_count': dispatched
    }), 201


@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
@authenticate()
def delete_notification(notification_id):
    """
    Dismiss or delete a notification.
    """
    notif = db.session.get(Notification, notification_id)
    if not notif:
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Notification not found.'}), 404

    if notif.recipient_user_id != request.current_user.user_id and request.current_user.role not in ('admin', 'principal'):
        return jsonify({'success': False, 'error': 'FORBIDDEN', 'message': 'You do not own this notification.'}), 403

    db.session.delete(notif)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Notification deleted successfully.'
    }), 200
