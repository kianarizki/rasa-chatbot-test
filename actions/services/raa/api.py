import requests

import jwt
import logging
from datetime import datetime, timedelta, date
from actions import config

logger = logging.getLogger(__name__)

RAA_KEY = config.RAA_JWT_SECRET

def get_attendace_raa(token_raa,attendace_type):
    try:
        response = requests.get(f"{config.RAA_BASE_URL}attendances?month={datetime.now().strftime('%m-%Y')}", headers={"Authorization":f"Bearer {token_raa}"})
        logger.info(f"Response : {response.json()}")

        if response.status_code == 200:
            data = response.json()
            attendances =  data.get("data", {})
            value = {
                "date": "",
                "nik": "",
                "clockin_time":"",
                "clockout_time":"",
                "project_id_clockin": "",
                "project_name_clockin": "",
                "project_id_clockout": "",
                "project_name_clockout": "",
            }
            for attend in attendances:
                if attendace_type == "today":
                    if attend.get("date","") == datetime.now().strftime("%Y-%m-%d"):
                        value["date"] = attend.get("date", "")
                        value["nik"] = attend.get("nik", "")
                        value["clockin_time"] = "2024-12-13T08:55:28.742562Z"##attend.get("clockin_time", "09:00")
                        value["clockout_time"] = attend.get("clockout_time", "")
                        value["project_id_clockin"] = "001M" #attend.get("project_id_clockin", "001M")
                        value["project_name_clockin"] =  "001M" #attend.get("project_name_clockin", "001M")
                        value["project_id_clockout"] = attend.get("project_id_clockout", "")
                        value["project_name_clockout"] = attend.get("project_name_clockout", "")
                        return value
                    # else:
                    #     return None
                elif attendace_type == "yesterday":
                    yesterday = datetime.now() - timedelta(1)
                    yesterday = datetime.strftime(yesterday, '%Y-%m-%d')
                    if attend.get("date","") == yesterday:
                        value["date"] = attend.get("date", "")
                        value["nik"] = attend.get("nik", "")
                        value["clockin_time"] = "2024-12-12T09:05:10.1315Z" #attend.get("clockin_time", "08:47")
                        value["clockout_time"] = "2024-12-12T17:41:48.1923Z" #attend.get("clockout_time", "17:03")
                        value["project_id_clockin"] = "001S"# attend.get("project_id_clockin", "001S")
                        value["project_name_clockin"] ="001S" #attend.get("project_name_clockin", "001S")
                        value["project_id_clockout"] = "001S"#attend.get("project_id_clockout", "001S")
                        value["project_name_clockout"] = "001S"#attend.get("project_name_clockout", "001S")
                        return value
                    # else:
                    #     return None
                else:
                    value["date"] = attend.get("date", "")
                    value["nik"] = attend.get("nik", "")
                    if (value["project_name_clockin"]!="" or value["project_name_clockout"] !="") \
                        and value["clockin_time"]!="" and value["clockout_time"]!="" :
                        return value

                    if value["project_name_clockin"]=="":
                        value["project_name_clockin"]=attend.get("project_name_clockin", "")
                    if value["project_name_clockout"]== "":
                        value["project_name_clockout"]=attend.get("project_name_clockout", "")
                    if value["clockin_time"]=="":
                        value["clockin_time"]=attend.get("clockin_time", "")
                    if value["clockout_time"]=="":
                        value["clockout_time"]=attend.get("clockout_time", "")
            
            return value
        else:
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error occured while fetching attendance: {e}")
        return None


def get_employee_perf_raa(token_raa, current_month, perf_type, use_dummy_data=False):
    try:
        if use_dummy_data:
            # Data dummy
            dummy_data = {
                "attendance_performance": [
                    {"legend_name": "cuti", "total": 3, "percentage": "15%"},
                    {"legend_name": "izin", "total": 2, "percentage": "10%"},
                    {"legend_name": "alpha/mangkir", "total": 1, "percentage": "5%"},
                    {"legend_name": "hadir", "total": 7, "percentage": "100%"}
                ]
            }
            data = dummy_data
        else:
            month = datetime.now().strftime("%m-%Y") if current_month else (datetime.now() - timedelta(days=31)).strftime("%m-%Y")
            project_id = '2'
            timezone = '7'
            nik = jwt.decode(token_raa, options={"verify_signature": False}).get("iss", "1010")
            logger.info("JWT Payload %s", nik)

            response = requests.get(
                f"{config.RAA_BASE_URL}dashboard/performance/web?month={month}&nik={nik}&project_id={project_id}&timezone={timezone}",
                headers={"Authorization": f"Bearer {token_raa}"}
            )
            logger.info(f"Response Get Perf User RAA : {response.json()}")

            if response.status_code == 200:
                data = response.json()
            else:
                return None

        value = {
            "legend_name": "",
            "total": 0,
            "percentage": "",
        }

        for i in data.get("attendance_performance", []):
            if perf_type == i.get("legend_name", ""):
                value["legend_name"] = i.get("legend_name", "")
                value["total"] = i.get("total", 0)
                value["percentage"] = i.get("percentage", "")
                break

        logger.info(f"VALUE: {value}")
        return value

    except Exception as e:
        logger.error(f"Error occurred while fetching attendance: {e}")
        return None


