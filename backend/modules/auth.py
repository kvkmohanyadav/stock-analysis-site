import hashlib
import secrets
import re
import jwt
from datetime import datetime, timedelta
from modules.database import get_db_connection

SECRET_KEY = "your-secret-key-change-in-production"

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hash_password(password) == password_hash

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_token():
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

def generate_jwt_token(user_id, email):
    """Generate JWT token for session"""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_jwt_token(token):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_user(username, password):
    """Authenticate user login"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check for default admin login
    if username.lower() == "admin" and password == "password":
        return {
            'success': True,
            'user': {
                'id': 0,
                'first_name': 'Admin',
                'last_name': 'User',
                'email': 'admin@stockanalysis.com'
            },
            'token': generate_jwt_token(0, 'admin@stockanalysis.com')
        }
    
    # Check for user by email
    cursor.execute("SELECT * FROM users WHERE email = ? AND is_active = 1", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and user['password_hash'] and verify_password(password, user['password_hash']):
        return {
            'success': True,
            'user': {
                'id': user['id'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'email': user['email']
            },
            'token': generate_jwt_token(user['id'], user['email'])
        }
    
    return {'success': False, 'error': 'Invalid credentials'}

def register_user(first_name, last_name, email, phone):
    """Register a new user"""
    # Validate email
    if not validate_email(email):
        return {'success': False, 'error': 'Invalid email format'}
    
    if not first_name or not first_name.strip():
        return {'success': False, 'error': 'First name is mandatory'}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if email already exists
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        conn.close()
        return {'success': False, 'error': 'Email already registered'}
    
    # Insert new user without password
    try:
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, phone, created_at, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (first_name.strip(), last_name.strip() if last_name else '', email.lower(), phone or '', datetime.now().isoformat()))
        
        # Generate token for password creation
        token = generate_token()
        expires_at = datetime.now() + timedelta(hours=24)
        
        cursor.execute("""
            INSERT INTO password_tokens (email, token, token_type, created_at, expires_at, used)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (email.lower(), token, 'create_password', datetime.now().isoformat(), expires_at.isoformat()))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return {
            'success': True,
            'message': 'Registration successful. Please check your email to create your password.',
            'token': token  # This will be used in the email link
        }
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

def forgot_password(first_name, last_name, email, phone):
    """Handle forgot password request"""
    if not validate_email(email):
        return {'success': False, 'error': 'Invalid email format'}
    
    if not first_name or not first_name.strip():
        return {'success': False, 'error': 'First name is mandatory'}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify user exists and details match
    cursor.execute("""
        SELECT * FROM users 
        WHERE email = ? AND first_name = ? AND is_active = 1
    """, (email.lower(), first_name.strip()))
    
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return {'success': False, 'error': 'User not found or details do not match'}
    
    # Check if last_name matches (if provided)
    if last_name and last_name.strip() and user['last_name'] != last_name.strip():
        conn.close()
        return {'success': False, 'error': 'Details do not match'}
    
    # Generate reset token
    token = generate_token()
    expires_at = datetime.now() + timedelta(hours=24)
    
    cursor.execute("""
        INSERT INTO password_tokens (email, token, token_type, created_at, expires_at, used)
        VALUES (?, ?, ?, ?, ?, 0)
    """, (email.lower(), token, 'reset_password', datetime.now().isoformat(), expires_at.isoformat()))
    
    conn.commit()
    conn.close()
    
    return {
        'success': True,
        'message': 'Password reset link has been sent to your email.',
        'token': token
    }

def verify_token(token, token_type):
    """Verify if token is valid and not expired"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM password_tokens 
        WHERE token = ? AND token_type = ? AND used = 0
    """, (token, token_type))
    
    token_record = cursor.fetchone()
    conn.close()
    
    if not token_record:
        return {'success': False, 'error': 'Invalid or expired token'}
    
    # Check if token is expired
    expires_at = datetime.fromisoformat(token_record['expires_at'])
    if datetime.now() > expires_at:
        return {'success': False, 'error': 'Token has expired'}
    
    return {
        'success': True,
        'email': token_record['email']
    }

def create_or_reset_password(token, password, token_type):
    """Create or reset password using token"""
    if len(password) < 8:
        return {'success': False, 'error': 'Password must be at least 8 characters'}
    
    # Verify token
    token_verify = verify_token(token, token_type)
    if not token_verify['success']:
        return token_verify
    
    email = token_verify['email']
    
    # Hash password
    password_hash = hash_password(password)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update user password
    cursor.execute("""
        UPDATE users SET password_hash = ? WHERE email = ?
    """, (password_hash, email))
    
    # Mark token as used
    cursor.execute("""
        UPDATE password_tokens SET used = 1 WHERE token = ?
    """, (token,))
    
    conn.commit()
    
    # Get user details
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    return {
        'success': True,
        'message': 'Password has been set successfully.',
        'user': {
            'id': user['id'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'email': user['email']
        },
        'token': generate_jwt_token(user['id'], user['email'])
    }

