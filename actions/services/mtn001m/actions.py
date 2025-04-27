
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
from actions.services.mtn001m.api import get_001m_token,get_001m_report_daily_internal,get_001m_report_daily_external,get_001m_component_description,get_001m_model_dropdown,get_001m_internal_status_process,get_001m_forecast_allocation_report, reformat_date, get_001m_site_allocation,get_001m_model_manufacturers

logger = logging.getLogger(__name__)
logger.info("Starting Action 001M Server")


class ActionGet001MReportDailyInternalDateFilter(Action):
    def name(self) -> str:
        return "action_get_001m_report_daily_internal_date_filter"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info(f"Running Action {self.name()}")
        language = tracker.get_slot("language")
        token_001m = get_001m_token(tracker)
        date_daily_report = tracker.get_slot("date_001m_daily_report") if tracker.get_slot("date_001m_daily_report") != " " else ""


        data = get_001m_report_daily_internal(token_001m,daily_report_date=date_daily_report)
        if data :
            message = "Berikut Daily Internal Report:" if language == "indonesia" else "Here are Daily Internal Reports: "

            for i in range(len(data)):

                message += f"- No: {i+1}\n"
                message += f"- Manufacture: {data[i].get('mtn_information', {}).get('model', {}).get('manufacturer', {}).get('name', None)}\n"
                message += f"- Model: {data[i].get('mtn_information', {}).get('model', {}).get('name', None)}\n"
                message += f"- MTN Routable: {data[i].get('mtn_information', {}).get('serial_number', None)}\n"
                message += f"- Comp. Part Number: {data[i].get('component', {}).get('name', None)}\n"
                message += f"- Comp. Description: {data[i].get('component_description', None)}\n"
                message += f"- Workorder No.: {data[i].get('workorder_information', {}).get('001m_workorder_number', None)}\n"
                message += f"- Process: {data[i].get('production_line', {}).get('status_process', None)}\n"
                message += f"- Start Job: {reformat_date(data[i].get('repair_information', {}).get('date_register_job', None),lang=language)}\n"
                message += f"- Estimated Finish Date: {reformat_date(data[i].get('production_line', {}).get('estimated_finish_date', None),lang=language)}\n"
                message += f"- Duration WIP: {data[i].get('actual_duration', None)}\n"
                message += f"- Status: {data[i].get('repair_information', {}).get('status_wip', None)}\n"
                message += f"- Progress: {data[i].get('repair_information', {}).get('progress', None)}\n"
                message += "\n"

            dispatcher.utter_message(text=message)
        
        else:
            if language == "indonesia" :
                dispatcher.utter_message(text="Maaf, Tidak ada data yang tersedia")
            else :
                dispatcher.utter_message(text="Sorry, there was no available data.")

        return []

class ActionGet001MReportDailyExternalDateFilter(Action):
    def name(self) -> str:
        return "action_get_001m_report_daily_external_date_filter"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info(f"Running Action {self.name()}")
        language = tracker.get_slot("language")
        token_001m = get_001m_token(tracker)
        date_daily_report = tracker.get_slot("date_001m_daily_report") if tracker.get_slot("date_001m_daily_report") != " " else ""


        data = get_001m_report_daily_external(token_001m,daily_report_date=date_daily_report)
        if data :
            message = "Berikut Daily External Report:" if language == "indonesia" else "Here are Daily External Reports"

            for i in range(len(data)):

                message += f"- No: {i+1}\n"
                message += f"- Manufacture: {data[i].get('mtn_information', {}).get('model', {}).get('manufacturer', {}).get('name', None)}\n"
                message += f"- Model: {data[i].get('mtn_information', {}).get('model', {}).get('name', None)}\n"
                message += f"- MTN Routable: {data[i].get('mtn_information', {}).get('serial_number', None)}\n"
                message += f"- Comp. Part Number: {data[i].get('component', {}).get('name', None)}\n"
                message += f"- Comp. Description: {data[i].get('component_description', None)}\n"
                message += f"- Workorder No.: {data[i].get('workorder_information', {}).get('001m_workorder_number', None)}\n"
                message += f"- Process: {data[i].get('production_line', {}).get('status_process', None)}\n"
                message += f"- Start Job: {reformat_date(data[i].get('repair_information', {}).get('date_register_job', None))}\n"
                message += f"- Estimated Finish Date: {reformat_date(data[i].get('production_line', {}).get('estimated_finish_date', None))}\n"
                message += f"- Duration WIP: {data[i].get('actual_duration', None)}\n"
                message += f"- Status: {data[i].get('repair_information', {}).get('status_wip', None)}\n"
                message += f"- Progress: {data[i].get('repair_information', {}).get('progress', None)}\n"
                message += "\n"

            dispatcher.utter_message(text=message)
        
        else:
            if language == "indonesia" :
                dispatcher.utter_message(text="Maaf, Tidak ada data yang tersedia")
            else :
                dispatcher.utter_message(text="Sorry, there was no available data.")

        return []

