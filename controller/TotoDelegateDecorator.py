from flask import Request
from config.config import Config
from controller.TotoLogger import TotoLogger

from controller.TotoTokenVerifier import TotoTokenVerifier
from controller.model.ExecutionContext import ExecutionContext
from controller.model.UserContext import UserContext
from controller.model.ValidationResult import ValidationResult

def toto_delegate(dlg): 
    """Creates a decorator for a Toto Delegate function  

    Args:
        dlg (callable): a function to decorate, that needs to have a signature f(request: Request, user_context: UserContext, exec_context: ExecutionContext)
    """
    
    def delegate_decorator(request: Request): 
        """Decorator for a Toto Delegate function
        
        This decorator performs the following operations: 
        1. Validates mandatory headers: x-correlation-id and Authorization header
        2. Validates JWT token passed as Bearer token in the Authorization header
        3. Creates the User Context to pass it to the delegate
        4. Creates the Execution Context to pass it to the delegate

        Args:
            request (Request): Flask Request object

        Returns:
            any: the returned value from the decorated function or a validation error
        """
        
        config = Config()
        logger = TotoLogger(config.api_name)
        
        # Extract info 
        cid, _ = extract_info(request)
        
        # Validate the request
        validation_result = validate_request(request)
        
        if not validation_result.validation_passed: 
            return validation_result.to_flask_response()
        
        # Log the incoming call
        logger.log(cid, f"Incoming API Call: {request.method} {request.path}")
        
        # Create a user context object
        user_context = UserContext(validation_result.token_verification_result.user_email)
        
        # Create an execution context object
        execution_context = ExecutionContext(config, logger, cid)

        # Call the delegate
        return dlg(request, user_context, execution_context)

    return delegate_decorator


def extract_info(request: Request) -> (str, str):
    """Extracts needed info from the request
    
    Returns cid and auth header
    """
    
    # Extract cid
    cid = request.headers.get("x-correlation-id")
    
    # Extract Authorization header
    auth_header = request.headers.get("Authorization")

    return cid, auth_header

def validate_request(request: Request) -> ValidationResult: 
    """ Validates the core request data that is mandatory for any call

    Args:
        request (Request): the HTTP request

    Returns:
        ValidationResult: the result of the validation. The flag "validation_passed" will indicate whether the validation was successfull of not
    """
    # Extract needed info
    cid, auth_header = extract_info(request)
    
    # Verify that the Correlation Id was provided
    if not cid: 
        return throw_validation_error(cid, 400, "No Correlation ID provided in the Request")
    
    # Verify that an Authorization header was provided
    if not auth_header: 
        return throw_validation_error(cid, 400, "No Authorization header provided in the Request")
    
    # Verify that the Authorization header contains a Bearer Token
    auth_header_tokens = auth_header.split()
    
    if auth_header_tokens[0] != 'Bearer': 
        return throw_validation_error(cid, 400, "Authorization header does not contain a Bearer token")
    
    # Verify the token
    token_verification = TotoTokenVerifier(cid = cid).verify_token(auth_header_tokens[1])
    
    if token_verification.code != 200: 
        return throw_validation_error(cid, token_verification.code, token_verification.message)
    
    return ValidationResult(True, token_verification_result=token_verification)
    
    
def throw_validation_error(cid: str, code: int, message: str, additional_log: str = None, logger: TotoLogger = TotoLogger(None)): 
    """ Generates a validation error

    Args:
        cid (str): the Correlation Id
        code (int): the HTTP Error Code to use
        message (str): the Message to both log and provide back to the caller
        additional_log (str): a log message to override the default log (e.g. for sensitivity or security reasons)
    """
    logger.log(cid, additional_log if additional_log is not None else message)
    
    return ValidationResult(False, error_code = code, error_message = message, cid = cid)
