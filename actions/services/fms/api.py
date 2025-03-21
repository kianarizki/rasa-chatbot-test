import requests

import logging
from datetime import datetime, timedelta, date
from actions import config
import jwt
logger = logging.getLogger(__name__)

def get_fms_token(tracker):
    events = tracker.events[::-1]
    for e in events:
        token_fms = e.get('metadata', {}).get('token_fms', None)
        if token_fms:
            return token_fms

    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsZXZlbCI6IjEiLCJwZXJtaXNzaW9ucyI6eyIxIjp0cnVlLCIxMCI6dHJ1ZSwiMTAwIjp0cnVlLCIxMDEiOnRydWUsIjEwMiI6dHJ1ZSwiMTAzIjp0cnVlLCIxMDQiOnRydWUsIjEwNSI6dHJ1ZSwiMTA2Ijp0cnVlLCIxMDciOnRydWUsIjEwOCI6dHJ1ZSwiMTA5Ijp0cnVlLCIxMSI6dHJ1ZSwiMTEwIjp0cnVlLCIxMTEiOnRydWUsIjExMiI6dHJ1ZSwiMTEzIjp0cnVlLCIxMTQiOnRydWUsIjExNSI6dHJ1ZSwiMTE2Ijp0cnVlLCIxMTciOnRydWUsIjExOCI6dHJ1ZSwiMTIiOnRydWUsIjEyMSI6dHJ1ZSwiMTIyIjp0cnVlLCIxMjMiOnRydWUsIjEyNCI6dHJ1ZSwiMTI1Ijp0cnVlLCIxMjYiOnRydWUsIjEyNyI6dHJ1ZSwiMTI4Ijp0cnVlLCIxMjkiOnRydWUsIjEzIjp0cnVlLCIxMzAiOnRydWUsIjEzMSI6dHJ1ZSwiMTMyIjp0cnVlLCIxMzMiOnRydWUsIjEzNCI6dHJ1ZSwiMTM1Ijp0cnVlLCIxMzYiOnRydWUsIjE0Ijp0cnVlLCIxNDAiOnRydWUsIjE0MSI6dHJ1ZSwiMTQyIjp0cnVlLCIxNDMiOnRydWUsIjE0NCI6dHJ1ZSwiMTQ1Ijp0cnVlLCIxNDYiOnRydWUsIjE0NyI6dHJ1ZSwiMTQ4Ijp0cnVlLCIxNDkiOnRydWUsIjE1Ijp0cnVlLCIxNTAiOnRydWUsIjE1MSI6dHJ1ZSwiMTUyIjp0cnVlLCIxNTMiOnRydWUsIjE1NCI6dHJ1ZSwiMTU1Ijp0cnVlLCIxNTYiOnRydWUsIjE1NyI6dHJ1ZSwiMTU4Ijp0cnVlLCIxNTkiOnRydWUsIjE2Ijp0cnVlLCIxNjAiOnRydWUsIjE2MSI6dHJ1ZSwiMTYyIjp0cnVlLCIxNjMiOnRydWUsIjE2NCI6dHJ1ZSwiMTY1Ijp0cnVlLCIxNjYiOnRydWUsIjE2NyI6dHJ1ZSwiMTY4Ijp0cnVlLCIxNjkiOnRydWUsIjE3Ijp0cnVlLCIxNzAiOnRydWUsIjE3MSI6dHJ1ZSwiMTcyIjp0cnVlLCIxNzMiOnRydWUsIjE3NCI6dHJ1ZSwiMTc1Ijp0cnVlLCIxNzYiOnRydWUsIjE3NyI6dHJ1ZSwiMTc4Ijp0cnVlLCIxNzkiOnRydWUsIjE4Ijp0cnVlLCIxODAiOnRydWUsIjE4MSI6dHJ1ZSwiMTgyIjp0cnVlLCIxOSI6dHJ1ZSwiMiI6dHJ1ZSwiMjAiOnRydWUsIjIxIjp0cnVlLCIyMiI6dHJ1ZSwiMjMiOnRydWUsIjI0Ijp0cnVlLCIyNSI6dHJ1ZSwiMjYiOnRydWUsIjI3Ijp0cnVlLCIyOCI6dHJ1ZSwiMjkiOnRydWUsIjMiOnRydWUsIjMwIjp0cnVlLCIzMSI6dHJ1ZSwiMzIiOnRydWUsIjMzIjp0cnVlLCIzNCI6dHJ1ZSwiMzUiOnRydWUsIjM2Ijp0cnVlLCIzNyI6dHJ1ZSwiMzgiOnRydWUsIjM5Ijp0cnVlLCI0Ijp0cnVlLCI0MCI6dHJ1ZSwiNDEiOnRydWUsIjQyIjp0cnVlLCI0MyI6dHJ1ZSwiNDQiOnRydWUsIjQ1Ijp0cnVlLCI0NiI6dHJ1ZSwiNDciOnRydWUsIjQ4Ijp0cnVlLCI0OSI6dHJ1ZSwiNSI6dHJ1ZSwiNTAiOnRydWUsIjUxIjp0cnVlLCI1MiI6dHJ1ZSwiNTMiOnRydWUsIjU0Ijp0cnVlLCI1NSI6dHJ1ZSwiNTYiOnRydWUsIjU3Ijp0cnVlLCI1OCI6dHJ1ZSwiNTkiOnRydWUsIjYiOnRydWUsIjYwIjp0cnVlLCI2MSI6dHJ1ZSwiNjIiOnRydWUsIjYzIjp0cnVlLCI2NCI6dHJ1ZSwiNjYiOnRydWUsIjY3Ijp0cnVlLCI2OCI6dHJ1ZSwiNjkiOnRydWUsIjciOnRydWUsIjcwIjp0cnVlLCI3MSI6dHJ1ZSwiNzIiOnRydWUsIjczIjp0cnVlLCI3NCI6dHJ1ZSwiNzUiOnRydWUsIjc2Ijp0cnVlLCI3NyI6dHJ1ZSwiNzgiOnRydWUsIjc5Ijp0cnVlLCI4Ijp0cnVlLCI4MCI6dHJ1ZSwiODEiOnRydWUsIjgyIjp0cnVlLCI4MyI6dHJ1ZSwiODQiOnRydWUsIjg1Ijp0cnVlLCI4NiI6dHJ1ZSwiODciOnRydWUsIjg4Ijp0cnVlLCI4OSI6dHJ1ZSwiOSI6dHJ1ZSwiOTAiOnRydWUsIjkxIjp0cnVlLCI5MiI6dHJ1ZSwiOTMiOnRydWUsIjk0Ijp0cnVlLCI5NSI6dHJ1ZSwiOTYiOnRydWUsIjk3Ijp0cnVlLCI5OCI6dHJ1ZSwiOTkiOnRydWV9LCJ1c2VyX25hbWUiOiJBZG1pbmlzdHJhdG9yIiwic2l0ZV9uYW1lIjoiSGVhZCBPZmZpY2UgSmFrYXJ0YSIsImV4cCI6MTc0MTMzMzQ5NywiaXNzIjoiMTIzNDUifQ.akS_FW-27m5_9n6y4soaUrevTo4WK14NIjAd7_6iGVo"

