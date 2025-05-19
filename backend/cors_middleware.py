import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CORSMiddleware:
    def __init__(self, app):
        self.app = app
        self.allowed_origins = ["http://localhost:5174", "http://localhost:3000", "http://localhost:5173"]
        self.allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allowed_headers = ["Content-Type", "Authorization", "X-Requested-With"]
        
    def __call__(self, environ, start_response):
        # Log the request
        request_method = environ.get('REQUEST_METHOD')
        path_info = environ.get('PATH_INFO')
        origin = environ.get('HTTP_ORIGIN')
        
        logger.info(f"CORS Middleware: {request_method} {path_info} from {origin}")
        
        # Handle OPTIONS request
        if request_method == 'OPTIONS':
            headers = [
                ('Access-Control-Allow-Origin', origin if origin in self.allowed_origins else self.allowed_origins[0]),
                ('Access-Control-Allow-Methods', ', '.join(self.allowed_methods)),
                ('Access-Control-Allow-Headers', ', '.join(self.allowed_headers)),
                ('Access-Control-Allow-Credentials', 'true'),
                ('Access-Control-Max-Age', '3600'),
                ('Content-Type', 'text/plain'),
                ('Content-Length', '0')
            ]
            start_response('200 OK', headers)
            return [b'']
            
        def custom_start_response(status, headers, exc_info=None):
            # Add CORS headers to every response
            cors_headers = []
            if origin in self.allowed_origins:
                cors_headers.append(('Access-Control-Allow-Origin', origin))
            else:
                cors_headers.append(('Access-Control-Allow-Origin', self.allowed_origins[0]))
                
            cors_headers.extend([
                ('Access-Control-Allow-Methods', ', '.join(self.allowed_methods)),
                ('Access-Control-Allow-Headers', ', '.join(self.allowed_headers)),
                ('Access-Control-Allow-Credentials', 'true')
            ])
            
            # Combine original headers with CORS headers
            new_headers = headers + cors_headers
            return start_response(status, new_headers, exc_info)
            
        return self.app(environ, custom_start_response)

