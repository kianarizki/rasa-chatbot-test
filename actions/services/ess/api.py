import requests
import logging
from datetime import datetime, timedelta, date, timezone
from actions import config
import jwt
import psycopg2
import json

logger = logging.getLogger(__name__)

ESS_KEY = config.ESS_JWT_SECRET


def get_ess_token(tracker):
    events = tracker.events[::-1]
    for e in events:
        token_ess = e.get('metadata', {}).get('token_ess', None)
        if token_ess:
            return token_ess
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uX2lkIjoiY2IzOTczZjctOTVkZS00Nzk1LTljMDYtMzhhOTBjMjZlYTIzIiwiYWxsb3dlZF9hcHBzIjpbIk1PQ0EiLCJMTVMtT1BEIiwiMDAxTSIsIkxNUyIsIkVTUyIsIlJBQSIsIk1FRElDIiwiVENTIiwiTE1TLU9QRC1BRE1JTiIsIlNDTSJdLCJsZXZlbCI6IjEiLCJwZXJtaXNzaW9ucyI6WzEsMTMsMTQsMTUsMjIsMjMsMjQsMjUsMjYsMjcsMjgsMjksMzAsMzEsMzIsMzMsMzQsMzUsMzYsMzcsMzksNDAsNDEsNDIsNDMsNDQsNDVdLCJleHAiOjE3NDEwNTI2NTEsImlzcyI6IjEwMTAifQ.hwq_hHfvnGJSSGQWSOvSFmmaecLm5OexEwKAdMe-1Ag"

## 
def generate_ess_token_by_nik(NIK : str):
    try:
        sample_payload = {
            "allowed_apps": [
                "ESS",
                "RAA",
                "TCS"
            ],
            "level": "-999",
            "permissions": [],
            "exp": int((datetime.now(timezone.utc) + timedelta(seconds=360)).timestamp()),
            "iss": NIK
            }
        token = jwt.encode(sample_payload, ESS_KEY, algorithm="HS256")
        return token
    except Exception as e:
        logger.error(f"Error occured while generating token: {e}")
        return None



def get_level_from_token(token: str):
    try:
        decoded_token = jwt.decode(token, ESS_KEY, algorithms=["HS256"])
        return int(decoded_token.get("level",1))
    except jwt.exceptions.InvalidTokenError as e:
        logger.error(f"Error decoding token {e}")
        return None

def get_profile_ess(token_ess):
    try:
        response = requests.get(f"{config.ESS_BASE_URL}profiles", headers={"Authorization": f"Bearer {token_ess}"})
        logger.info(f"Response : {response.json()}")

        if response.status_code == 200:
            data = response.json()

            if data.get("status") and "data" in data:
                profile_data = data.get("data", {})
                
                def safe_get(d, *keys):
                    for key in keys:
                        d = d.get(key, {}) if isinstance(d, dict) else {}
                    return d if d else None

                profile = {
                    "id": profile_data.get("id"),
                    "nik": profile_data.get("nik"),
                    "name": profile_data.get("name"),
                    "email": profile_data.get("email"),
                    "image_profile": profile_data.get("image_profile"),
                    "finger_id": profile_data.get("finger_id"),
                    "status_project": profile_data.get("status_project"),
                    "gender": {
                        "id": safe_get(profile_data, "gender", "id"),
                        "name": safe_get(profile_data, "gender", "name")
                    },
                    "religion": {
                        "id": safe_get(profile_data, "religion", "id"),
                        "name": safe_get(profile_data, "religion", "name")
                    },
                    "role": {
                        "id": safe_get(profile_data, "role", "id"),
                        "name": safe_get(profile_data, "role", "name")
                    },
                    "project": {
                        "id": safe_get(profile_data, "project", "id"),
                        "name": safe_get(profile_data, "project", "name")
                    },
                    "departement": {
                        "id": safe_get(profile_data, "departement", "id"),
                        "name": safe_get(profile_data, "departement", "name")
                    },
                    "position": {
                        "id": safe_get(profile_data, "position", "id"),
                        "name": safe_get(profile_data, "position", "name")
                    },
                    "level": {
                        "id": safe_get(profile_data, "level", "id"),
                        "name": safe_get(profile_data, "level", "name")
                    },
                    "project_name": profile_data.get("project_name"),
                    "is_approver": profile_data.get("is_approver")
                }
                return profile
            else:
                logger.error("Invalid response structure or status is false")
                return None

        else:
            logger.error(f"Unexpected status code: {response.status_code}, Message: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error occurred while fetching profile: {e}")
        return None


