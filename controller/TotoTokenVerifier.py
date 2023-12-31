from typing import Type, TypedDict
import jwt

from config.config import Config

class TokenVerificationResult:
    code: int
    message: str
    user_email: str
    auth_provider: str
    
    def __init__(self, code: str, message: str, user_email: str = None, auth_provider: str = None) -> None:
        self.code = code
        self.message = message
        self.user_email = user_email
        self.auth_provider = auth_provider
    
class TotoTokenVerifier: 
    
    def __init__(self, cid: str = None): 
        
        self.cid = cid
        
        # Load the JWT signing key
        self.jwt_key = Config(cid = cid).jwt_key
        
    
    def verify_token(self, jwt_token: str) -> TokenVerificationResult:
        
        # Verify that the Authorization token is valid
        decoded_token = None
        
        try: 
            
            decoded_token = jwt.decode(jwt_token, self.jwt_key, algorithms=['HS256'])
            
            # Verify that the token is provided by toto
            if decoded_token.get('authProvider') != 'toto': 
                return TokenVerificationResult(code = 401, message = "JWT not issued by Toto.")
            
            return TokenVerificationResult(code = 200, message = "Token is valid.", user_email = decoded_token.get("user"), auth_provider = decoded_token.get("authProvider"))
            
        except jwt.exceptions.InvalidSignatureError: 
            return TokenVerificationResult(code = 401, message = "JWT verification failed. Invalid Signature.")
        except jwt.ExpiredSignatureError: 
            return TokenVerificationResult(code = 401, message = "JWT verification failed. Token expired.")
        except jwt.InvalidTokenError: 
            return TokenVerificationResult(code = 401, message = "JWT verification failed. Invalid token.")
