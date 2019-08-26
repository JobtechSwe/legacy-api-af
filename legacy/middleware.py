import logging

logger = logging.getLogger(__name__)


class StripContentTypeMiddleware:
    """
    WSGI middleware to strip Content-Type header for GETs and move them to Accept header.
    Necessary due to old api incorrectly specifying content-type to be used for requested return format.
    """
    def __init__(self, app):
        """Create the new middleware.
        Args:
            app: a flask application
        """
        self.app = app

    def __call__(self, environ, start_response):
        """Run the middleware and then call the original WSGI application."""

        if environ['REQUEST_METHOD'] == 'GET':
            try:
                environ['HTTP_ACCEPT'] = environ['CONTENT_TYPE']
                del environ['CONTENT_TYPE']
            except KeyError:
                pass
            else:
                logger.debug('Remove header "Content-Type" from GET request')
        return self.app(environ, start_response)