def get_timeoff_ess(token_ess,leave_type):
    try:
        response = requests.get(f"{config.ESS_BASE_URL}timeoff/user/leave-quota", headers={"Authorization":f"Bearer {token_ess}"})
        logger.info(f"Response : {response.json()}")
   
        if response.status_code == 200:
            data = response.json()

            quota_types = ["big_quotas", "yearly_quotas", "outstanding_quotas", "subtitute_quotas"]
            all_quotas = {}

            for quota_type in quota_types:
                quotas = data.get("data",{}).get(quota_type, [])
                if quotas is not None:
                    for quota in quotas:
                        all_quotas[quota["quota_id"]] = {
                            "quota_type": quota_type,
                            "quota": quota["quota"],
                            "expired": quota["expired"]
                        }
            return all_quotas
        else:
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error occured while fetching attendance: {e}")
        return None
    
def get_timeoff_latest_user_ess(token_ess, status_type):
    try:

        response = requests.get(f"{config.ESS_BASE_URL}timeoff/user/all?page=1&limit=1", headers={"Authorization":f"Bearer {token_ess}"})
        logger.info(f"Response Get TimeOFF Latest User ESS : {response.json()}")
     
        if response.status_code == 200:
            data = response.json()
            value = {
                "created_at":"" ,
                "status":"",
                "request_date":"",
                "approval_date":"",
                "time_off_type":"",
                "reason":"",
                "approved_by":""
            }
            for i in data.get("data", []):
                value['status'] = i.get("status","")
                value["reason"]  = i.get("reason","")
                data_timeoff  = i.get("data_time_off",[])
                if data_timeoff:
                    value["request_date"] = data_timeoff[0].get("request_date","")
                    value["time_off_type"] = data_timeoff[0].get("time_off_type","")

                approval  = i.get("approval",[])
                if approval!=[]:
                    value["approval_date"] = approval[0].get("approval_date","")
                    value["approved_by"] = approval[0].get("approved_by","")

            logger.info(f"VALUE {value}")
            return value
        else:
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error occured while fetching attendance: {e}")
        return None