class ActionAskDate001MDailyReport(Action):
    def name(self) -> Text:
        return "action_ask_date_001m_daily_report"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        message = MessageSchema("options")

        if language == "indonesia":
            date_message = MessageDatePicker("Masukkan Tanggal")
            message.add_date_picker(date_message)
            dispatcher.utter_message(
                text="Silahkan masukkan tanggal",
                json_message=message.to_dict()
            )

        else:
            date_message = MessageDatePicker("Insert Date")
            message.add_date_picker(date_message)
            dispatcher.utter_message(
                text="Please enter the date",
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
                text="Masukkan pilihan manufaktur",
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
                text="Masukkan pilihan model",
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
                text="Choose the Component Description Options",
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
    
class ActionAskSearchDailyReport(Action):
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
                text="Input the Search Query",
            )
        return []

class ActionAskAdditionalDailyReport(Action):
    def name(self) -> Text:
        return "action_ask_additional_daily_report"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        

        if language == "indonesia":
            dispatcher.utter_message(
                text="Silahkan Masukkan Nilai Filter Pertama:",
                buttons= [
                    {
                        "title":"Manufacturer",
                        "payload":"manufacturer"
                    },
                    {
                        "title":"Model",
                        "payload":"model"
                    },
                    {
                        "title":"Deskripsi Komponen",
                        "payload":"component-description"
                    },
                    {
                        "title":"Status Process",
                        "payload":"status-process"
                    },
                    {
                        "title":"Search",
                        "payload":"search"
                    },

                ]
            )

        else:
            dispatcher.utter_message(
                text="Please Enter First Filter Value:",
                buttons= [
                    {
                        "title":"Manufacturer",
                        "payload":"manufacturer"
                    },
                    {
                        "title":"Model",
                        "payload":"model"
                    },
                    {
                        "title":"Component Description",
                        "payload":"component-description"
                    },
                    {
                        "title":"Status Process",
                        "payload":"status-process"
                    },
                    {
                        "title":"Search",
                        "payload":"search"
                    },

                ]
            )
        return []

class ActionAskAdditionalDailyReportValue(Action):
    def name(self) -> Text:
        return "action_ask_additional_daily_report_value"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        message = self.get_message_from_key(tracker.get_slot("additional_daily_report"),token_001m=get_001m_token(tracker),tracker=tracker)    
        if message :
            if language == "indonesia":
                dispatcher.utter_message(
                    text="Silahkan Masukkan Nilai Filter Kedua:",
                    json_message=message.to_dict()
                )

            else:
                dispatcher.utter_message(
                    text="Please Enter the Second Filter Value:",
                    json_message=message.to_dict()
                )
        
        else:
            dispatcher.utter_message(
                text="Masukkan Search / Input your Search"
            )

        return []
    
    def get_message_from_key(self,slot_value:str,token_001m:str,tracker: Tracker):
        message = MessageSchema("options")
        
        if slot_value == "manufacturer":
            manufacturers = get_001m_model_manufacturers(token_001m)
            options = []
            for model in manufacturers:
                options.append({
                    "label":model["name"],
                    "value":model["id"],
                })
            message.add_select(MessageSelectOptions("Manufacturer",options))            
        
        elif slot_value == "model":
            manufacturers = get_001m_model_dropdown(token_001m)
            options = []
            for model in manufacturers:
                options.append({
                    "label":model["name"],
                    "value":model["id"],
                })
            message.add_select(MessageSelectOptions("Model",options))


        elif slot_value == "component-description":
            manufacturers = get_001m_component_description(token_001m)
            options = []
            for model in manufacturers:
                options.append({
                    "label":model["name"],
                    "value":model["id"],
                })
            message.add_select(MessageSelectOptions("Component Description",options))

        elif slot_value == "status-process":
            manufacturers = get_001m_internal_status_process(token_001m,tracker=tracker)
            options = []
            for model in manufacturers:
                options.append({
                    "label":model["name"],
                    "value":model["id"],
                })
            message.add_select(MessageSelectOptions("Status Process",options))

        else:
            return None

        return message