def get_all_equipments_fms(token_fms, query_condition,values):
    try:
        URL = f"{config.FMS_BASE_URL}equipments?"
        if query_condition == "search":
            URL += f"?search={values}"
        elif query_condition == "equipment_site":
            URL += f"?equipment_site={query_condition}"
        elif query_condition == "equipment":
            URL += f"?equipment={query_condition}"
        elif query_condition == "top10":
            URL += f"?site_id={values}&limit=100"
        elif query_condition == "top10breakdown":
            URL += f"?site_id={values}&limit=9999&condition_status=Breakdown"
        response = requests.get(URL, headers={"cookie":f"token={token_fms}"})
        logger.info(f"Response Get ALL Equipment FMS : {response.json()}")
        if response.status_code == 200:
            data = response.json()
            value = {
                "total_equipments": 0,
                "count_type": 0,
                "units": [],

            }

            value["total_equipments"] = data.get("total",0)
            value["count_type"] = data.get("total",0)
            data = data.get("data",None)
            if data==None:
                return None
            for i in data:
                temp = {
                    "equipment_type":"",
                    "equipment_category_name":"",
                    "manufacture_name":"",
                    "model":"",
                    "modification_description":"",
                    "serial_number":"",
                    "head_unit_sn":"",
                    "nearon_sn":"",
                    "location":"",
                    "condition_status":"",
                    "is_active":"",
                    "purchase_date":"",
                    "unit_name":"",
                    "site_name":"",
                    "modification_name":"",
                }
          

                temp['site_name'] = i.get("site",{}).get("site","")
                temp["equipment_type"] = i.get('model',{}).get("equipment_category",{}).get("equipment_type",{}).get("name","")
                temp['equipment_category_name'] = i.get('model',{}).get("equipment_category",{}).get("name","")
                temp['manufacture_name'] = i.get('model',{}).get("manufacture_name",{}).get("name","")
                temp['model'] = i.get("model",{}).get("name","")
                temp['modification_name'] = i.get("installed_modification",{}).get("modification")
                temp['modification_description'] = i.get("installed_modification",{}).get("description")
                temp['serial_number'] = i.get("serial_number","")
                temp['head_unit_sn'] = i.get("head_unit_sn","")
                temp['nearon_sn'] = i.get("nearon_sn","")
                temp['location'] = "Lat :" + i.get("site").get("latitude","") + " Long: " + i.get("site").get("longitude","")
                temp['condition_status'] = i.get("condition_status","")
                temp['is_active'] = i.get("is_active","")#"Active" if i.get("is_active","true") == "true" else "Inactive"
                temp['purchase_date'] = datetime.strptime(i.get("purchase_date","2024-12-17T04:44:31Z"), '%Y-%m-%dT%H:%M:%SZ')
                temp['unit_name'] = i.get("code","")
                temp['hm'] = i.get("hm",0)
                temp['km'] = i.get("km",0)
                temp['capacity'] = i.get("capacity",0)

                value['units'].append(temp)

            logger.info(f"VALUE {value}")
            return value
        else:
            return None
    except Exception as e:
        logger.error(f"Error occured while fetching: {e}")
        return None
    


