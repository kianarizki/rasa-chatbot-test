
from typing import Text, Any, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction
import requests
import jwt
import snakemd
import logging
import datetime
from datetime import datetime, timedelta, date
from babel.dates import format_datetime



from actions.schema import MessageSchema,MessageDatePicker,MessageRangePicker, MessageSelectOptions

from actions.services.mtn001m.api import get_001m_token,get_001m_model_manufacturers,get_001m_report_daily_internal,get_001m_component_description,get_001m_model_dropdown,get_001m_internal_status_process


logger = logging.getLogger(__name__)
logger.info("Starting Action 001M Server")


class ActionGet001MReportDailyInternalDateFilter(Action):
    def name(self) -> str:
        return "action_get_001m_report_daily_internal_date_filter"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info(f"Running Action {self.name()}")
        language = tracker.get_slot("language")
        token_001m = get_001m_token(tracker)
        date_daily_report = tracker.get_slot("date_daily_report") if tracker.get_slot("date_daily_report") != " " else ""
        # manufacture_daily_report = tracker.get_slot("manufacture_daily_report") if tracker.get_slot("manufature_daily_report") != " " else ""
        # model_daily_report = tracker.get_slot("model_daily_report") if tracker.get_slot("model_daily_report") != " " else ""
        # comp_desc_daily_report = tracker.get_slot("comp_desc_daily_report") if tracker.get_slot("comp_desc_daily_report") != " " else ""
        # status_process_daily_report = tracker.get_slot("status_process_daily_report") if tracker.get_slot("status_process_daily_report") != " " else ""
        # search_daily_report = tracker.get_slot("search_daily_report") if tracker.get_slot("search_daily_report") != " " else ""

        data = get_001m_report_daily_internal(token_001m,daily_report_date=date_daily_report)
        if data :
            message = "Berikut Daily Internal Report:"
            # doc = snakemd.Document()
            # table_header = ["No", "Manufacture", "Model","MTN Routable", "Comp. Part Number", "Comp. Description", "Workorder No", "Process", "Start Job", "Estimated Finish Data", "Duration WIP", "Status", "Progress"]
            # table_data = []

            for i in range(len(data)):
                # table_data.append([str(i+1), 
                #                    data[i].get('mtn_information', {}).get('model', {}).get('manufacturer', {}).get('name', None),
                #                    data[i].get('mtn_information', {}).get('model', {}).get('name', None),
                #                    data[i].get('mtn_information', {}).get('serial_number', None),
                #                    data[i].get('component', {}).get('name', None),
                #                    data[i].get('component_description', None),
                #                    data[i].get('workorder_information', {}).get('001m_workorder_number', None),
                #                    data[i].get('production_line', {}).get('status_process', None),
                #                    data[i].get('repair_information', {}).get('date_register_job', None),
                #                    data[i].get('production_line', {}).get('estimated_finish_date', None),
                #                    data[i].get('actual_duration', None),
                #                    data[i].get('repair_information', {}).get('status_wip', None),
                #                    data[i].get('repair_information', {}).get('progress', None)
                #                    ])
                message += f"- No: {i+1}\n"
                message += f"- Manufacture: {data[i].get('mtn_information', {}).get('model', {}).get('manufacturer', {}).get('name', None)}\n"
                message += f"- Model: {data[i].get('mtn_information', {}).get('model', {}).get('name', None)}\n"
                message += f"- MTN Routable: {data[i].get('mtn_information', {}).get('serial_number', None)}\n"
                message += f"- Comp. Part Number: {data[i].get('component', {}).get('name', None)}\n"
                message += f"- Comp. Description: {data[i].get('component_description', None)}\n"
                message += f"- Workorder No.: {data[i].get('workorder_information', {}).get('001m_workorder_number', None)}\n"
                message += f"- Process: {data[i].get('production_line', {}).get('status_process', None)}\n"
                message += f"- Start Job: {data[i].get('repair_information', {}).get('date_register_job', None)}\n"
                message += f"- Estimated Finish Date: {data[i].get('production_line', {}).get('estimated_finish_date', None)}\n"
                message += f"- Duration WIP: {data[i].get('actual_duration', None)}\n"
                message += f"- Status: {data[i].get('repair_information', {}).get('status_wip', None)}\n"
                message += f"- Progress: {data[i].get('repair_information', {}).get('progress', None)}\n"
                message += "\n"

            dispatcher.utter_message(text=message)
            # doc.add_table(table_header,table_data)
            # dispatcher.utter_message(text=doc.__str__())
        
        else:
            if language == "indonesia" :
                dispatcher.utter_message(text="Maaf, Tidak ada data yang tersedia")
                
            else :
                dispatcher.utter_message(text="Sorry, there was no available data.")

        return 