class ActionGet001MReportDailyInternalAdditionalFilter(Action):
    def name(self) -> str:
        return "action_get_001m_report_daily_internal_additional_filter"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info(f"Running Action {self.name()}")
        language = tracker.get_slot("language")
        token_001m = get_001m_token(tracker)
        date_daily_report = tracker.get_slot("date_001m_daily_report") if tracker.get_slot("date_001m_daily_report") != " " else ""
        additional_filter = tracker.get_slot("additional_daily_report")
        additional_filter_value = tracker.get_slot("additional_daily_report_value")

        data = None

        if additional_filter == "manufacturer":
            data = get_001m_report_daily_internal(token_001m,daily_report_date=date_daily_report,manufacturer=additional_filter_value)
        elif additional_filter == "model":
            data = get_001m_report_daily_internal(token_001m,daily_report_date=date_daily_report,model=additional_filter_value)
        elif additional_filter == "component-description":
            data = get_001m_report_daily_internal(token_001m,daily_report_date=date_daily_report,component_description=additional_filter_value)
        elif additional_filter == "status-process":
            data = get_001m_report_daily_internal(token_001m,daily_report_date=date_daily_report,status_process=additional_filter_value)
        else:
            data = get_001m_report_daily_internal(token_001m,daily_report_date=date_daily_report,search=additional_filter_value)

        if data :
            message = "Berikut Daily Internal Report:" if language == "indonesia" else "Here are Daily Internal Reports: "

            for i in range(len(data)):
                message += f"- No: {i+1}\n"
                message += f"- Manufacture: {data[i].get('mtn_information', {}).get('model', {}).get('manufacturer', {}).get('name', None)}\n"
                message += f"- Model: {data[i].get('mtn_information', {}).get('model', {}).get('name', None)}\n"
                message += f"- MTN Routable: {data[i].get('mtn_information', {}).get('serial_number', None)}\n"
                message += f"- Comp. Part Number: {data[i].get('component', {}).get('name', None)}\n"
                message += f"- Comp. Description: {data[i].get('component_description', None)}\n"
                message += f"- Workorder No.: {data[i].get('workorder_information', {}).get('001m_workorder_number', None)}\n"
                message += f"- Process: {data[i].get('production_line', {}).get('status_process', None)}\n"
                message += f"- Start Job: {reformat_date(data[i].get('repair_information', {}).get('date_register_job', None),lang=language)}\n"
                message += f"- Estimated Finish Date: {reformat_date(data[i].get('production_line', {}).get('estimated_finish_date', None),lang=language)}\n"
                message += f"- Duration WIP: {data[i].get('actual_duration', None)}\n"
                message += f"- Status: {data[i].get('repair_information', {}).get('status_wip', None)}\n"
                message += f"- Progress: {data[i].get('repair_information', {}).get('progress', None)}\n"
                message += "\n"
            dispatcher.utter_message(text=message)

        else:
            if language == "indonesia" :
                dispatcher.utter_message(text="Maaf, Tidak ada data yang tersedia")
                
            else :
                dispatcher.utter_message(text="Sorry, there was no available data.")
        return [SlotSet("additional_daily_report_value", None), SlotSet("additional_daily_report",None)]
    
