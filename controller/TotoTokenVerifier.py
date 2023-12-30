from typing import Type, TypedDict
import jwt

class TokenVerificationResult:
    code: int
    message: str
    
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
    
class TotoTokenVerifier: 
    
    def verify_token(self, jwt_token: str) -> TokenVerificationResult:
        
        # Verify that the Authorization token is valid
        jwt_key = "9a8nsd098a0s98dn098as09d8!!&%£sji0n890adsAAAD3AS"
        
        decoded_token = None
        
        try: 
            
            decoded_token = jwt.decode(jwt_token, jwt_key, algorithms=['HS256'])
            
        except jwt.exceptions.InvalidSignatureError: 
            return TokenVerificationResult(code = 401, message = "JWT verification failed. Invalid Signature.")
        except jwt.ExpiredSignatureError: 
            return TokenVerificationResult(code = 401, message = "JWT verification failed. Token expired.")
        except jwt.InvalidTokenError: 
            return TokenVerificationResult(code = 401, message = "JWT verification failed. Invalid token.")
        
        # Verify that the token is provided by toto
        if decoded_token.get('authProvider') != 'toto': 
            return TokenVerificationResult(code = 401, message = "JWT not issued by Toto.")
        
        return TokenVerificationResult(code = 200, message = "Token is valid.")