def get_all_equipments_categoires_fms(token_fms, query_condition,value):
    try:
        URL = f"{config.FMS_BASE_URL}equipments/categories"
        if query_condition == "search":
            URL += f"?search={value}"
        elif query_condition == "is_active":
            URL += f"?is_active={'true' if value else 'false'}"
        response = requests.get(URL, headers={"cookie":f"token={token_fms}"})
        logger.info(f"Response Get ALL Equipment FMS {URL}: {response.json()}")
     
        if response.status_code == 200:
            data = response.json()
            value = {
                "total_equipments": 0,
                "equipment_category":[],
                "equipment_type":[]

            }

            value["total_equipments"] = data.get("total",0)
            value["count_type"] = data.get("total",0)
            data = data.get("data",None)
            if data==None:
                return None
            for i in data:
                temp = {
                    "category_name":"",
                    "is_active":False,
                    "equipment_type":""
                }
                temp["category_name"] = i.get("name","")
                temp['is_active'] = i.get("is_active",False)
                temp["equipment_type"] = len(i.get("equipment_type",[]))
                for j in i.get("equipment_type",[]):
                    value["equipment_type"].append(j.get("name",""))


                value['equipment_category'].append(temp)
            logger.info(f"VALUE {value}")
            return value
        else:
            return None
    except Exception as e:
        logger.error(f"Error occured while fetching: {e}")
        return None
    
