import requests
import os
from dotenv import load_dotenv

# Load environment variables
# needs to happen before anything else (to properly instantiate constants)
load_dotenv(verbose=True, override=True)

FMS_BASE_URL = os.environ.get('FMS_BASE_URL') #https://dev-fms.apps-madhani.com/api/

RAA_BASE_URL = os.environ.get('RAA_BASE_URL') #https://dev-api.apps-madhani.com/raa/v1/

ESS_BASE_URL = os.environ.get('ESS_BASE_URL') #https://dev-api.apps-madhani.com/ess/v1/

RAA_JWT_SECRET = os.environ.get('RAA_JWT_SECRET') #AaBbCcJKLMadhanirAAnNoOPqrstu23VWXYZ

ESS_JWT_SECRET = os.environ.get('ESS_JWT_SECRET') #AaBbCcJKLMadhaniessnNoOPqrstu23VWXYZ

MTN001M_BASE_URL = os.environ.get('MTN001M_BASE_URL') #https://dev-001m-super.apps-madhani.com/api/jobs

CHAT_BASE_URL = os.environ.get('CHAT_BASE_URL') #https://dev-chat.apps-madhani.com/v1/api/

RAA_TOKEN = os.environ.get('RAA_TOKEN')

ESS_TOKEN = os.environ.get('ESS_TOKEN')

FMS_TOKEN = os.environ.get('FMS_TOKEN')

MTN001M_TOKEN = os.environ.get('MTN_001M_TOKEN')

# Database configuration
DB_CONFIG = {
    "dbname": os.environ.get('DB_NAME'),
    "user": os.environ.get('DB_USERNAME'),
    "password": os.environ.get('DB_PASSWORD'),
    "host": os.environ.get('DB_HOST'),
    "port": os.environ.get('DB_PORT'),
}

DB_CONFIG_TIMEOFF = {
    "dbname": os.environ.get('DB_NAME_TIMEOFF'),
    "user": os.environ.get('DB_USERNAME'),
    "password": os.environ.get('DB_PASSWORD'),
    "host": os.environ.get('DB_HOST'),
    "port": os.environ.get('DB_PORT'),
}