class ActionGet001MReportDailyInternalDateManufactureFilter(Action):
    def name(self) -> str:
        return "action_get_001m_report_daily_internal_date_manufacture_filter"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info(f"Running Action {self.name()}")
        language = tracker.get_slot("language")
        token_001m = get_001m_token(tracker)
        date_daily_report = tracker.get_slot("date_daily_report") if tracker.get_slot("date_daily_report") != " " else ""
        manufacture_daily_report = tracker.get_slot("manufacture_daily_report") if tracker.get_slot("manufature_daily_report") != " " else ""
        # model_daily_report = tracker.get_slot("model_daily_report") if tracker.get_slot("model_daily_report") != " " else ""
        # comp_desc_daily_report = tracker.get_slot("comp_desc_daily_report") if tracker.get_slot("comp_desc_daily_report") != " " else ""
        # status_process_daily_report = tracker.get_slot("status_process_daily_report") if tracker.get_slot("status_process_daily_report") != " " else ""
        # search_daily_report = tracker.get_slot("search_daily_report") if tracker.get_slot("search_daily_report") != " " else ""

        data = get_001m_report_daily_internal(token_001m,daily_report_date=date_daily_report,manufacturer=manufacture_daily_report)
        if data :
            message = "Berikut Daily Internal Report:"
            # doc = snakemd.Document()
            # table_header = ["No", "Manufacture", "Model","MTN Routable", "Comp. Part Number", "Comp. Description", "Workorder No", "Process", "Start Job", "Estimated Finish Data", "Duration WIP", "Status", "Progress"]
            # table_data = []

            for i in range(len(data)):
                # table_data.append([str(i+1), 
                #                    data[i].get('mtn_information', {}).get('model', {}).get('manufacturer', {}).get('name', None),
                #                    data[i].get('mtn_information', {}).get('model', {}).get('name', None),
                #                    data[i].get('mtn_information', {}).get('serial_number', None),
                #                    data[i].get('component', {}).get('name', None),
                #                    data[i].get('component_description', None),
                #                    data[i].get('workorder_information', {}).get('001m_workorder_number', None),
                #                    data[i].get('production_line', {}).get('status_process', None),
                #                    data[i].get('repair_information', {}).get('date_register_job', None),
                #                    data[i].get('production_line', {}).get('estimated_finish_date', None),
                #                    data[i].get('actual_duration', None),
                #                    data[i].get('repair_information', {}).get('status_wip', None),
                #                    data[i].get('repair_information', {}).get('progress', None)
                #                    ])
                message += f"- No: {i+1}\n"
                message += f"- Manufacture: {data[i].get('mtn_information', {}).get('model', {}).get('manufacturer', {}).get('name', None)}\n"
                message += f"- Model: {data[i].get('mtn_information', {}).get('model', {}).get('name', None)}\n"
                message += f"- MTN Routable: {data[i].get('mtn_information', {}).get('serial_number', None)}\n"
                message += f"- Comp. Part Number: {data[i].get('component', {}).get('name', None)}\n"
                message += f"- Comp. Description: {data[i].get('component_description', None)}\n"
                message += f"- Workorder No.: {data[i].get('workorder_information', {}).get('001m_workorder_number', None)}\n"
                message += f"- Process: {data[i].get('production_line', {}).get('status_process', None)}\n"
                message += f"- Start Job: {data[i].get('repair_information', {}).get('date_register_job', None)}\n"
                message += f"- Estimated Finish Date: {data[i].get('production_line', {}).get('estimated_finish_date', None)}\n"
                message += f"- Duration WIP: {data[i].get('actual_duration', None)}\n"
                message += f"- Status: {data[i].get('repair_information', {}).get('status_wip', None)}\n"
                message += f"- Progress: {data[i].get('repair_information', {}).get('progress', None)}\n"
                message += "\n"

            dispatcher.utter_message(text=message)
            # doc.add_table(table_header,table_data)
            # dispatcher.utter_message(text=doc.__str__())
        
        else:
            if language == "indonesia" :
                dispatcher.utter_message(text="Maaf, Tidak ada data yang tersedia")
                
            else :
                dispatcher.utter_message(text="Sorry, there was no available data.")

        return [SlotSet("date_daily_report", None), SlotSet("manufacture_daily_report",None)]