class ActionGet001MReportDailyExternalAdditionalFilter(Action):
    def name(self) -> str:
        return "action_get_001m_report_daily_external_additional_filter"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info(f"Running Action {self.name()}")
        language = tracker.get_slot("language")
        token_001m = get_001m_token(tracker)
        date_daily_report = tracker.get_slot("date_001m_daily_report") if tracker.get_slot("date_001m_daily_report") != " " else ""
        additional_filter = tracker.get_slot("additional_daily_report")
        additional_filter_value = tracker.get_slot("additional_daily_report_value")

        data = None

        if additional_filter == "manufacturer":
            data = get_001m_report_daily_internal(token_001m,daily_report_date=date_daily_report,manufacturer=additional_filter_value)        
        elif additional_filter == "model":
            data = get_001m_report_daily_internal(token_001m,daily_report_date=date_daily_report,model=additional_filter_value)
        elif additional_filter == "component-description":
            data = get_001m_report_daily_internal(token_001m,daily_report_date=date_daily_report,component_description=additional_filter_value)
        elif additional_filter == "status-process":
            data = get_001m_report_daily_internal(token_001m,daily_report_date=date_daily_report,status_process=additional_filter_value)
        else:
            data = get_001m_report_daily_internal(token_001m,daily_report_date=date_daily_report,search=additional_filter_value)

        if data :
            message = "Berikut Daily External Report:" if language == "indonesia" else "Here are Daily External Report :"

            for i in range(len(data)):
                message += f"- No: {i+1}\n"
                message += f"- Manufacture: {data[i].get('mtn_information', {}).get('model', {}).get('manufacturer', {}).get('name', None)}\n"
                message += f"- Model: {data[i].get('mtn_information', {}).get('model', {}).get('name', None)}\n"
                message += f"- MTN Routable: {data[i].get('mtn_information', {}).get('serial_number', None)}\n"
                message += f"- Comp. Part Number: {data[i].get('component', {}).get('name', None)}\n"
                message += f"- Comp. Description: {data[i].get('component_description', None)}\n"
                message += f"- Workorder No.: {data[i].get('workorder_information', {}).get('001m_workorder_number', None)}\n"
                message += f"- Process: {data[i].get('production_line', {}).get('status_process', None)}\n"
                message += f"- Start Job: {reformat_date(data[i].get('repair_information', {}).get('date_register_job', None),lang=language)}\n"
                message += f"- Estimated Finish Date: {reformat_date(data[i].get('production_line', {}).get('estimated_finish_date', None),lang=language)}\n"
                message += f"- Duration WIP: {data[i].get('actual_duration', None)}\n"
                message += f"- Status: {data[i].get('repair_information', {}).get('status_wip', None)}\n"
                message += f"- Progress: {data[i].get('repair_information', {}).get('progress', None)}\n"
                message += "\n"

            dispatcher.utter_message(text=message)

        else:
            if language == "indonesia" :
                dispatcher.utter_message(text="Maaf, Tidak ada data yang tersedia")
                
            else :
                dispatcher.utter_message(text="Sorry, there was no available data.")
        return [SlotSet("additional_daily_report_value", None), SlotSet("additional_daily_report",None)]


class ActionCancelFollowup001MDailyReport(Action):
    def name(self) -> str:
        return "action_cancel_followup_001m_daily_report"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        if language == "indonesia":
            dispatcher.utter_message("Terima kasih")
        else:    
            dispatcher.utter_message("Thankyou")
            
        return [SlotSet("date_001m_daily_report",None), SlotSet("additional_daily_report_value", None), SlotSet("additional_daily_report",None)]


class ActionGet001MForecastAllocationReportDateFilter(Action):

    def name(self) -> str:
        return "action_get_001m_forecast_allocation_report_date_filter"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info(f"Running Action {self.name()}")
        language = tracker.get_slot("language")
        token_001m = get_001m_token(tracker)
        date_forecast_allocation_report = tracker.get_slot("date_001m_forecast_allocation_report")
        start_date, end_date = date_forecast_allocation_report.split(" - ") if date_forecast_allocation_report else "",""
        data = get_001m_forecast_allocation_report(token_001m, start_date=start_date, end_date=end_date)

        if data:
            message = "Berikut Forecast & Allocation Report:" if language=="indonesia" else "Here are Forecast and Allocation Reports: \n"

            for i in range(len(data)):
                message += f"\n- No: {i+1}"
                message += f"\n- Manufacture: {data[i].get('mtn_information',{}).get('model',{}).get('manufacturer',{}).get('name','-')}"
                message += f"\n- Model: {data[i].get('mtn_information',{}).get('model',{}).get('name','-')}"
                message += f"\n- MTN Routable: {data[i].get('mtn_information',{}).get('serial_number','-')}"
                message += f"\n- Comp. Part Number: {data[i].get('component',{}).get('name','-')}"
                message += f"\n- Comp. Description: {data[i].get('component_description','-')}"
                message += f"\n- Workorder No.: {data[i].get('workorder_information',{}).get('001m_workorder_number','-')}"
                message += f"\n- Unit Allocation: {data[i].get('allocation',{}).get('unit_id','-')}"
                message += f"\n- Site Allocation: {data[i].get('allocation',{}).get('site','-')}"
                message += f"\n- Estimated Finish Date: {reformat_date(data[i].get('production_line',{}).get('estimated_finish_date','-'),lang=language)}\n"
            
            dispatcher.utter_message(text=message)
        else:
            message = "Tidak ada data Forecast & Allocation Report yang ditemukan" if language=="indonesia" else "No Forecast and Allocation Report data found"
            dispatcher.utter_message(text=message)

        return []
    

