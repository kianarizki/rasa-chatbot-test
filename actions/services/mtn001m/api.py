import requests

import logging
from datetime import datetime, timedelta, date
from actions import config
import jwt

logger = logging.getLogger(__name__)


def get_001m_token(tracker):
    events = tracker.events[::-1]
    for e in events:
        token_fms = e.get('metadata', {}).get('token_fms', None)
        if token_fms:
            return token_fms

    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDQ3NzAyMjQsImlzcyI6IjEwMTAiLCJ1c2VyIjp7Im5payI6IjEwMTAiLCJuYW1lIjoiUHJpc2NhIEF1ZHlhIFRyaSBDYWh5YSBBbmdncmFldGEiLCJyb2xlX2lkIjoiMSIsInBlcm1pc3Npb25zIjpbMSwyLDMsNCw1LDYsNyw4LDksMTAsMTEsMTIsMTMsMTQsMTUsMTYsMTcsMTgsMTksMjAsMjEsMjIsMjMsMjQsMjUsMjYsMjcsMjgsMjksMzAsMzEsMzIsMzMsMzQsMzUsMzYsMzcsMzgsMzksNDAsNDEsNDIsNDMsNDQsNDUsNDYsNDcsNDgsNDksNTAsNTEsNTIsNTMsNTQsNTUsNTYsNTcsNTgsNTksNjAsNjEsNjIsNjMsNjQsNjUsNjgsNjksNzAsNzEsNzIsNzQsNzUsNzYsNzcsNzgsNzksODAsODEsODIsODQsODUsODYsODgsODksOTAsOTEsOTIsOTMsOTQsOTUsOTYsOTcsOTgsOTksMTAwLDEwMSwxMDIsMTAzLDEwNCwxMDUsMTA2LDEwNywxMDgsMTA5LDExMCwxMTEsMTEyLDExMywxMTQsMTE1LDExNiwxMTcsMTE4LDExOSwxMjIsMTIzLDEyNCwxMjUsMTI2LDEyNywxMjgsMTI5LDEzMCwxMzEsMTMyLDEzMywxMzYsMTM3LDEzOSwxNDBdfX0.hNLDnRtYm1EhxIS6o9tyDAO8j33iTZWQoaZJWb2-niI"

def get_001m_report_daily_internal(token_001m:str,daily_report_date="", search="", status_process="", manufacturer="", model="", component_description="",limit="",page=""):
    url = f"{config.MTN001M_BASE_URL}/jobs/daily-report?daily-report-date={daily_report_date}&search={search}&status-process={status_process}&manufacturer={manufacturer}&model={model}&component-description={component_description}&limit={limit}&page={page}"
    logger.info(f"Fetching {url}")

    try:
        response = requests.get(url, headers={"cookie":f"token_001m={token_001m}"})
        logger.info(f"Response GET Daily Report Internal 001M : {response.json()}")
        if response.status_code == 200:
            data = response.json()
            data = data.get("data",[])
            return data
        else:
            logger.warning(f"Failed to fetch daily report internal {response.json()}")
            return None
    except Exception as e:
        logger.error(f"Error occured while fetching daily report internal: {e}")
        return None

def get_001m_report_daily_external(token_001m:str,daily_report_date="", search="", status_process="", manufacturer="", model="", component_description="",limit="",page=""):
    url = f"{config.MTN001M_BASE_URL}/jobs/daily-report/external?daily-report-date={daily_report_date}&search={search}&status-process={status_process}&manufacturer={manufacturer}&model={model}&component-description={component_description}&limit={limit}&page={page}"
    logger.info(f"Fetching {url}")

    try:
        response = requests.get(url, headers={"cookie":f"token_001m={token_001m}"})
        logger.info(f"Response GET Daily Report External 001M : {response.json()}")
        if response.status_code == 200:
            data = response.json()
            data = data.get("data",[])
            return data
        else:
            logger.warning(f"Failed to fetch daily report external {response}")
            return None
    except Exception as e:
        logger.error(f"Error occured while fetching daily report external: {e}")
        return None



