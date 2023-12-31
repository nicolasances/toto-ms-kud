from abc import ABCMeta, abstractclassmethod
from flask import Request, abort, jsonify
from config.config import Config
from controller.TotoLogger import TotoLogger
import jwt

from controller.TotoTokenVerifier import TotoTokenVerifier
from controller.model.ExecutionContext import ExecutionContext
from controller.model.UserContext import UserContext
from controller.model.ValidationResult import ValidationResult

class TotoDelegate: 

    @abstractclassmethod
    def do(request: Request, user_context: UserContext, exec_context: ExecutionContext):
        pass

class TotoAPIController: 
    
    def __init__(self) -> None:
        self.config = Config()
        self.logger = TotoLogger(self.config.api_name)
    
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
            dict: a JSONified dictionnary containing the response payload (or the error payload)
        """
        # Extract info 
        cid, _ = self.extract_info(request)
        
        # Validate the request
        validation_result = self.validate_request(request)
        
        if not validation_result.validation_passed: 
            return validation_result.to_flask_response()
        
        # Log the incoming call
        self.logger.log(cid, f"Incoming API Call: {request.method} {request.path}")
        
        # Create a user context object
        user_context = UserContext(validation_result.token_verification_result.user_email)
        
        # Create an execution context object
        execution_context = ExecutionContext(self.config, self.logger, cid)

        # Call the delegate
        return self.delegate.do(request, user_context, execution_context)
    
    
    def extract_info(self, request: Request) -> (str, str):
        """Extracts needed info from the request
        
        Returns cid and auth header
        """
        
        # Extract cid
        cid = request.headers.get("x-correlation-id")
        
        # Extract Authorization header
        auth_header = request.headers.get("Authorization")

        return cid, auth_header
    
    
    def validate_request(self, request: Request) -> ValidationResult: 
        """ Validates the core request data that is mandatory for any call

        Args:
            request (Request): the HTTP request

        Returns:
            ValidationResult: the result of the validation. The flag "validation_passed" will indicate whether the validation was successfull of not
        """
        # Extract needed info
        cid, auth_header = self.extract_info(request)
        
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
        
        # Verify the token
        token_verification = TotoTokenVerifier(cid = cid).verify_token(auth_header_tokens[1])
        
        if token_verification.code != 200: 
            return self.throw_validation_error(cid, token_verification.code, token_verification.message)
        
        return ValidationResult(True, token_verification_result=token_verification)
        
        
    def throw_validation_error(self, cid: str, code: int, message: str, additional_log: str = None): 
        """ Generates a validation error

        Args:
            cid (str): the Correlation Id
            code (int): the HTTP Error Code to use
            message (str): the Message to both log and provide back to the caller
            additional_log (str): a log message to override the default log (e.g. for sensitivity or security reasons)
        """
        self.logger.log(cid, additional_log if additional_log is not None else message)
        
        return ValidationResult(False, error_code = code, error_message = message, cid = cid)
    