class ActionAskDate001MForecastAllocationReport(Action):
    def name(self) -> Text:
        # date_001m_forecast_allocation_report
        return "action_ask_date_001m_forecast_allocation_report"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        message = MessageSchema("options")
        if language=="indonesia":
            message.add_range_picker(MessageRangePicker("Masukkan Tanggal"))
            dispatcher.utter_message(text="Masukkan Tanggal", json_message=message.to_dict())

        else:
            message.add_range_picker(MessageRangePicker("Insert Date"))
            dispatcher.utter_message(text="Insert Date", json_message=message.to_dict())
        
        return []


class ActionAskAdditional001MForecastReport(Action):
    def name(self) -> Text:
        return "action_ask_additional_001m_forecast_report"
# additional_001m_forecast_report
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        

        if language == "indonesia":
            dispatcher.utter_message(
                text="Silahkan Masukkan Nilai Filter Pertama:",
                buttons= [
                    {
                        "title":"Manufacturer",
                        "payload":"manufacturer"
                    },
                    {
                        "title":"Model",
                        "payload":"model"
                    },
                    {
                        "title":"Deskripsi Komponen",
                        "payload":"component-description"
                    },
                    {
                        "title":"Alokasi Site",
                        "payload":"site-allocation"
                    },
                    {
                        "title":"Search",
                        "payload":"search"
                    },

                ]
            )

        else:
            dispatcher.utter_message(
                text="Please Enter First Filter Value:",
                buttons= [
                    {
                        "title":"Manufacturer",
                        "payload":"manufacturer"
                    },
                    {
                        "title":"Model",
                        "payload":"model"
                    },
                    {
                        "title":"Component Description",
                        "payload":"component-description"
                    },
                    {
                        "title":"Site Allocation",
                        "payload":"site-allocation"
                    },
                    {
                        "title":"Search",
                        "payload":"search"
                    },

                ]
            )
        return []
    
class ActionAskAdditional001MForecastReportValue(Action):

    def name(self) -> Text:
        return "action_ask_additional_001m_forecast_report_value"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        message = self.get_message_from_key(tracker.get_slot("additional_001m_forecast_report"),token_001m=get_001m_token(tracker),tracker=tracker)    
        if message :
            if language == "indonesia":
                dispatcher.utter_message(
                    text="Silahkan Masukkan Nilai Filter Kedua:",
                    json_message=message.to_dict()
                )

            else:
                dispatcher.utter_message(
                    text="Please Enter the Second Filter Value:",
                    json_message=message.to_dict()
                )
        
        else:
            dispatcher.utter_message(
                text="Masukkan Search / Input your Search"
            )

        return []

    def get_message_from_key(self,slot_value:str,token_001m:str,tracker: Tracker):
        message = MessageSchema("options")
        
        if slot_value == "manufacturer":
            manufacturers = get_001m_model_manufacturers(token_001m)
            options = []
            for model in manufacturers:
                options.append({
                    "label":model["name"],
                    "value":model["id"],
                })
            message.add_select(MessageSelectOptions("Manufacturer",options))            
        
        elif slot_value == "model":
            manufacturers = get_001m_model_dropdown(token_001m)
            options = []
            for model in manufacturers:
                options.append({
                    "label":model["name"],
                    "value":model["id"],
                })
            message.add_select(MessageSelectOptions("Model",options))


        elif slot_value == "component-description":
            manufacturers = get_001m_component_description(token_001m)
            options = []
            for model in manufacturers:
                options.append({
                    "label":model["name"],
                    "value":model["id"],
                })
            message.add_select(MessageSelectOptions("Component Description",options))

        elif slot_value == "site-allocation":
            manufacturers = get_001m_site_allocation(token_001m,tracker=tracker)
            options = []
            for model in manufacturers:
                options.append({
                    "label":model["name"],
                    "value":model["id"],
                })
            message.add_select(MessageSelectOptions("Status Process",options))

        else:
            return None

        return message
    