def get_001m_model_manufacturers(token_001m:str):
    url = f"{config.MTN001M_BASE_URL}/models/manufacturers"

    default_data = [
        {
            "id": "6",
            "name": "GENERAL|GENERAL",
            "created_at": "2025-02-05T09:37:40.147063Z",
            "updated_at": "2025-02-05T09:37:40.147063Z"
        },
        {
            "id": "5",
            "name": "SYN-TOYOTA",
            "created_at": "2024-10-29T09:05:05.879507Z",
            "updated_at": "2024-10-29T09:05:05.879507Z"
        },
        {
            "id": "4",
            "name": "KOMATSU",
            "created_at": "2024-10-28T02:23:45.781357Z",
            "updated_at": "2024-10-28T02:42:15.685955Z"
        },
        {
            "id": "2",
            "name": "TESTQA",
            "created_at": "2024-08-28T08:01:02.905625Z",
            "updated_at": "2024-08-28T08:01:02.905625Z"
        },
        {
            "id": "1",
            "name": "CATERPILLAR",
            "created_at": "2024-08-14T05:21:32.00425Z",
            "updated_at": "2024-08-14T05:21:32.00425Z"
        }
    ]

    try:
        response = requests.get(url, headers={"cookie":f"token_001m={token_001m}"})
        logger.info(f"Response GET Daily Report Internal 001M : {response.json()}")
     
        if response.status_code == 200:
            data = response.json()
            data = data.get("data",[])
            return data
        else:
            return default_data
    except Exception as e:
        logger.error(f"Error occured while fetching daily report internal: {e}")
        return default_data
    

def get_001m_model_dropdown(token_001m:str):
    url = f"{config.MTN001M_BASE_URL}/models-dropdown"

    default_data = [
            {
                "id": "6",
                "name": "GENERAL|GENERAL",
                "manufacturer": {
                    "id": "6",
                    "name": "GENERAL|GENERAL"
                },
                "created_at": "2025-02-05T09:37:40.15092Z",
                "updated_at": "2025-02-05T09:37:40.150921Z"
            },
            {
                "id": "5",
                "name": "SYN-FORTUNER",
                "manufacturer": {
                    "id": "5",
                    "name": "SYN-TOYOTA"
                },
                "created_at": "2024-10-29T09:05:17.172677Z",
                "updated_at": "2024-10-29T09:05:17.172677Z"
            },
            {
                "id": "4",
                "name": "PCX200 EXCAVATOR",
                "manufacturer": {
                    "id": "4",
                    "name": "KOMATSU"
                },
                "created_at": "2024-10-28T02:35:34.200862Z",
                "updated_at": "2024-10-31T00:40:20.447514Z"
            },
            {
                "id": "3",
                "name": "TEST:MODELS",
                "manufacturer": {
                    "id": "2",
                    "name": "TESTQA"
                },
                "created_at": "2024-09-02T03:57:36.102335Z",
                "updated_at": "2024-09-02T03:57:36.102336Z"
            },
            {
                "id": "2",
                "name": "2TEST2MODEL",
                "manufacturer": {
                    "id": "2",
                    "name": "TESTQA"
                },
                "created_at": "2024-08-28T08:01:19.209893Z",
                "updated_at": "2024-08-28T08:01:19.209894Z"
            },
            {
                "id": "1",
                "name": "777D",
                "manufacturer": {
                    "id": "1",
                    "name": "CATERPILLAR"
                },
                "created_at": "2024-08-14T05:21:32.007595Z",
                "updated_at": "2024-08-14T05:21:32.007595Z"
            }
        ]

    try:
        response = requests.get(url, headers={"cookie":f"token_001m={token_001m}"})
        logger.info(f"Response GET Daily Report Internal 001M : {response.json()}")
     
        if response.status_code == 200:
            data = response.json()
            data = data.get("data",[])
            return data.get("models",[])
        else:
            return default_data
    except Exception as e:
        logger.error(f"Error occured while fetching daily report internal: {e}")
        return default_data    
    