class ActionAskDateDailyReport(Action):
    def name(self) -> Text:
        return "action_ask_date_daily_report"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        message = MessageSchema("options")

        if language == "indonesia":
            date_message = MessageDatePicker("Masukkan Tanggal")
            message.add_date_picker(date_message)
            dispatcher.utter_message(
                text="Masukkan Tanggal",
                json_message=message.to_dict()
            )

        else:
            date_message = MessageDatePicker("Insert Date")
            message.add_date_picker(date_message)
            dispatcher.utter_message(
                text="Insert Date",
                json_message= message.to_dict()
            )


        return []
    
class ActionAskManufactureDailyReport(Action):
    def name(self) -> Text:
        return "action_ask_manufacture_daily_report"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_001m = get_001m_token(tracker)
        manufacturers = get_001m_model_manufacturers(token_001m)
        message = MessageSchema("options")
        options = []
        for model in manufacturers:
            options.append({
                "label":model["name"],
                "value":model["id"],
            })


        if language == "indonesia":
            message.add_select(MessageSelectOptions("Manufaktur",options))
            dispatcher.utter_message(
                text="Masukkan Pilihan Manufaktur",
                json_message=message.to_dict()
            )

        else:
            message.add_select(MessageSelectOptions("Manufacture",options))
            dispatcher.utter_message(
                text="Choose the manufacturer options",
                json_message= message.to_dict()
            )


        return []
    

class ActionAskModelDailyReport(Action):
    def name(self) -> Text:
        return "action_ask_model_daily_report"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_001m = get_001m_token(tracker)
        manufacturers = get_001m_model_dropdown(token_001m)
        message = MessageSchema("options")
        options = []
        for model in manufacturers:
            options.append({
                "label":model["name"],
                "value":model["id"],
            })


        if language == "indonesia":
            message.add_select(MessageSelectOptions("Model",options))
            dispatcher.utter_message(
                text="Masukkan Pilihan Model",
                json_message=message.to_dict()
            )

        else:
            message.add_select(MessageSelectOptions("Model",options))
            dispatcher.utter_message(
                text="Choose the model options",
                json_message= message.to_dict()
            )


        return []
    
class ActionAskCompDescDailyReport(Action):
    def name(self) -> Text:
        return "action_ask_comp_desc_daily_report"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_001m = get_001m_token(tracker)
        manufacturers = get_001m_component_description(token_001m)
        message = MessageSchema("options")
        options = []
        for model in manufacturers:
            options.append({
                "label":model["name"],
                "value":model["id"],
            })


        if language == "indonesia":
            message.add_select(MessageSelectOptions("Comp Desc",options))
            dispatcher.utter_message(
                text="Masukkan Pilihan Deskripsi Komponen",
                json_message=message.to_dict()
            )

        else:
            message.add_select(MessageSelectOptions("Comp Desc",options))
            dispatcher.utter_message(
                text="Choose the Component options",
                json_message= message.to_dict()
            )


        return []
    


class ActionAskStatusProcessDailyReport(Action):
    def name(self) -> Text:
        return "action_ask_status_process_daily_report"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_001m = get_001m_token(tracker)
        manufacturers = get_001m_internal_status_process(token_001m)
        message = MessageSchema("options")
        options = []
        for model in manufacturers:
            options.append({
                "label":model["name"],
                "value":model["id"],
            })


        if language == "indonesia":
            message.add_select(MessageSelectOptions("Status Proses",options))
            dispatcher.utter_message(
                text="Masukkan Pilihan Status Proses",
                json_message=message.to_dict()
            )

        else:
            message.add_select(MessageSelectOptions("Status Process",options))
            dispatcher.utter_message(
                text="Choose the Process Status",
                json_message= message.to_dict()
            )


        return []
    
class ActionAskCompDescDailyReport(Action):
    def name(self) -> Text:
        return "action_ask_search_daily_report"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        

        if language == "indonesia":
            dispatcher.utter_message(
                text="Masukkan Search",
            )

        else:
            dispatcher.utter_message(
                text="Input the search query",
            )


        return []
    