def get_all_work_orders_fms(token_fms, query_condition,value):
    try:
        URL = f"{config.FMS_BASE_URL}projects/work-orders"
        # logger.info(f"Query Condition, Value {query_condition} {value}")

        if query_condition == "search":
            URL += f"?search={value}"
        elif query_condition == "is_active":
            URL += f"?is_active={'true' if value else 'false'}"
        elif query_condition == "site_id":
            URL += f"?site_id={value}"
        elif query_condition == "shift_name":
            URL += f"?shift_name={value}"
        elif query_condition == "site_date":
            URL += f"?site_id={value[0]}&date={value[1]}"
        elif query_condition == "site_last_night":
            URL += f"?site_id={value[0]}&date={value[1]}&shift_name={value[2]}"
        elif query_condition == "site_last_day":
            URL += f"?site_id={value[0]}&date={value[1]}&shift_name={value[2]}"
        elif query_condition == "date_shift":
            URL += f"?date={value[0]}&shift_name={value[1]}"
        elif query_condition == "date":
            logger.info(f"value {value}")
            add_URL = f"?date={value}"

            if value == "hari ini" or value == "today":
                value = datetime.now().strftime('%Y-%m-%d')
            elif value == "kemarin siang" or value == "last noon":
                value = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                add_URL = f"?date={value}&shift_name=Day"
            elif value == "last night" or value == "kemarin malam":
                value = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                add_URL = f"?date={value}&shift_name=Night"
                logger.info("Adding")
        
            URL += add_URL

        response = requests.get(URL, headers={"cookie":f"token={token_fms}"})
        logger.info(f"Response Get ALL WO FMS {URL} from query con {query_condition} Value {value}: {response.json()}")
     
        if response.status_code == 200:
            data = response.json()
            value = {
                "total":0,
                "data":[],
            }

            value["total"] = data.get("total",0)
            data = data.get("data",None)
            if data==None:
                return None
            for i in data:
                temp = {
                    "id": "",
                    "site_id": "",
                    "pit_id": "",
                    "shift_id": "",
                    "work_order_no": "",
                    "date": "",
                    "is_active": True,
                    "created_at": "",
                    "updated_at": "",
                    "site_name": "",
                    "pit_name": "",
                    "shift_name": ""
                }

                temp["id"] = i.get("id","")
                temp['site_id'] = i.get("site_id","")
                temp['pit_id'] = i.get("pit_id","")
                temp['shift_id'] = i.get("shift_id","")
                temp['work_order_no'] = i.get("work_order_no","")
                temp['date'] = i.get("date","2025-01-01T00:00:00Z")
                temp['is_active'] = i.get("is_active",True)
                temp['created_at'] = datetime.strptime(i.get("created_at","2024-11-22T03:55:32.690078Z"),'%Y-%m-%dT%H:%M:%S.%fZ')
                temp['updated_at'] = datetime.strptime(i.get("updated_at","2024-11-22T03:55:32.690078Z"),'%Y-%m-%dT%H:%M:%S.%fZ')
                temp['site_name'] = i.get("site_name","")
                temp['pit_name'] = i.get("pit_name","")
                temp['shift_name'] = i.get("shift_name","")
                value["data"].append(temp)
            logger.info(f"VALUE {value}")
            return value
        else:
            return None
    except Exception as e:
        logger.error(f"Error occured while fetching: {e}")
        return None
    


