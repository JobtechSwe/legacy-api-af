import os

# Elasticsearch settings
ES_HOST = os.getenv("ES_HOST", "localhost")
ES_PORT = os.getenv("ES_PORT", 9200)
ES_USER = os.getenv("ES_USER")
ES_PWD = os.getenv("ES_PWD")
ES_INDEX = os.getenv("ES_INDEX", "platsannons-read")
ES_TAX_INDEX = os.getenv("ES_TAX_INDEX", "taxonomy")

# Logo backend setting
COMPANY_LOGO_BASE_URL = os.getenv('COMPANY_LOGO_BASE_URL',
                                  'https://www.arbetsformedlingen.se/rest/arbetsgivare/rest/af/v3/')

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = False
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# APM and Debug settings
APM_SERVICE_NAME = os.getenv("APM_SERVICE_NAME")
APM_SERVICE_URL = os.getenv("APM_SERVICE_URL")
APM_SECRET = os.getenv("APM_SECRET")
APM_LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")

# Key values for platsannons index
WORKPLACE_ADDRESS_MUNICIPALITY_CODE = 'workplace_address.municipality_code'
WORKPLACE_ADDRESS_MUNICIPALITY = 'workplace_address.municipality'
WORKPLACE_ADDRESS_REGION_CODE = 'workplace_address.region_code'
WORKPLACE_ADDRESS_REGION = 'workplace_address.region'
WORKPLACE_ADDRESS_COUNTRY_CODE = 'workplace_address.country_code'
WORKPLACE_ADDRESS_COUNTRY = 'workplace_address.country'
WORKPLACE_ADDRESS_STREET_ADDRESS = 'workplace_address.street_address'
WORKPLACE_ADDRESS_POSTCODE = 'workplace_address.postcode'
WORKPLACE_ADDRESS_CITY = 'workplace_address.city'
WORKPLACE_ADDRESS_COORDINATES = 'workplace_address.coordinates'
OCCUPATION = 'occupation'
OCCUPATION_GROUP = 'occupation_group'
OCCUPATION_FIELD = 'occupation_field'
NUMBER_OF_VACANCIES = 'number_of_vacancies'
PUBLICATION_DATE = 'publication_date'
LAST_PUBLICATION_DATE = 'last_publication_date'
REMOVED = 'removed'
DURATION = 'duration'
EMPLOYMENT_TYPE = 'employment_type'
EMPLOYER_ORGANIZATION_NUMBER = 'employer.organization_number'
DESCRIPTION_TEXT = "description.text"
HEADLINE = "headline"
WORKING_HOURS_TYPE = "working_hours_type"
SALARY_TYPE = 'salary_type'