def get_001m_component_description(token_001m:str):
    url = f"{config.MTN001M_BASE_URL}/models-dropdown"

    default_data = [
            {
                "id": "1",
                "name": "TRANSMISSION",
                "created_at": "2024-08-14T05:21:32.010323Z",
                "updated_at": "2024-08-14T05:21:32.010323Z"
            },
            {
                "id": "2",
                "name": "TORQUE CONVERTER",
                "created_at": "2023-07-10T16:35:04.563Z",
                "updated_at": "2023-07-10T16:35:04.563Z"
            },
            {
                "id": "3",
                "name": "FINAL DRIVE",
                "created_at": "2023-07-10T16:35:04.563Z",
                "updated_at": "2023-07-10T16:35:04.563Z"
            },
            {
                "id": "4",
                "name": "ENGINE",
                "created_at": "2024-08-14T05:21:32.067465Z",
                "updated_at": "2024-08-14T05:21:32.067465Z"
            },
            {
                "id": "5",
                "name": "DIFFERENTIAL",
                "created_at": "2024-08-14T05:21:32.067465Z",
                "updated_at": "2024-08-14T05:21:32.067465Z"
            },
            {
                "id": "6",
                "name": "FINAL DRIVE & WHEEL BRAKE",
                "created_at": "2024-08-14T05:21:32.067465Z",
                "updated_at": "2024-08-14T05:21:32.067465Z"
            },
            {
                "id": "7",
                "name": "LIFT/HOIST CYLINDER",
                "created_at": "2024-08-14T05:21:32.067465Z",
                "updated_at": "2024-08-14T05:21:32.067465Z"
            },
            {
                "id": "8",
                "name": "STEERING CYLINDER",
                "created_at": "2024-08-14T05:21:32.067465Z",
                "updated_at": "2024-08-14T05:21:32.067465Z"
            },
            {
                "id": "9",
                "name": "FRONT SUSPENSION CYLINDER",
                "created_at": "2024-08-14T05:21:32.067465Z",
                "updated_at": "2024-08-14T05:21:32.067465Z"
            },
            {
                "id": "10",
                "name": "REAR SUSPENSION CYLINDER",
                "created_at": "2024-08-14T05:21:32.067465Z",
                "updated_at": "2024-08-14T05:21:32.067465Z"
            },
            {
                "id": "11",
                "name": "ENGINE C15",
                "created_at": "2024-08-14T05:21:32.067465Z",
                "updated_at": "2024-08-14T05:21:32.067465Z"
            },
            {
                "id": "12",
                "name": "ENGINE 3406",
                "created_at": "2024-08-14T05:21:32.067465Z",
                "updated_at": "2024-08-14T05:21:32.067465Z"
            },
            {
                "id": "13",
                "name": "BRAKER & DIFFERENTIAL DRIVE GP",
                "created_at": "2024-08-14T05:21:32.067465Z",
                "updated_at": "2024-08-14T05:21:32.067465Z"
            },
            {
                "id": "15",
                "name": "TESTADDCOMP",
                "created_at": "2024-10-26T08:49:24.369131Z",
                "updated_at": "2024-10-26T08:49:24.369132Z"
            },
            {
                "id": "16",
                "name": "ADADAD",
                "created_at": "2024-10-26T08:50:26.77358Z",
                "updated_at": "2024-10-26T08:50:26.77358Z"
            },
            {
                "id": "17",
                "name": "119020",
                "created_at": "2025-02-05T09:37:40.137612Z",
                "updated_at": "2025-02-05T09:37:40.137612Z"
            }
        ]

    try:
        response = requests.get(url, headers={"cookie":f"token_001m={token_001m}"})
        logger.info(f"Response GET Daily Report Internal 001M : {response.json()}")
     
        if response.status_code == 200:
            data = response.json()
            data = data.get("data",[])
            return data.get("part_types",[])
        else:
            return default_data
    except Exception as e:
        logger.error(f"Error occured while fetching daily report internal: {e}")
        return default_data        
    


