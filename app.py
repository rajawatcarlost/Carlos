from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import db, Settings, TelegramAccount, GroupChat, BroadcastJob
from telegram_handler import TelegramHandler
import asyncio
import json
import os
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Global telegram handler
telegram_handler = None


@app.before_request
def check_setup():
    """Check if system is configured"""
    if request.path.startswith('/static/'):
        return
    
    settings = Settings.query.first()
    
    if not settings or not settings.is_configured:
        if request.path != '/setup' and request.path != '/save-setup':
            return redirect(url_for('setup'))


@app.route('/')
def index():
    """Dashboard home page"""
    accounts = TelegramAccount.query.filter_by(is_active=True).all()
    stats = {
        'total_accounts': len(accounts),
        'total_groups': GroupChat.query.count(),
        'total_broadcasts': BroadcastJob.query.count()
    }
    return render_template('index.html', stats=stats, accounts=accounts)


@app.route('/setup', methods=['GET'])
def setup():
    """Setup page - Get API credentials"""
    settings = Settings.query.first()
    
    if settings and settings.is_configured:
        return redirect(url_for('index'))
    
    return render_template('setup.html')


@app.route('/save-setup', methods=['POST'])
def save_setup():
    """Save API credentials"""
    data = request.json
    api_id = data.get('api_id', '').strip()
    api_hash = data.get('api_hash', '').strip()
    
    if not api_id or not api_hash:
        return jsonify({'status': 'error', 'message': 'API ID and Hash are required'}), 400
    
    try:
        settings = Settings.query.first()
        
        if not settings:
            settings = Settings()
        
        settings.api_id = api_id
        settings.api_hash = api_hash
        settings.is_configured = True
        
        db.session.add(settings)
        db.session.commit()
        
        # Initialize telegram handler
        global telegram_handler
        telegram_handler = TelegramHandler(api_id, api_hash)
        
        return jsonify({'status': 'success', 'message': 'Settings saved successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/accounts')
def accounts():
    """Accounts management page"""
    accounts = TelegramAccount.query.all()
    return render_template('accounts.html', accounts=accounts)


@app.route('/add-account', methods=['GET'])
def add_account():
    """Add new account page"""
    return render_template('add_account.html')


@app.route('/api/start-login', methods=['POST'])
def start_login():
    """Start telegram login"""
    data = request.json
    phone_number = data.get('phone_number', '').strip()
    
    if not phone_number:
        return jsonify({'status': 'error', 'message': 'Phone number is required'}), 400
    
    # Check if account already exists
    existing_account = TelegramAccount.query.filter_by(phone_number=phone_number).first()
    if existing_account:
        return jsonify({'status': 'error', 'message': 'Account already added'}), 400
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(telegram_handler.login(phone_number))
        loop.close()
        
        if result['status'] == 'code_requested':
            session['phone_number'] = phone_number
            return jsonify(result)
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/verify-login-code', methods=['POST'])
def verify_login_code():
    """Verify login code"""
    data = request.json
    phone_number = session.get('phone_number')
    code = data.get('code', '').strip()
    
    if not phone_number or not code:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(telegram_handler.verify_login_code(phone_number, code))
        loop.close()
        
        if result['status'] == 'success':
            session.pop('phone_number', None)
            return jsonify(result)
        elif result['status'] == 'password_needed':
            return jsonify(result)
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/verify-password', methods=['POST'])
def verify_password():
    """Verify 2FA password"""
    data = request.json
    phone_number = session.get('phone_number')
    password = data.get('password', '')
    
    if not phone_number or not password:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(telegram_handler.verify_password(phone_number, password))
        loop.close()
        
        if result['status'] == 'success':
            session.pop('phone_number', None)
            return jsonify(result)
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/get-groups/<int:account_id>', methods=['GET'])
def get_groups(account_id):
    """Get groups for an account"""
    account = TelegramAccount.query.get(account_id)
    
    if not account:
        return jsonify({'status': 'error', 'message': 'Account not found'}), 404
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(telegram_handler.get_groups(account.phone_number))
        loop.close()
        
        if result['status'] == 'success':
            # Save groups to database
            GroupChat.query.filter_by(account_id=account_id).delete()
            
            for group in result['groups']:
                group_chat = GroupChat(
                    account_id=account_id,
                    group_id=group['id'],
                    group_name=group['name'],
                    group_username=group.get('username'),
                    participants_count=group.get('participants_count', 0)
                )
                db.session.add(group_chat)
            
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'groups': result['groups']
            })
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/groups/<int:account_id>')
def groups(account_id):
    """Groups management page"""
    account = TelegramAccount.query.get(account_id)
    
    if not account:
        return redirect(url_for('accounts'))
    
    groups = GroupChat.query.filter_by(account_id=account_id).all()
    return render_template('groups.html', account=account, groups=groups)


