# admin_middleware.py
"""
Admin middleware for protecting admin-only routes
"""

from functools import wraps
from flask import request, current_app, g, jsonify
import jwt
from model.user import User


def admin_required(func):
    """
    Middleware/decorator requiring admin authentication for API endpoints.
    
    Checks:
    1. Valid JWT token is present
    2. Token is valid and not expired
    3. User exists in database
    4. User has 'Admin' role
    
    Sets g.current_user with authenticated admin user.
    
    Returns:
        - 401 Unauthorized: Missing or invalid token
        - 403 Forbidden: User is not an admin
        - Function result if all checks pass
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Get token from cookies
        token = request.cookies.get(current_app.config.get("JWT_TOKEN_NAME", "jwt_python_flask"))
        
        if not token:
            return {
                "success": False,
                "message": "Authentication token is missing",
                "error": "Unauthorized",
                "status": 401
            }, 401
        
        try:
            # Decode JWT token
            secret_key = current_app.config.get("SECRET_KEY")
            data = jwt.decode(token, secret_key, algorithms=["HS256"])
            
            # Get user from database
            current_user = User.query.filter_by(_uid=data.get("_uid")).first()
            
            if not current_user:
                return {
                    "success": False,
                    "message": "User not found",
                    "error": "Unauthorized",
                    "status": 401
                }, 401
            
            # Check if user is admin
            if current_user._role != 'Admin':
                return {
                    "success": False,
                    "message": "Admin access required",
                    "error": "Forbidden",
                    "status": 403
                }, 403
            
            # Store user in Flask's g object for use in the view function
            g.current_user = current_user
            
        except jwt.ExpiredSignatureError:
            return {
                "success": False,
                "message": "Authentication token has expired",
                "error": "Unauthorized",
                "status": 401
            }, 401
        except jwt.InvalidTokenError as e:
            return {
                "success": False,
                "message": "Invalid authentication token",
                "error": "Unauthorized",
                "status": 401
            }, 401
        except Exception as e:
            return {
                "success": False,
                "message": "An error occurred during authentication",
                "error": str(e),
                "status": 500
            }, 500
        
        # Call the protected function
        return func(*args, **kwargs)
    
    return decorated_function
