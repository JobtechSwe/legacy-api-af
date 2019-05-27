import logging
from flask import Flask
from flask_cors import CORS
from elasticapm.contrib.flask import ElasticAPM
from jobtech.common.customlogging import configure_logging
from legacy.rest import api
from legacy import settings
# Import all Resources that are to be made visible for the app
from legacy.rest.endpoints import SoklistaLan

app = Flask(__name__)
CORS(app)
configure_logging([__name__.split('.')[0], 'sokannonser', 'jobtech'])
log = logging.getLogger(__name__)
log.info(logging.getLevelName(log.getEffectiveLevel()) + ' log level activated')
log.info("Starting %s" % __name__)


def configure_app(flask_app):
    flask_app.config.SWAGGER_UI_DOC_EXPANSION = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config.RESTPLUS_VALIDATE = settings.RESTPLUS_VALIDATE
    flask_app.config.RESTPLUS_MASK_SWAGGER = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config.ERROR_404_HELP = settings.RESTPLUS_ERROR_404_HELP
    if settings.APM_SERVICE_NAME and settings.APM_SERVICE_URL and settings.APM_SECRET:
        flask_app.config['ELASTIC_APM'] = {
            'SERVICE_NAME': settings.APM_SERVICE_NAME,
            'SERVER_URL': settings.APM_SERVICE_URL,
            'SECRET_TOKEN': settings.APM_SECRET
        }
        apm = ElasticAPM(flask_app, logging=logging.INFO)
        log.info("ElasticAPM enabled")
        log.debug("APM details: %s" % str(apm))
    else:
        log.info("ElasticAPM is disabled")


def initialize_app(flask_app, api):
    configure_app(flask_app)
    api.init_app(flask_app)


if __name__ == '__main__':
    # Used only when starting this script directly, i.e. for debugging
    initialize_app(app, api)
    app.run(debug=True)
else:
    # Main entrypoint
    initialize_app(app, api)