def get_approval_leave_off_ess(token_ess):
    try:
        # API call to fetch data
        response = requests.get(
            f"{config.ESS_BASE_URL}timeoff/user/timeoff-approver",
            headers={"Authorization": f"Bearer {token_ess}"}
        )
        logger.info(f"Response Get Approval Leave Off ESS : {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            value = {
                "data": [],
                "message": ""
            }

            # Extract the list of approvers
            approvers = data.get("data", [])
            
            if not approvers:
                logger.warning("No approvers found in the response.")
                return None
            
            profile = get_profile_ess(token_ess)
            deparment_id = profile['departement']['id']
            project_id = profile['project']['id']
            designated_person = get_designated_person(deparment_id,project_id, token_ess)
            
            for approver in approvers:
                temp = {
                    "id": approver.get("id", "N/A"),
                    "level_id": approver.get("level_id", -1),
                    "level_name": approver.get("level_name", "N/A"),
                    "sequence": approver.get("sequence", -1),
                    "designated_person": []
                }
                if approver.get("designated_person",None):
                    temp['designated_person'].append({
                        "nik": approver.get('designated_person').get("nik"),
                        "name": approver.get('designated_person').get("name"),
                        "image_profile": approver.get('designated_person').get("image_profile"),
                        "role_name": approver.get('designated_person').get("role_name"),
                        "department_name": approver.get('designated_person').get("department_name"),
                        "position_name": approver.get('designated_person').get("position_name"),
                        "project_name": approver.get('designated_person').get("project_name"),
                        "status_project": approver.get('designated_person').get("status_project"),
                        "level_name": approver.get('designated_person').get("level_name"),
                    })
                    value["data"].append(temp)

                    continue


                for dp in designated_person: 
                    if temp['level_name'] == dp['level_name']:
                        temp['designated_person'].append(dp)
                        # break
                        
                value["data"].append(temp)

            # Assuming reason is consistent across all approvers
            value["message"] = data.get("message", "N/A")

            logger.info(f"Processed Value: {value}")
            return value
        else:
            logger.error(f"Failed to fetch data, status code: {response.status_code}")
            return None
        # value = {'data': [{'id': '', 'level_id': 4, 'level_name': 'Superintendent', 'sequence': 1, 'designated_person': [{'nik': 'ALV01', 'name': 'L. Alvarado', 'image_profile': 'https://assets.apps-madhani.com/ess/user/648809fe-9ca9-4287-a4b4-bddee3c84e46.jpg', 'role_name': 'Project Manager', 'department_name': 'HSE', 'position_name': 'HSE Superintendent', 'project_name': '001M', 'status_project': 'dedicated', 'level_name': 'Superintendent'}]}, {'id': '', 'level_id': 3, 'level_name': 'Supervisor', 'sequence': 2, 'designated_person': [{'nik': 'HRS1D', 'name': 'HR Site 001D', 'image_profile': '', 'role_name': 'HR Site', 'department_name': 'Board & GM', 'position_name': 'General Manager Plant', 'project_name': '001D', 'status_project': 'dedicated', 'level_name': 'Supervisor'}, {'nik': 'LEVI123', 'name': 'Leviathan', 'image_profile': 'https://assets.apps-madhani.com/ess/user/8b8be963-fcf3-46d4-bd8c-02a3ad3f00fc.jpg', 'role_name': 'HR Head Office', 'department_name': 'Board & GM', 'position_name': 'President Director', 'project_name': '001D', 'status_project': 'dedicated', 'level_name': 'Supervisor'}, {'nik': 'ROY32', 'name': 'Royan Supervisor', 'image_profile': '', 'role_name': 'HR Head Office', 'department_name': 'Board & GM', 'position_name': 'Corporate Director', 'project_name': '001D', 'status_project': 'dedicated', 'level_name': 'Supervisor'}]}, {'id': '', 'level_id': 2, 'level_name': 'Foreman', 'sequence': 3, 'designated_person': [{'nik': 'NICK03', 'name': 'NICK03', 'image_profile': 'https://assets.apps-madhani.com/ess/', 'role_name': 'User', 'department_name': 'HRGA', 'position_name': 'HRGA Officer', 'project_name': '001D', 'status_project': 'dedicated', 'level_name': 'Foreman'}]}], 'message': 'success'}
        # return value
    except Exception as e:
        logger.error(f"Error occurred while fetching approval leave off data: {e}")
        return None