def get_project_sites_raa(token_raa):
    try:
        response = requests.get(f"{config.RAA_BASE_URL}projects", headers={"Authorization":f"Bearer {token_raa}"})
        logger.info(f"Response Get Projects Madhani RAA : {response.json()}")
     
        if response.status_code == 200:
            data = response.json()
            value = []
            for i in data.get("data", []):
                if i.get("name",None):
                    value.append(i.get("name"))
            logger.info(f"VALUE {value}")
            return value
        else:
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error occured while fetching attendance: {e}")
        return None

def get_user_profile_raa(token_raa):
    try:
        response = requests.get(f"{config.RAA_BASE_URL}profiles", headers={"Authorization":f"Bearer {token_raa}"})
        logger.info(f"Response Get Profile User RAA : {response.json()}")
     
        if response.status_code == 200:
            data = response.json()
            value = {
                "role_name":"",
                "department_name" : "",
                "project_name":"",
                "position_name":"",
                "email":"",
                "password":"",
                "phone":"",
                "nomor_wa":"",
                "date_of_hire":""
            }
            data = data.get("data",{})

            if data!={}:
                value["role_name"] = data.get("role_name", "")
                value["department_name"] = data.get("departement_name", "")
                value["project_name"] = data.get("project_name", "")
                value["position_name"] = data.get("position_name", "")
                value["email"] = data.get("email", "")
                value["password"] = data.get("password", "")
                value["phone"] = data.get("phone", "")
                value["nomor_wa"] = data.get("nomor_wa", "")
                value["date_of_hire"] = data.get("date_of_hire", "")
            logger.info(f"VALUE {value}")
            return value
        else:
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error occured while fetching attendance: {e}")
        return None
    
def get_information_all_position_raa(token_raa):
    try:
        response = requests.get(f"{config.RAA_BASE_URL}positions", headers={"Authorization":f"Bearer {token_raa}"})
        logger.info(f"Response Get ALL Positions RAA : {response.json()}")
     
        if response.status_code == 200:
            data = response.json()
            value = []
            data = data.get("data",[])
            for i in data:
                value.append(i.get("name",""))
            logger.info(f"VALUE {value}")
            return value
        else:
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error occured while fetching attendance: {e}")
        return None
    
def get_information_all_departments_raa(token_raa):
    try:
        response = requests.get(f"{config.RAA_BASE_URL}departements", headers={"Authorization":f"Bearer {token_raa}"})
        logger.info(f"Response Get ALL Departments RAA : {response.json()}")
     
        if response.status_code == 200:
            data = response.json()
            value = []
            data = data.get("data",[])
            for i in data:
                value.append(i.get("name",""))
            logger.info(f"VALUE {value}")
            return value
        else:
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error occured while fetching attendance: {e}")
        return None

def get_raa_token(tracker):
    events = tracker.events[::-1]
    for e in events:
        token_raa = e.get('metadata', {}).get('token_raa', None)
        if token_raa:
            return token_raa

    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uX2lkIjoiMzliYTgxODUtZjI5My00NTJiLWEwZjEtMDBjYWEzNTMxNzMwIiwibGV2ZWwiOiIxIiwicGVybWlzc2lvbnMiOnsiMSI6dHJ1ZSwiMTAiOnRydWUsIjE4Ijp0cnVlLCIxOSI6dHJ1ZSwiMiI6dHJ1ZSwiMjAiOnRydWUsIjIxIjp0cnVlLCIyMiI6dHJ1ZSwiMjMiOnRydWUsIjI3Ijp0cnVlLCIyOCI6dHJ1ZSwiMjkiOnRydWUsIjMiOnRydWUsIjQiOnRydWUsIjUiOnRydWUsIjYiOnRydWUsIjciOnRydWUsIjgiOnRydWUsIjkiOnRydWV9LCJleHAiOjE3NDkwOTEwOTMsImlzcyI6IjEwMTAifQ.iuffrmH02GhVt_7zd1dhwBcMfVhq6LKwsqQBFs--yNM"

def get_raa_token_api(token_ess):
    headers = {
        'Authorization': f'Bearer {token_ess}',
        'Content-Type': 'application/json'
    }
    response = requests.get(f'{config.RAA_BASE_URL}login', headers=headers)
    if response.status_code == 200:
        data = response.json()
        token_raa = data.get('data', {}).get('token_raa', None)
        if token_raa is not None:
            return token_raa
        return None
    else:
        return None