class ActionGet001MForecastAllocationReportAdditionalFilter(Action):
    def name(self) -> Text:
        return "action_get_001m_forecast_allocation_report_additional_filter"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info(f"Running Action {self.name()}")
        language = tracker.get_slot("language")
        token_001m = get_001m_token(tracker)
        
        date_forecast_allocation_report = tracker.get_slot("date_001m_forecast_allocation_report") if tracker.get_slot("date_001m_forecast_allocation_report") != " " else ""
        

        start_date, end_date = date_forecast_allocation_report.split(" - ") if date_forecast_allocation_report else "",""
        # data = get_001m_forecast_allocation_report(token_001m, start_date=start_date, end_date=end_date)

        additional_filter = tracker.get_slot("additional_001m_forecast_report")
        additional_filter_value = tracker.get_slot("additional_001m_forecast_report_value")

        data = None

        if additional_filter == "manufacturer":
            data = get_001m_forecast_allocation_report(token_001m,start_date=start_date,end_date=end_date,manufacturer=additional_filter_value)        
        elif additional_filter == "model":
            data = get_001m_forecast_allocation_report(token_001m,start_date=start_date,end_date=end_date,model=additional_filter_value)
        elif additional_filter == "component-description":
            data = get_001m_forecast_allocation_report(token_001m,start_date=start_date,end_date=end_date,component_description=additional_filter_value)
        elif additional_filter == "site-allocation":
            data = get_001m_forecast_allocation_report(token_001m,start_date=start_date,end_date=end_date,site_allocation=additional_filter_value)
        else:
            data = get_001m_forecast_allocation_report(token_001m,start_date=start_date,end_date=end_date,search=additional_filter_value)

        if data :
            message = "Berikut Daily External Report:" if language == "indonesia" else "Here are Daily External Report :"

            for i in range(len(data)):
                message += f"- No: {i+1}\n"
                message += f"- Manufacture: {data[i].get('mtn_information', {}).get('model', {}).get('manufacturer', {}).get('name', None)}\n"
                message += f"- Model: {data[i].get('mtn_information', {}).get('model', {}).get('name', None)}\n"
                message += f"- MTN Routable: {data[i].get('mtn_information', {}).get('serial_number', None)}\n"
                message += f"- Comp. Part Number: {data[i].get('component', {}).get('name', None)}\n"
                message += f"- Comp. Description: {data[i].get('component_description', None)}\n"
                message += f"- Workorder No.: {data[i].get('workorder_information', {}).get('001m_workorder_number', None)}\n"
                message += f"- Process: {data[i].get('production_line', {}).get('status_process', None)}\n"
                message += f"- Start Job: {reformat_date(data[i].get('repair_information', {}).get('date_register_job', None),lang=language)}\n"
                message += f"- Estimated Finish Date: {reformat_date(data[i].get('production_line', {}).get('estimated_finish_date', None),lang=language)}\n"
                message += f"- Duration WIP: {data[i].get('actual_duration', None)}\n"
                message += f"- Status: {data[i].get('repair_information', {}).get('status_wip', None)}\n"
                message += f"- Progress: {data[i].get('repair_information', {}).get('progress', None)}\n"
                message += "\n"

            dispatcher.utter_message(text=message)

        else:
            if language == "indonesia" :
                dispatcher.utter_message(text="Maaf, Tidak ada data yang tersedia")
                
            else :
                dispatcher.utter_message(text="Sorry, there was no available data.")
        return [SlotSet("additional_001m_forecast_report", None), SlotSet("additional_001m_forecast_report_value",None)]


class ActionCancelFollowup001MForecastAllocationReport(Action):
    def name(self) -> str:
        return "action_cancel_followup_001m_forecast_allocation_report"
   
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        if language == "indonesia":
            dispatcher.utter_message("Terima kasih")
        else:    
            dispatcher.utter_message("Thankyou")
           
        return [SlotSet("date_001m_forecast_allocation_report",None), SlotSet("additional_001m_forecast_report", None), SlotSet("additional_001m_forecast_report_value",None)]