def get_all_work_area_by_site_fms(token_fms, query_condition, value, site):
    try:
        # Construct URL based on query condition
        URL = f"{config.FMS_BASE_URL}projects/sites/{site}/work-areas"
        
        if query_condition == "search":
            URL += f"?search={value}"
        elif query_condition == "is_active":
            URL += f"?is_active={'true' if value else 'false'}"
        elif query_condition == "site_id":
            URL += f"?site_id={value}"
        elif query_condition == "shift_name":
            URL += f"?shift_name={value}"
        elif query_condition == "disposal":
            URL += f"?is_disposal={value}"
        
        # Send GET request to fetch work areas
        response = requests.get(URL, headers={"cookie": f"token={token_fms}"})
        
        # Log the response for debugging purposes
        logger.info(f"Response Get ALL WA FMS {URL}: {response.json()}")
        
        # Check if the response status is 200 OK
        if response.status_code == 200:
            data = response.json()
            
            # Initialize result dictionary to store the processed data
            result = {
                "total": 0,
                "data": [],
            }

            # Set the total count of work areas
            result["total"] = data.get("total", 0)
            
            # Get the list of work areas from the response data
            work_areas = data.get("data", [])
            
            # If there is no data in the response, return None
            if not work_areas:
                return None
            
            # Loop through each work area and format it as needed
            for work_area in work_areas:
                # Process each work area into the required structure
                temp = {
                    "id": work_area.get("id", "N/A"),
                    "name": work_area.get("name", "N/A"),
                    "workorder_id": work_area.get("workorder_id", "N/A"),
                    "shift_id": work_area.get("shift_id", None),  # Could be None if not provided
                    "pit_id": work_area.get("pit_id", "N/A"),
                    "pit_name": work_area.get("pit_name", "N/A"),
                    "site_id": work_area.get("site_id", "N/A"),
                    "site_name": work_area.get("site_name", "N/A"),
                    "inventory": work_area.get("inventory", 0),
                    "is_active": work_area.get("is_active", False),
                    "created_at": work_area.get("created_at", "N/A"),
                    "updated_at": work_area.get("updated_at", "N/A"),
                    "measurement_name": work_area.get("measurement_name", "N/A"),
                    "is_ph": work_area.get("is_ph", False),
                    "date": work_area.get("date", "N/A"),
                    "is_disposal": work_area.get("is_disposal", False),
                    "created_from": work_area.get("created_from", "N/A"),
                }
                
                # Append the formatted work area to the result's data list
                result["data"].append(temp)
            
            # Return the final processed result
            return result
        else:
            # If response status is not 200, log the error and return None
            logger.error(f"Failed to fetch work areas: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        # Log any exception that occurs during the request or processing
        logger.error(f"Error occurred while fetching work areas: {e}")
        return None


def get_all_fleet_setting_fms(token_fms, query_condition, value):
    try:
        # Construct URL based on query condition
        URL = f"{config.FMS_BASE_URL}projects/fleets"

        if query_condition == "search":
            URL += f"?search={value}"
        elif query_condition == "is_active":
            URL += f"?is_active={'true' if value else 'false'}"
        elif query_condition == "site_id":
            URL += f"?site_id={value}"
        elif query_condition == "shift_name":
            URL += f"?shift_name={value}"
        elif query_condition == "search_site":
            URL += f"?search_site={value[0]}&site_id={value[1]}"
        elif query_condition == "limit_site":
            URL += f"?limit=100&site_id={value[1]}"

        # Send GET request to fetch work areas
        response = requests.get(URL, headers={"cookie": f"token={token_fms}"})

        # Log the response for debugging purposes
        logger.info(f"Response Get ALL Fleet FMS {URL}: {response.json()}")

        # Check if the response status is 200 OK
        if response.status_code == 200:
            data = response.json()

            # Initialize result dictionary to store the processed data
            result = {
                "total": data.get("total", 0),
                "page": data.get("page", 1),
                "count": data.get("count", 0),
                "data": []
            }

            # Get the list of fleet settings from the response data
            fleet_data = data.get("data", [])

            # If there is no data in the response, return None
            if not fleet_data:
                return None

            # Loop through each fleet setting and format it as needed
    # Loop through each fleet setting and format it as needed
            for fleet in fleet_data:
                formatted_fleet = {
                    "id": fleet.get("id", "N/A"),
                    "excavator_id": fleet.get("excavator_id", "N/A"),
                    "excavator_code": fleet.get("excavator_code", "N/A"),
                    "excavator_capacity": fleet.get("excavator_capacity", 0),
                    "excavator_factor_material": fleet.get("excavator_factor_material", 0),
                    "excavator_operator": fleet.get("excavator_operator","N/A"),
                    "site_id": fleet.get("site_id", "N/A"),
                    "site_name": fleet.get("site_name", "N/A"),
                    "work_area_id": fleet.get("work_area_id", "N/A"),
                    "work_area_name": fleet.get("work_area_name", "N/A"),
                    "activity_code": fleet.get("activity_code", 0),
                    "activity_name": fleet.get("activity_name", "N/A"),
                    "material_id": fleet.get("material_id", "N/A"),
                    "pit_id": fleet.get("pit_id", "N/A"),
                    "pit_name": fleet.get("pit_name", "N/A"),
                    "distance": fleet.get("distance", 0),
                    "is_actual": fleet.get("is_actual", False),
                    "need_setting": fleet.get("need_setting", False),
                    # "equipments" : fleet.get("equipments",[]),
                    "matching_fleet" : fleet.get("matching_fleet","N/A"),
                    "spot_time": fleet.get("spot_time", "N/A"),
                    "loader_cycle_time": fleet.get("loader_cycle_time", "N/A"),
                    "haul_time" : fleet.get("haul_time","N/A"),
                    "dump_time" : fleet.get("dump_time","N/A"),
                    "return_time" : fleet.get("return_time","N/A"),
                    "excavator_productivity_actual": fleet.get("excavator_productivity_actual",{
                        "value": 0,
                        "unit": 0,
                    }),
                    "excavator_production_cycle": fleet.get("excavator_production_cycle",{
                        "value":"N/A",
                        "unit": "N/A",
                    }),
                    "productivity_target": fleet.get("productivity_target", {
                        "value":"N/A",
                        "unit": "N/A",
                    }),
                    "created_at": fleet.get("created_at", "N/A"),
                    "updated_at": fleet.get("updated_at", "N/A"),
                }

                # Process nested data (e.g., excavator_model, haulers)
                excavator_model = fleet.get("excavator_model", {})
                if not excavator_model:
                    excavator_model = {
                        "id": "N/A",
                        "name": "N/A",
                        "manufacture": {"name": "N/A"},
                        "type": {"name": "N/A"},
                    }
                formatted_fleet["excavator_model"] = {
                    "id": excavator_model.get("id", "N/A"),
                    "name": excavator_model.get("name", "N/A"),
                    "manufacture": excavator_model.get("manufacture", {}).get("name", "N/A"),
                    "type": excavator_model.get("type", {}).get("name", "N/A"),
                }

                haulers = fleet.get("haulers", [])
                if not haulers:
                    haulers = [
                                    {
                        "equipment_type_id": "",
                        "equipment_type_name":"",
                        "class_name": "",
                        "amount": 0,
                        "capacity": 0,
                        "factor_material": "",
                        "material_name": "",
                    } for _ in range(1) 
                    ]
                formatted_fleet["haulers"] = [
                    {
                        "equipment_type_id": hauler.get("equipment_type_id", "N/A"),
                        "equipment_type_name": hauler.get("equipment_type_name", "N/A"),
                        "class_name": hauler.get("class_name", "N/A"),
                        "amount": hauler.get("amount", 0),
                        "capacity": hauler.get("capacity", 0),
                        "factor_material": hauler.get("factor_material", "N/A"),
                        "material_name": hauler.get("material_name", "N/A"),
                    } for hauler in haulers
                ]
                equipments = fleet.get("equipments",[])
                # if not equipments:
                #     equipments = [
                #                 {
                #         "name": "",
                #         "type": "",
                #     } for _ in range(1) 
                #     ]
                formatted_fleet["equipments"] = [
                    {
                        "name": equipment.get("name", "N/A"),
                        "type": equipment.get("tipe", "N/A"),
                    } for equipment in equipments
                ]

                telemetry = fleet.get("excavator_telemetry")

                if not telemetry:
                    telemetry = {
                        "latitude": 0,
                        "longitude": 0, 
                        "bearing": 0,
                        "distance_meters": 0,
                        "fuel_level": 0,
                        "speed_kmh": 0,
                        "payload" :0,
                        "hour_meter" :0,
                        "total_distance_metered": 0,
                    }

                formatted_fleet["excavator_telemetry"] = {
                    "latitude": telemetry.get("latitude", 0),
                    "longitude": telemetry.get("longitude", 0),
                    "bearing": telemetry.get("bearing", 0),
                    "distance_meters": telemetry.get("distance_meters", 0),
                    "fuel_level": telemetry.get("fuel_level", 0),
                    "speed_kmh": telemetry.get("speed_kmh", 0),
                    "payload": telemetry.get("payload", 0),
                    "hour_meter": telemetry.get("hour_meter", 0),
                    "total_distance_metered": telemetry.get("total_distance_metered", 0),
                }
                # Append the formatted fleet to the result's data list
                result["data"].append(formatted_fleet)
             
            return result
        else:
            # If response status is not 200, log the error and return None
            logger.error(f"Failed to fetch fleet settings: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        # Log any exception that occurs during the request or processing
        logger.error(f"Error occurred while fetching fleet settings: {e}")
        return None


def get_fms_production_performance_control(token_fms,query_type:str , values:list):
    try:
        site_name = values[0]
        timezone = 7
        shift_name = values[1]
        date_slot = values[2]
        url = f"{config.FMS_BASE_URL}projects/production-performance/{site_name}/shift-time/{shift_name}?timezone={timezone}&date={date_slot}"
        print(url)
        response = requests.get(url, headers={"cookie": f"token={token_fms}"})
        logger.info(f"Response: {response.json()}")

        if response.status_code == 200:
            data = response.json()

            if data["status"] and "data" in data:
                production_data = {
                    "waste_production": {
                        "shiftly": data["data"].get("waste_production", {}).get("shiftly", {}),
                        "daily": data["data"].get("waste_production", {}).get("daily", {}),
                        "month_to_date": data["data"].get("waste_production", {}).get("month_to_date", {}),
                        "year_to_date": data["data"].get("waste_production", {}).get("year_to_date", {})
                    },
                    "coal_production": {
                        "shiftly": data["data"].get("coal_production", {}).get("shiftly", {}),
                        "daily": data["data"].get("coal_production", {}).get("daily", {}),
                        "month_to_date": data["data"].get("coal_production", {}).get("month_to_date", {}),
                        "year_to_date": data["data"].get("coal_production", {}).get("year_to_date", {})
                    },
                    "digger_productivity": {
                        "waste": data["data"].get("digger_productivity", {}).get("waste"),
                        "coal": data["data"].get("digger_productivity", {}).get("coal")
                    }
                }
                return production_data
            else:
                logger.error("Invalid response structure or status is false")
                return None

        else:
            logger.error(f"Unexpected status code: {response.status_code}, Message: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error occurred while fetching production data: {e}")
        return None


def get_equipment_breakdown_fms(token_fms, site_id, value):
    """
    Fetch data from the given API URL and handle null values gracefully.
    
    Args:
        token_fms (str): The Token of the API endpoint.
        query_type (str): The type of query to be returned
        value (array of str): The value to filter the equipment breakdown by.
    
    Returns:
        dict: The parsed JSON response or an error message if the request fails.
    """
    try:
        url = f"{config.FMS_BASE_URL}equipments/breakdowns?site_id={value[0]}&limit=9999"
        response = requests.get(url, headers={"cookie": f"token={token_fms}"})
        response.raise_for_status()
        data = response.json()
        
        # Check if the response contains valid data
        if data.get("status") and data.get("data"):
            # Clean null or missing values in the response
            cleaned_data = []
            for item in data["data"]:
                cleaned_item = {key: (value if value not in [None, "", "0001-01-01T00:00:00Z"] else None)
                                for key, value in item.items()}
                
                # Special handling for nested dictionaries
                if "equipment_type" in cleaned_item:
                    cleaned_item["equipment_type"] = {key: (value if value else None)
                                                      for key, value in cleaned_item["equipment_type"].items()}
                
                if "sites" in cleaned_item:
                    cleaned_item["sites"] = {key: (value if value else None)
                                             for key, value in cleaned_item["sites"].items()}
                
                if "model_condition" in cleaned_item:
                    cleaned_item["model_condition"] = {key: (value if value not in [None, ""] else None) for key, value in cleaned_item["model_condition"].items()}
                
                # Ensure faults is handled correctly
                if "faults" in cleaned_item:
                    cleaned_item["faults"] = [
                        {key: (value if value else None) for key, value in fault.items()}
                        for fault in cleaned_item["faults"]
                    ]
                
                cleaned_data.append(cleaned_item)
            
            return {
                    "code": data.get("code"), "status": data.get("status"),
                    "message": data.get("message"), "page": data.get("page"),
                    "count": data.get("count"), "total": data.get("total"), 
                    "data": cleaned_data
                    }
        
        return None
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error on executing request {url} : {e}")
        return None
    except ValueError as e:
        logger.error(f"Error on executing request {url} : {e}")
        return None
    
def get_operator_kpi_fms(token_fms, query_params, values, nik):
    """
    Fetch data from /projects/user-kpi/:NIK

    Params:
    token_fms (str): Authentication token for API access
    query_params (str): The query parameter to filter results (e.g., "date")
    values (list): The values for the query parameter
    nik (str): Operator NIK identifier

    Returns:
    dict: API result if available else None
    """
    try:
        url = f"{config.FMS_BASE_URL}projects/user-kpi/{nik}"
        headers = {"cookie": f"token={token_fms}"}
        
        # Attach query parameters if provided
        if query_params == "date" and values:
            url += f"?date={values[0]}"
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 200 and data.get("status") is True:
            if data.get("data",{}).get("details",None) == None:
                data['data']['details'] = [
                    {
                    "equipment": {
                    "id": "N/A",
                    "name": "N/A",
                    "code": "N/A",
                    "model": {
                    "id": "N/A",
                    "name": "N/A"
                    }
                    },
                    "dump_point_id": "N/A",
                    "dump_point_name": "N/A",
                    "material": "N/A",
                    "hourly_productivity_actual": 0,
                    "hourly_productivity_total": 0,
                    "production_actual": 0,
                    "production_total": 0,
                    "production_unit": "N/A",
                    "average_cycle_time_minutes": 0,
                    "cycles": 0,
                    "total_distances_meters": 0,
                    "hm_start": 0,
                    "hm_stop": 0,
                    "workhour_minutes_total": 0,
                    "login_status": "",
                    "login_at": "N/A",
                    "logout_status": "",
                    "logout_at": ""
                    }
                ]
            return data.get("data", {})
        else:
            logger.error(f"Unexpected response structure: {data}")
            return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error on executing request {url} : {e}")
        return None
    except ValueError as e:
        logger.error(f"Error parsing JSON response from {url} : {e}")
        return None
    
def get_nik_from_token_fms(token_fms):
    """
    Extracts the token from the provided FMS authentication token.
    
    Args:
        token_fms (str): The FMS authentication token.
    
    Returns:
        str: The token without the "token=" prefix.
    """
    nik = jwt.decode(token_fms, options={"verify_signature": False}).get("iss", "12345")
    return nik