def get_001m_internal_status_process(token_001m:str,tracker):
    current_jobs = tracker.active_loop.get("name","")
    logger.info(f"Current Jobs: {current_jobs}")
    url = f"{config.MTN001M_BASE_URL}/jobs/status-process"
    if "external" in current_jobs:
        url = f"{config.MTN001M_BASE_URL}/jobs/external/status-process"

    default_data = [
        {
            "id": "1",
            "name": "Waiting Approval Register",
            "type": "internal"
        },
        {
            "id": "2",
            "name": "Receive",
            "type": "internal"
        },
        {
            "id": "3",
            "name": "Disassembly",
            "type": "internal"
        },
        {
            "id": "4",
            "name": "Measurement",
            "type": "internal"
        },
        {
            "id": "5",
            "name": "Pre Order",
            "type": "internal"
        },
        {
            "id": "31",
            "name": "RF Part/Repair List",
            "type": "grey_area"
        },
        {
            "id": "32",
            "name": "RF Approve",
            "type": "grey_area"
        },
        {
            "id": "33",
            "name": "Vendor Selected",
            "type": "grey_area"
        },
        {
            "id": "34",
            "name": "Waiting Quotation",
            "type": "grey_area"
        },
        {
            "id": "35",
            "name": "Approve Quotation",
            "type": "grey_area"
        },
        {
            "id": "36",
            "name": "Input Part List Into AMT",
            "type": "grey_area"
        },
        {
            "id": "37",
            "name": "Waiting PO MTN Approve",
            "type": "grey_area"
        },
        {
            "id": "38",
            "name": "PO MTN Approve",
            "type": "grey_area"
        },
        {
            "id": "39",
            "name": "Waiting Parts/Repairs",
            "type": "grey_area"
        },
        {
            "id": "40",
            "name": "Parts Ready to Assembly",
            "type": "grey_area"
        },
        {
            "id": "6",
            "name": "Assembly",
            "type": "internal"
        },
        {
            "id": "7",
            "name": "Test Performance",
            "type": "internal"
        },
        {
            "id": "8",
            "name": "Quality Assurance & Quality Control",
            "type": "internal"
        }
    ]

    try:
        response = requests.get(url, headers={"cookie":f"token_001m={token_001m}"})
        logger.info(f"Response GET Daily Report Internal 001M : {response.json()}")

        if response.status_code == 200:
            data = response.json()
            data = data.get("data",[])
            return data
        else:
            return default_data
    except Exception as e:
        logger.error(f"Error occured while fetching daily report internal: {e}")
        return default_data        
    
from datetime import datetime
from babel.dates import format_datetime


def reformat_date(datestr, lang="indonesia") -> str:
    locale = "id" if lang == "indonesia" else "en"
    
    try:
        dt = datetime.fromisoformat(datestr.replace('Z', '+00:00'))

        if locale=="en":
            english_format = format_datetime(
                dt, 
                format='full',  
                locale='en_US'
            )

            return english_format

        indonesian_format = format_datetime(
        dt,
        format='full',  
        locale='id_ID'
    )   
        return indonesian_format
    except Exception as e:
        return "-"

def get_001m_forecast_allocation_report(token_001m:str, start_date='',end_date='',manufacturer='',model='',comp_description='',site_allocation='',search=''):
    
    
    url = f"{config.MTN001M_BASE_URL}/jobs/forecast-allocation-report?start_date={start_date}&end_date={end_date}&manufacturer={manufacturer}&model={model}&component-description={comp_description}&site_allocation={site_allocation}&search={search}"
    try:
        response = requests.get(url, headers={"cookie":f"token_001m={token_001m}"})
        logger.info(f"{url} :Response GET Jobs Forecast Allocation Report 001M : {response.json()}")

        if response.status_code == 200:
            data = response.json()
            data = data.get("data",[])
            return data
        else:
            return []
    except Exception as e:
        logger.error(f"Error occured while fetching daily report internal: {e}")
        return None

def get_001m_site_allocation(token_001m:str, tracker):
    url = f"{config.MTN001M_BASE_URL}/shipment-tracking/site-allocation"
    try:
        response = requests.get(url, headers={"cookie":f"token_001m={token_001m}"})
        logger.info(f"Response GET Site Allocation 001M : {response.json()}")
        default_data = [
            {
                "name":"001Z",
                "id"  :"4"
            },
            {
                "name":"020D",
                "id"  : "5"
            }
        ]
        if response.status_code == 200:
            data = response.json()
            data = data.get("data",[])
            return data
        else:
            return default_data
    except Exception as e:
        logger.error(f"Error occured while fetching site allocation: {e}")
        return default_data        