def post_approval_leave_off(token_ess, leave_req_type, leave_req_date_from, leave_req_date_until, leave_req_reason, approval_nik):
    logger.info(f"Leave Req Type {leave_req_type}")
    logger.info(f"Leave Req Date From {leave_req_date_from}")
    logger.info(f"Leave Req Date Until {leave_req_date_until}")
    logger.info(f"Leave Req Reason {leave_req_reason}")
    logger.info(f"Approval NIK {approval_nik}")

    req_type = {
        "cuti pengganti hari": 1,
        "cuti tahunan": 2,
        "cuti besar": 3,
    }
    
    url = f"{config.ESS_BASE_URL}timeoff/create"
    headers = {"Authorization": f"Bearer {token_ess}", "Content-Type": "application/json"}            
    # profile = get_profile_ess(token_ess)
    approvers = get_approval_leave_off_ess(token_ess)
    selected_approvers=[]
    cnt = 1
    for approver in approvers['data']:
        if approver.get("designated_person",None):
            for dp in approver.get("designated_person"): 
                if dp['nik'] in approval_nik:
                    dp['level_id'] = get_profile_ess(generate_ess_token_by_nik(dp['nik']))['level']['id']
                    dp['sequence'] = cnt
                    selected_approvers.append({
                       "level_id": dp['level_id'],
                        "level_name":dp['level_name'],
                        "sequence":dp['sequence'],
                        "nik": dp['nik']
                    })
                    cnt += 1


    logger.info(f"SELECTED approfer {selected_approvers}")
    if selected_approvers == None or len(selected_approvers )== 0:
        return {
            "success": False,
            "message_en": "No approvers found to approve the leave request.",
            "message_id": "Tidak ada approval yang terdapat pada akun anda."
        }

    req_body = {
        "task_transfer": "",
        "nik_approver": "",
        "reason": leave_req_reason,
        "cuti": [
            {
                "id": 0,
                "request_date": leave_req_date_from,
                "end_requested_date": leave_req_date_until,
                "hospital": "",
                "attachment": [],
                "child_name": "",
                "family_name": "",
                "time_off_type_id": req_type[leave_req_type],
                "time_off_category": None,
                "from_time": "",
                "to_time": ""
            }
        ],
        "approvals": selected_approvers,
    }

    req_body = json.dumps(req_body)
    logger.info(f"Request Body: {req_body}")
    try:
        response = requests.post(
        url=url,
        headers=headers,
        data=req_body,
        
    )
        logger.info(f"Response Post Approval Leave Off ESS : {response.json()}")
        if response.status_code == 201:
            return {
                "success": True,
                "message_en": "Leave request has been submitted successfully😊",
                "message_id": "Permintaan cuti telah berhasil dikirim😊"
            }
        else :
            return {
                "success": False,
                "message_en": f"Failed to submit leave request, status code: {response.status_code}",
                "message_id": f"Gagal mengirim permintaan cuti, status kode: {response.status_code}"
            }  
    except Exception as e:
        logger.error(f"Error occurred while fetching approval leave off data: {e}")
        return {
                "success": False,
                "message_en": f"Failed to submit leave request, status code: {response.status_code}",
                "message_id": f"Gagal mengirim permintaan cuti, status kode: {response.status_code}"
            }  

def get_designated_person(departement_id: int, project_id: int,token_ess):
    try:
        response = requests.get(f"{config.ESS_BASE_URL}timeoff/user/designated-person?department_id={departement_id}&project_id={project_id}", headers={"Authorization": f"Bearer {token_ess}"})
        logger.info(f"Response: {response.json()}")

        if response.status_code == 200:
            data = response.json()

            if data["status"] and "data" in data:
                profiles = []
                for profile in data["data"]:
                    profiles.append({
                        "nik": profile.get("nik"),
                        "name": profile.get("name"),
                        "image_profile": profile.get("image_profile"),
                        "role_name": profile.get("role_name"),
                        "department_name": profile.get("department_name"),
                        "position_name": profile.get("position_name"),
                        "project_name": profile.get("project_name"),
                        "status_project": profile.get("status_project"),
                        "level_name": profile.get("level_name"),
                    })
                return profiles
            else:
                logger.error("Invalid response structure or status is false")
                return None

        else:
            logger.error(f"Unexpected status code: {response.status_code}, Message: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error occurred while fetching designated person: {e}")
        return None



import psycopg2
from psycopg2.extras import RealDictCursor  # For results as dictionaries if needed


def fetch_data(query, params=None):
    """
    Execute a read-only query and return the results.

    :param query: SQL query string
    :param params: Tuple or list of parameters to be passed to the query
    :return: Query results as a list of rows
    """
    try:
        with psycopg2.connect(**config.DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()  # Fetch all results
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        return []
    

def fetch_data_timeoff(query, params=None):
    """
    Execute a read-only query and return the results from timeoff database.

    :param query: SQL query string
    :param params: Tuple or list of parameters to be passed to the query
    :return: Query results as a list of rows
    """
    try:
        with psycopg2.connect(**config.DB_CONFIG_TIMEOFF) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()  # Fetch all results
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        return []
