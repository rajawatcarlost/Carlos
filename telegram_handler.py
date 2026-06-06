import asyncio
import os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from models import db, TelegramAccount
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramHandler:
    """Handle Telegram client operations"""
    
    def __init__(self, api_id, api_hash, session_dir='telegram_sessions'):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_dir = session_dir
        self.clients = {}
        
        # Create session directory if it doesn't exist
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)
    
    def get_client(self, phone_number):
        """Get or create a Telegram client for a phone number"""
        session_path = os.path.join(self.session_dir, phone_number)
        
        if phone_number not in self.clients:
            client = TelegramClient(session_path, self.api_id, self.api_hash)
            self.clients[phone_number] = client
        
        return self.clients[phone_number]
    
    async def login(self, phone_number, password=None):
        """Login to Telegram account"""
        try:
            client = self.get_client(phone_number)
            
            if not await client.is_user_authorized():
                await client.connect()
                
                # Request code
                await client.request_login_token(phone_number)
                
                return {
                    'status': 'code_requested',
                    'message': f'Code sent to {phone_number}',
                    'phone_number': phone_number
                }
            
            return {
                'status': 'already_connected',
                'message': 'Already logged in'
            }
        
        except Exception as e:
            logger.error(f"Login error for {phone_number}: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def verify_login_code(self, phone_number, code):
        """Verify login code and complete authentication"""
        try:
            client = self.get_client(phone_number)
            
            if not await client.is_user_authorized():
                await client.connect()
                user = await client.sign_in_with_password_async(phone_number, code)
            else:
                user = await client.get_me()
            
            # Store session string for persistence
            account = TelegramAccount.query.filter_by(phone_number=phone_number).first()
            if not account:
                account = TelegramAccount(phone_number=phone_number)
            
            account.user_id = str(user.id)
            account.first_name = user.first_name or ''
            account.username = user.username or ''
            account.is_active = True
            
            db.session.add(account)
            db.session.commit()
            
            return {
                'status': 'success',
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'first_name': user.first_name,
                    'username': user.username
                }
            }
        
        except SessionPasswordNeededError:
            return {
                'status': 'password_needed',
                'message': 'Password verification required'
            }
        except Exception as e:
            logger.error(f"Verification error for {phone_number}: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def verify_password(self, phone_number, password):
        """Verify 2FA password"""
        try:
            client = self.get_client(phone_number)
            user = await client.sign_in_with_password_async(password)
            
            account = TelegramAccount.query.filter_by(phone_number=phone_number).first()
            if not account:
                account = TelegramAccount(phone_number=phone_number)
            
            account.user_id = str(user.id)
            account.first_name = user.first_name or ''
            account.username = user.username or ''
            account.is_active = True
            
            db.session.add(account)
            db.session.commit()
            
            return {
                'status': 'success',
                'message': '2FA verification successful'
            }
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def get_groups(self, phone_number):
        """Get all groups for an account"""
        try:
            client = self.get_client(phone_number)
            
            if not await client.is_user_authorized():
                return {
                    'status': 'error',
                    'message': 'Account not authorized'
                }
            
            await client.connect()
            
            groups = []
            async for dialog in client.iter_dialogs():
                if dialog.is_group:
                    groups.append({
                        'id': str(dialog.id),
                        'name': dialog.name,
                        'username': dialog.entity.username if hasattr(dialog.entity, 'username') else None,
                        'participants_count': dialog.entity.participants_count if hasattr(dialog.entity, 'participants_count') else 0
                    })
            
            return {
                'status': 'success',
                'groups': groups
            }
        
        except Exception as e:
            logger.error(f"Error getting groups for {phone_number}: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def send_message(self, phone_number, group_id, message):
        """Send message to a group"""
        try:
            client = self.get_client(phone_number)
            
            if not await client.is_user_authorized():
                await client.connect()
            
            await client.send_message(int(group_id), message)
            
            return {
                'status': 'success',
                'message': 'Message sent successfully'
            }
        
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def broadcast_to_groups(self, phone_number, group_ids, message, delay=2):
        """Send message to multiple groups with delay"""
        results = {
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            client = self.get_client(phone_number)
            
            if not await client.is_user_authorized():
                await client.connect()
            
            for group_id in group_ids:
                try:
                    await client.send_message(int(group_id), message)
                    results['successful'] += 1
                    await asyncio.sleep(delay)  # Anti-spam delay
                
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append({
                        'group_id': group_id,
                        'error': str(e)
                    })
        
        except Exception as e:
            logger.error(f"Broadcast error: {str(e)}")
            results['errors'].append({'general': str(e)})
        
        return results
    
    async def disconnect(self, phone_number):
        """Disconnect a client"""
        try:
            if phone_number in self.clients:
                client = self.clients[phone_number]
                if client.is_connected():
                    await client.disconnect()
                del self.clients[phone_number]
            
            return {'status': 'success'}
        
        except Exception as e:
            logger.error(f"Disconnect error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def disconnect_all(self):
        """Disconnect all clients"""
        for phone_number in list(self.clients.keys()):
            await self.disconnect(phone_number)
