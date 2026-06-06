from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Settings(db.Model):
    """Store API credentials"""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    api_id = db.Column(db.String(20), nullable=False)
    api_hash = db.Column(db.String(100), nullable=False)
    is_configured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Settings {self.id}>'


class TelegramAccount(db.Model):
    """Store telegram account information"""
    __tablename__ = 'telegram_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.String(50))
    first_name = db.Column(db.String(100))
    username = db.Column(db.String(100))
    session_string = db.Column(db.Text)  # Store session string for persistence
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    groups = db.relationship('GroupChat', backref='account', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TelegramAccount {self.phone_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'username': self.username,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


class GroupChat(db.Model):
    """Store group information for each account"""
    __tablename__ = 'group_chats'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('telegram_accounts.id'), nullable=False)
    group_id = db.Column(db.String(50), nullable=False)
    group_name = db.Column(db.String(255), nullable=False)
    group_username = db.Column(db.String(100))
    participants_count = db.Column(db.Integer, default=0)
    is_selected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<GroupChat {self.group_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'group_name': self.group_name,
            'group_username': self.group_username,
            'participants_count': self.participants_count,
            'is_selected': self.is_selected
        }


class BroadcastJob(db.Model):
    """Store broadcast job information"""
    __tablename__ = 'broadcast_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('telegram_accounts.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    delay_between_messages = db.Column(db.Integer, default=2)  # seconds
    auto_repeat = db.Column(db.Boolean, default=False)
    repeat_interval = db.Column(db.Integer, default=3600)  # seconds
    is_active = db.Column(db.Boolean, default=True)
    groups_json = db.Column(db.Text)  # JSON array of group IDs
    total_sent = db.Column(db.Integer, default=0)
    total_failed = db.Column(db.Integer, default=0)
    last_sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    account = db.relationship('TelegramAccount', backref='broadcasts')
    
    def __repr__(self):
        return f'<BroadcastJob {self.id}>'
    
    def get_groups(self):
        if self.groups_json:
            return json.loads(self.groups_json)
        return []
    
    def set_groups(self, groups):
        self.groups_json = json.dumps(groups)
    
    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'message': self.message,
            'delay_between_messages': self.delay_between_messages,
            'auto_repeat': self.auto_repeat,
            'repeat_interval': self.repeat_interval,
            'is_active': self.is_active,
            'groups': self.get_groups(),
            'total_sent': self.total_sent,
            'total_failed': self.total_failed,
            'created_at': self.created_at.isoformat()
        }
