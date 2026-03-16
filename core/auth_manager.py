"""
用户认证管理模块

支持用户注册、登录、Token校验和权限管理
"""

import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from pathlib import Path


class AuthManager:
    """用户认证和授权管理器"""
    
    def __init__(self, db_path: str = 'users_db.json'):
        self.db_path = Path(db_path)
        self.users_db: Dict = {}
        self.sessions: Dict = {}  # token -> user_info
        self.token_expiry: Dict = {}  # token -> expiry_time
        self.load_database()
    
    def load_database(self):
        """从JSON文件加载用户数据库"""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self.users_db = json.load(f)
            except Exception as e:
                print(f"⚠️  Failed to load user database: {e}")
                self.users_db = {}
        else:
            self.users_db = {}
    
    def save_database(self):
        """保存用户数据库到JSON文件"""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.users_db, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Failed to save user database: {e}")
    
    @staticmethod
    def hash_password(password: str) -> str:
        """对密码进行哈希处理（PBKDF2）"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}${pwd_hash.hex()}"
    
    @staticmethod
    def verify_password(password: str, pwd_hash: str) -> bool:
        """验证密码"""
        try:
            salt, stored_hash = pwd_hash.split('$')
            pwd_verify = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return pwd_verify.hex() == stored_hash
        except Exception:
            return False
    
    def register(self, username: str, password: str, email: str = "") -> Tuple[bool, str]:
        """
        用户注册
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱（可选）
            
        Returns:
            (是否成功, 消息)
        """
        # 验证输入
        if not username or len(username) < 3:
            return False, "❌ 用户名至少3个字符"
        
        if not password or len(password) < 6:
            return False, "❌ 密码至少6个字符"
        
        # 检查用户名是否已存在
        if username in self.users_db:
            return False, "❌ 用户名已存在"
        
        # 创建新用户
        self.users_db[username] = {
            'password_hash': self.hash_password(password),
            'email': email,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'role': 'user',  # 用户角色：user, admin
            'is_active': True,
            'detections_count': 0  # 检测次数统计
        }
        
        self.save_database()
        return True, f"✅ 用户 {username} 注册成功！"
    
    def login(self, username: str, password: str, token_expiry_hours: int = 24) \
            -> Tuple[bool, str, Optional[str]]:
        """
        用户登录
        
        Args:
            username: 用户名
            password: 密码
            token_expiry_hours: Token有效时间（小时）
            
        Returns:
            (是否成功, 消息, Token)
        """
        # 检查用户是否存在
        if username not in self.users_db:
            return False, "❌ 用户名或密码错误", None
        
        user = self.users_db[username]
        
        # 检查用户是否激活
        if not user.get('is_active', True):
            return False, "❌ 账户已被禁用", None
        
        # 验证密码
        if not self.verify_password(password, user['password_hash']):
            return False, "❌ 用户名或密码错误", None
        
        # 生成Token
        token = secrets.token_urlsafe(32)
        expiry_time = datetime.now() + timedelta(hours=token_expiry_hours)
        
        # 保存会话
        self.sessions[token] = {
            'username': username,
            'login_time': datetime.now().isoformat(),
            'role': user['role']
        }
        self.token_expiry[token] = expiry_time.isoformat()
        
        # 更新最后登录时间
        user['last_login'] = datetime.now().isoformat()
        self.save_database()
        
        return True, f"✅ 欢迎，{username}！", token
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """
        验证Token是否有效
        
        Args:
            token: 要验证的Token
            
        Returns:
            (是否有效, 用户信息)
        """
        if token not in self.sessions:
            return False, None
        
        # 检查Token是否过期
        expiry_str = self.token_expiry.get(token)
        if expiry_str:
            expiry_time = datetime.fromisoformat(expiry_str)
            if datetime.now() > expiry_time:
                # Token已过期
                del self.sessions[token]
                del self.token_expiry[token]
                return False, None
        
        return True, self.sessions[token]
    
    def logout(self, token: str) -> bool:
        """
        用户登出
        
        Args:
            token: 用户Token
            
        Returns:
            是否成功
        """
        if token in self.sessions:
            del self.sessions[token]
            if token in self.token_expiry:
                del self.token_expiry[token]
            return True
        return False
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """获取用户信息"""
        if username in self.users_db:
            user = self.users_db[username].copy()
            # 不返回密码哈希
            user.pop('password_hash', None)
            return user
        return None
    
    def update_detection_count(self, token: str) -> bool:
        """更新用户的检测次数"""
        is_valid, user_info = self.verify_token(token)
        if not is_valid:
            return False
        
        username = user_info['username']
        if username in self.users_db:
            self.users_db[username]['detections_count'] = \
                self.users_db[username].get('detections_count', 0) + 1
            self.save_database()
            return True
        return False
    
    def get_user_stats(self, token: str) -> Optional[Dict]:
        """获取用户统计信息"""
        is_valid, user_info = self.verify_token(token)
        if not is_valid:
            return None
        
        username = user_info['username']
        user = self.users_db.get(username)
        if user:
            return {
                'username': username,
                'role': user.get('role'),
                'created_at': user.get('created_at'),
                'last_login': user.get('last_login'),
                'detections_count': user.get('detections_count', 0)
            }
        return None
    
    def is_admin(self, token: str) -> bool:
        """检查用户是否为管理员"""
        is_valid, user_info = self.verify_token(token)
        return is_valid and user_info.get('role') == 'admin'
    
    def clear_expired_tokens(self):
        """清除过期的Token"""
        expired_tokens = []
        for token, expiry_str in self.token_expiry.items():
            expiry_time = datetime.fromisoformat(expiry_str)
            if datetime.now() > expiry_time:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            self.logout(token)
        
        return len(expired_tokens)


# 全局认证管理器实例
_auth_manager_instance: Optional[AuthManager] = None


def get_auth_manager() -> AuthManager:
    """获取全局认证管理器实例"""
    global _auth_manager_instance
    if _auth_manager_instance is None:
        _auth_manager_instance = AuthManager()
    return _auth_manager_instance