@app.route('/api/save-groups', methods=['POST'])
def save_groups():
    """Save selected groups"""
    data = request.json
    account_id = data.get('account_id')
    selected_groups = data.get('selected_groups', [])
    
    try:
        # Update all groups for this account
        GroupChat.query.filter_by(account_id=account_id).update({'is_selected': False})
        
        for group_id in selected_groups:
            group = GroupChat.query.filter_by(account_id=account_id, group_id=str(group_id)).first()
            if group:
                group.is_selected = True
        
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Groups saved successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/broadcast/<int:account_id>')
def broadcast(account_id):
    """Broadcast message page"""
    account = TelegramAccount.query.get(account_id)
    
    if not account:
        return redirect(url_for('accounts'))
    
    selected_groups = GroupChat.query.filter_by(account_id=account_id, is_selected=True).all()
    return render_template('broadcast.html', account=account, groups=selected_groups)


@app.route('/api/send-broadcast', methods=['POST'])
def send_broadcast():
    """Send broadcast message"""
    data = request.json
    account_id = data.get('account_id')
    message = data.get('message', '').strip()
    delay = int(data.get('delay', 2))
    auto_repeat = data.get('auto_repeat', False)
    repeat_interval = int(data.get('repeat_interval', 3600))
    
    if not message:
        return jsonify({'status': 'error', 'message': 'Message cannot be empty'}), 400
    
    account = TelegramAccount.query.get(account_id)
    if not account:
        return jsonify({'status': 'error', 'message': 'Account not found'}), 404
    
    try:
        selected_groups = GroupChat.query.filter_by(account_id=account_id, is_selected=True).all()
        group_ids = [group.group_id for group in selected_groups]
        
        if not group_ids:
            return jsonify({'status': 'error', 'message': 'No groups selected'}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(
            telegram_handler.broadcast_to_groups(account.phone_number, group_ids, message, delay)
        )
        loop.close()
        
        # Save broadcast job
        broadcast_job = BroadcastJob(
            account_id=account_id,
            message=message,
            delay_between_messages=delay,
            auto_repeat=auto_repeat,
            repeat_interval=repeat_interval,
            is_active=True,
            total_sent=results['successful'],
            total_failed=results['failed'],
            last_sent_at=datetime.utcnow()
        )
        broadcast_job.set_groups(group_ids)
        
        db.session.add(broadcast_job)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Message sent to {results["successful"]} groups',
            'results': results
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/delete-account/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    """Delete an account"""
    try:
        account = TelegramAccount.query.get(account_id)
        
        if not account:
            return jsonify({'status': 'error', 'message': 'Account not found'}), 404
        
        # Delete related data
        GroupChat.query.filter_by(account_id=account_id).delete()
        BroadcastJob.query.filter_by(account_id=account_id).delete()
        
        db.session.delete(account)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Account deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/history')
def history():
    """Broadcast history page"""
    jobs = BroadcastJob.query.order_by(BroadcastJob.created_at.desc()).all()
    return render_template('history.html', jobs=jobs)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('500.html'), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Initialize telegram handler if settings exist
        settings = Settings.query.first()
        if settings and settings.is_configured:
            telegram_handler = TelegramHandler(settings.api_id, settings.api_hash)
    
    app.run(debug=True, host='127.0.0.1', port=5000)
