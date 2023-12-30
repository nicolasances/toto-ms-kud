from abc import ABCMeta, abstractclassmethod
from flask import Request, abort, jsonify
from config.config import Config
from controller.TotoLogger import TotoLogger
import jwt

from controller.TotoTokenVerifier import TokenVerificationResult, TotoTokenVerifier

class TotoDelegate: 

    @abstractclassmethod
    def do(request):
        pass

class TotoAPIController: 
    
    def __init__(self, api_name): 
        
        self.api_name = api_name
        self.logger = TotoLogger(self.api_name)
    
    
    def delegate(self, delegate: TotoDelegate): 

        self.delegate = delegate

        return self

    
    def process(self, request: Request): 
        """ Processes an HTTP Request. 
        To process the request, this method uses the Toto Delegate that was set using the 
        delete() method. 

        Args:
            request (Request): the HTTP Request to be processed

        Returns:
            _type_: a JSONified dictionnary containing the response payload (or the error payload)
        """
        
        # Validations
        cid = request.headers.get("x-correlation-id")
        auth_header = request.headers.get("Authorization")
        
        # Verify that the Correlation Id was provided
        if not cid: 
            return self.throw_validation_error(cid, 400, "No Correlation ID provided in the Request")
        
        # Verify that an Authorization header was provided
        if not auth_header: 
            return self.throw_validation_error(cid, 400, "No Authorization header provided in the Request")
        
        # Verify that the Authorization header contains a Bearer Token
        auth_header_tokens = auth_header.split()
        
        if auth_header_tokens[0] != 'Bearer': 
            return self.throw_validation_error(cid, 400, "Authorization header does not contain a Bearer token")
        
        token_verification = TotoTokenVerifier().verify_token(auth_header_tokens[1])
        
        if token_verification.code != 200: 
            return self.throw_validation_error(cid, token_verification.code, token_verification.message)
        
        # Log the incoming call
        print(f"Incoming API Call: {request.method} {request.path}")

        return self.delegate.do(request)
    
    def throw_validation_error(self, cid: str, code: int, message: str, additional_log: str = None): 
        """ Generates a validation error

        Args:
            cid (str): the Correlation Id
            code (int): the HTTP Error Code to use
            message (str): the Message to both log and provide back to the caller
            additional_log (str): a log message to override the default log (e.g. for sensitivity or security reasons)
        """
        self.logger.log(cid, additional_log if additional_log is not None else message)
        
        return jsonify({"code": code, "message": message}), code
    