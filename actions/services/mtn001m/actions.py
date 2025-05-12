
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
from actions.services.mtn001m.api import get_001m_token,get_001m_report_daily_internal,get_001m_report_daily_external,get_001m_component_description,get_001m_model_dropdown,get_001m_internal_status_process,get_001m_forecast_allocation_report, reformat_date, get_001m_site_allocation,get_001m_model_manufacturers, get_001m_jobs, get_001m_timesheets, get_001m_job_detail, get_001m_shipment, get_001m_shipment_detail

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
    

class ActionAskDateForecastAllocationReport(Action):
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
    
class ActionAskAdditional001MForecastValue(Action):

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


class ActionAskComponentName001M(Action):

    def name(self)-> str:
        return "action_ask_component_name_001m"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any])-> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text="Tolong sebutkan komponen yang Anda cari, contohnya: DESCMTNR")
        
        else:
            dispatcher.utter_message(text="Please state the component you are looking for, example: DESCMTNR")
        
        return []
    
class ActionGet001MComponentEstimatedFinishDateForecastAllocationReport(Action):
    def name(self) -> str:
        return "action_get_001m_component_estimated_finish_date_forecast_allocation_report"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any])-> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        component_name = tracker.get_slot("component_name_001m")
        token_001m = get_001m_token(tracker)
        data = get_001m_jobs(token_001m=token_001m,  q_filter="comp_name", filter_value=[component_name])
        message = ""
        if data:
            if len(data):
                if language == "indonesia":
                    message = f"Komponen {data[0]['mtn_information']['serial_number']} masih dalam proses, komponen ini diperkirakan selesai pada tanggal **{reformat_date(data[0]['production_line']['estimated_finish_date'])}**"
                else:
                    message = f"Component {data[0]['mtn_information']['serial_number']} is still in process, this component estimated will be done on **{reformat_date(data[0]['production_line']['estimated_finish_date'], 'english')}**"
            else:
                if language == "indonesia":
                    message = f"Maaf, tidak ditemukan data untuk komponen {component_name}"
                else:
                    message = f"Sorry, there's no data for component {component_name}"
        else:
            if language == "indonesia":
                message = "Maaf, sedang terjadi error dalam server"
            else:
                message = "Sorry, there was error on server"
        
        dispatcher.utter_message(message)



        return [SlotSet("component_name_001m", None)]
    
class ActionGet001MComponentRepairLocationForecastAllocationReport(Action):

    def name(self)-> str:
        return "action_get_001m_component_repair_location_forecast_allocation_report"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any])-> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        component_name = tracker.get_slot("component_name_001m")
        token_001m = get_001m_token(tracker)
        data = get_001m_jobs(token_001m=token_001m, q_filter="comp_name", filter_value=[component_name])
        message = ""
        doc = snakemd.Document()
        table_data = []

        if data:
            if len(data):
                if language == "indonesia":
                    message = f"Baik, informasi perbaikan untuk komponen **{data[0]['mtn_information']['serial_number']}** adalah sebagai berikut:\n"
                    table_data.append(["Manufacture", data[0]['mtn_information']['model']['manufacturer']['name']])
                    table_data.append(["Model", data[0]['mtn_information']['model']['name']])
                    table_data.append(["Comp. Description", data[0]['mtn_information']['component_description']])
                    table_data.append(["Repair By", data[0]['repair_information']['repair_by']])
                    table_data.append(["Repair/Rebuild As", data[0]['repair_information']['repair_rebuild_as']])
                    table_data.append(["Repair Location", data[0]['repair_information']['repair_location']])
                    table_data.append(["Process", data[0]['production_line']['status_process']])
                    table_data.append(["Progress", f"{data[0]['repair_information']['progress']}%"])
                    table_data.append(["Component Status", data[0]['repair_information']['component_status']])
                    table_data.append(["Estimated Finish Date", reformat_date(data[0]['production_line']['estimated_finish_date'])])

                else:
                    message = f"The information for component **{data[0]['mtn_information']['serial_number']}** are:\n"
                    table_data.append(["Model", data[0]['mtn_information']['model']['name']])
                    table_data.append(["Comp. Description", data[0]['mtn_information']['component_description']])
                    table_data.append(["Repair By", data[0]['repair_information']['repair_by']])
                    table_data.append(["Repair/Rebuild As", data[0]['repair_information']['repair_rebuild_as']])
                    table_data.append(["Repair Location", data[0]['repair_information']['repair_location']])
                    table_data.append(["Process", data[0]['production_line']['status_process']])
                    table_data.append(["Progress", f"{data[0]['repair_information']['progress']}%"])
                    table_data.append(["Component Status", data[0]['repair_information']['component_status']])
                    table_data.append(["Estimated Finish Date", reformat_date(data[0]['production_line']['estimated_finish_date'])])

            else:
                if language == "indonesia":
                    message = f"Maaf, tidak ditemukan data untuk komponen {component_name}"
                else:
                    message = f"Sorry, there's no data for component {component_name}"
        else:
            if language == "indonesia":
                message = "Maaf, sedang terjadi error dalam server"
            else:
                message = "Sorry, there was error on server"
        


        dispatcher.utter_message(message)

        if len(table_data):
            doc.add_table(header=["Name", "Value"], data= table_data)
            dispatcher.utter_message(doc.__str__())


        return [SlotSet("component_name_001m", None)]

class ActionGet001MApprovalRouteForecastAllocationReport(Action):
    def name(self)-> str:
        return "action_get_001m_approval_route_forecast_allocation_report"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any])-> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        component_name = tracker.get_slot("component_name_001m")
        token_001m = get_001m_token(tracker)
        data = get_001m_jobs(token_001m=token_001m,  q_filter="comp_name", filter_value=[component_name])
        message = ""
        doc = snakemd.Document()
        table_data = []
        if data:
            if len(data):
                if language=="indonesia":

                    message = f"Berikut proses persetujuan perbaikan komponen **{data[0]['mtn_information']['serial_number']}** dilakukan oleh:\n"
                    message+= f"- Current Approval Status: **{self.approval_status_to_text(data[0]['approval_route']['approval_status'],data)}** \n"
                    message+= "\n"
                    message+= f"Approval Route Details:\n"
                    message+= f"- Supervisor: \n"
                    message+= f"Name: {data[0]['approval_route']['plant_supervisor']['name']}\n"
                    message+= f"Role: {data[0]['approval_route']['plant_supervisor']['role']['name']}\n"
                    if data[0]['approval_route']['plant_supervisor'].get('approval_status',None):
                        message+= f"Approval Status: {'Approved' if data[0]['approval_route']['plant_supervisor']['approval_status'] else 'Not Approved'}\n"#Approved" if approval_status else "Not Approved"---> nilainya true and false. true (approved) false (not approved)
                        message+= f"Approval Comment: {data[0]['approval_route']['plant_supervisor']['approval_comment']}\n"

                    message += "\n"
                    
                    message+=f"- Superintendent: \n"
                    message+=f"Name: {data[0]['approval_route']['plant_superintendent']['name']} \n"
                    message+=f"Role: {data[0]['approval_route']['plant_superintendent']['role']['name']}\n"
                    if data[0]['approval_route']['plant_superintendent'].get('approval_status',None):
                        message+= f"Approval Status: {'Approved' if data[0]['approval_route']['plant_superintendent']['approval_status'] else 'Not Approved'}\n"#Approved" if approval_status else "Not Approved"---> nilainya true and false. true (approved) false (not approved)
                        message+= f"Approval Comment: {data[0]['approval_route']['plant_superintendent']['approval_comment']}\n"
                    
                    message+= "\n"
                    
                    message+=f"- Manager: \n"
                    message+=f"Name: {data[0]['approval_route']['plant_manager']['name']} \n"
                    message+=f"Role: {data[0]['approval_route']['plant_manager']['role']['name']}\n"
                    if data[0]['approval_route']['plant_manager'].get('approval_status',None):
                        message+= f"Approval Status: {'Approved' if data[0]['approval_route']['plant_manager']['approval_status'] else 'Not Approved'}\n"#Approved" if approval_status else "Not Approved"---> nilainya true and false. true (approved) false (not approved)
                        message+= f"Approval Comment: {data[0]['approval_route']['plant_manager']['approval_comment']}\n"
                    
                    message+= "\n"
                
                else:
                    message = f"Here are approval process of **{data[0]['mtn_information']['serial_number']}** :\n"
                    message+= f"- Current Approval Status: **{self.approval_status_to_text(data[0]['approval_route']['approval_status'],data)}** \n"
                    message+= "\n"
                    message+= f"Approval Route Details:\n"
                    message+= f"- Supervisor: \n"
                    message+= f"Name: {data[0]['approval_route']['plant_supervisor']['name']}\n"
                    message+= f"Role: {data[0]['approval_route']['plant_supervisor']['role']['name']}\n"
                    if data[0]['approval_route']['plant_supervisor'].get('approval_status',None):
                        message+= f"Approval Status: {'Approved' if data[0]['approval_route']['plant_supervisor']['approval_status'] else 'Not Approved'}\n"#Approved" if approval_status else "Not Approved"---> nilainya true and false. true (approved) false (not approved)
                        message+= f"Approval Comment: {data[0]['approval_route']['plant_supervisor']['approval_comment']}\n"

                    message += "\n"
                    
                    message+=f"- Superintendent: \n"
                    message+=f"Name: {data[0]['approval_route']['plant_superintendent']['name']} \n"
                    message+=f"Role: {data[0]['approval_route']['plant_superintendent']['role']['name']}\n"
                    if data[0]['approval_route']['plant_superintendent'].get('approval_status',None):
                        message+= f"Approval Status: {'Approved' if data[0]['approval_route']['plant_superintendent']['approval_status'] else 'Not Approved'}\n"#Approved" if approval_status else "Not Approved"---> nilainya true and false. true (approved) false (not approved)
                        message+= f"Approval Comment: {data[0]['approval_route']['plant_superintendent']['approval_comment']}\n"
                    
                    message+= "\n"
                    
                    message+=f"- Manager: \n"
                    message+=f"Name: {data[0]['approval_route']['plant_manager']['name']} \n"
                    message+=f"Role: {data[0]['approval_route']['plant_manager']['role']['name']}\n"
                    if data[0]['approval_route']['plant_manager'].get('approval_status',None):
                        message+= f"Approval Status: {'Approved' if data[0]['approval_route']['plant_manager']['approval_status'] else 'Not Approved'}\n"#Approved" if approval_status else "Not Approved"---> nilainya true and false. true (approved) false (not approved)
                        message+= f"Approval Comment: {data[0]['approval_route']['plant_manager']['approval_comment']}\n"
                    
                    message+= "\n"

            else:
                if language == "indonesia":
                    message = f"Maaf, tidak ditemukan data untuk komponen {component_name}"
                else:
                    message = f"Sorry, there's no data for component {component_name}"
        else:
            if language == "indonesia":
                message = "Maaf, sedang terjadi error dalam server"
            else:
                message = "Sorry, there was error on server"
        dispatcher.utter_message(message)
        if len(table_data):
            doc.add_table(header=["Name", "Value"], data= table_data)
            dispatcher.utter_message(doc.__str__())
        return [SlotSet("component_name_001m", None)]

    def approval_status_to_text(self,status,data)-> str:
        if status == None :
            if not data[0]['approval_route']['plant_supervisor'].get('approval_status',None):
                return "Waiting Approval Supervisor"
            
            if not data[0]['approval_route']['plant_superintendent'].get('approval_status',None):
                return "Waiting Approval Superintendent"

            if not data[0]['approval_route']['plant_manager'].get('approval_status',None):
                return "Waiting Approval Manager"
            return "Waiting Approval"
        
        if status == 0 :
            return "Waiting Approval Supervisor"

        if status == 1 :
            return "Waiting Approval Superintendent"

        if status == 2:
            return "Waiting Approval Manager"
        
        if status == 4:
            return "Waiting Approval Admin"
        
        if status == -4:
            return "Not Approved by Admin"

        if status == -1 :
            return "Not Approved by Superintendent"
        
        if status == -2 :
            return "Not Approved by Manager"

    
class ActionGet001MMechanicNameOnComponentRepairsForecastAllocationReport(Action):
    def name(self)-> str:
        return "action_get_001m_mechanic_name_on_component_repairs_forecast_allocation_report"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any])-> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        component_name = tracker.get_slot("component_name_001m")
        token_001m = get_001m_token(tracker)
        data = get_001m_jobs(token_001m=token_001m, q_filter="comp_name", filter_value=[component_name])
        message = ""
        doc = snakemd.Document()
        table_data = []
        if data:
            if len(data):
                data_timesheet = get_001m_timesheets(token_001m=token_001m,q_filter="job-id",filter_value=[data[0]['id']])
                if language == "indonesia":
                    message = f"Saat ini, perbaikan komponen **{data[0]['mtn_information']['serial_number']}** sedang dikerjakan oleh:\n"
                    table_data.append(["Manufacture", data[0]['mtn_information']['model']['manufacturer']['name']])
                    table_data.append(["Model", data[0]['mtn_information']['model']['name']])
                    table_data.append(["Comp. Description", data[0]['mtn_information']['component_description']])
                    table_data.append(["Mechanic Name", data_timesheet[0]['mechanic']['name']])
                    table_data.append(["Mechanic NIK", data_timesheet[0]['mechanic']['nik']])
                    table_data.append(["Repair Location", data[0]['repair_information']['repair_location']])
                    table_data.append(["Progress", f"{data[0]['repair_information']['progress']}%"])
                    table_data.append(["Status Process", data_timesheet[0]['status_process']])
                    table_data.append(["Estimated Finish Date", reformat_date(data[0]['production_line']['estimated_finish_date'])])

                else:
                    message = f"Currently, component **{data[0]['mtn_information']['serial_number']}** is worked by:\n"
                    table_data.append(["Manufacture", data[0]['mtn_information']['model']['manufacturer']['name']])
                    table_data.append(["Model", data[0]['mtn_information']['model']['name']])
                    table_data.append(["Comp. Description", data[0]['mtn_information']['component_description']])
                    table_data.append(["Mechanic Name", data_timesheet[0]['mechanic']['name']])
                    table_data.append(["Mechanic NIK", data_timesheet[0]['mechanic']['nik']])
                    table_data.append(["Repair Location", data[0]['repair_information']['repair_location']])
                    table_data.append(["Progress", f"{data[0]['repair_information']['progress']}%"])
                    table_data.append(["Status Process", data_timesheet[0]['status_process']])
                    table_data.append(["Estimated Finish Date", reformat_date(data[0]['production_line']['estimated_finish_date'])])

            else:
                if language == "indonesia":
                    message = f"Maaf, tidak ditemukan data untuk komponen {component_name}"
                else:
                    message = f"Sorry, there's no data for component {component_name}"
        else:
            if language == "indonesia":
                message = "Maaf, sedang terjadi error dalam server"
            else:
                message = "Sorry, there was error on server"

        dispatcher.utter_message(message)
        if len(table_data):
            doc.add_table(header=["Name", "Value"], data= table_data)
            dispatcher.utter_message(doc.__str__())

        return [SlotSet("component_name_001m", None)]

class ActionGet001MechanicCurrentTaskOnComponentRepairsForecastAllocationReport(Action):
    def name(self)-> str:
        return "action_get_001m_mechanic_current_task_on_component_repairs_forecast_allocation_report"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any])-> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        component_name = tracker.get_slot("mechanic_nik_001m")
        token_001m = get_001m_token(tracker)
        data_timesheet = get_001m_timesheets(token_001m=token_001m,q_filter="mechanic",filter_value=[component_name])
        message = ""
        doc = snakemd.Document()
        table_data = []
        if data_timesheet:
            if len(data_timesheet):
                data = get_001m_job_detail(token_001m=token_001m, job_id=data_timesheet[0]['job']['id'])
                if language == "indonesia":
                    message = f"Saat ini, **{data_timesheet[0]['mechanic']['name']}** sedang mengerjakan perbaikan pada komponen **{data[0]['mtn_information']['serial_number']}**\n"
                    table_data.append(["Manufacture", data[0]['mtn_information']['model']['manufacturer']['name']])
                    table_data.append(["Model", data[0]['mtn_information']['model']['name']])
                    table_data.append(["Comp. Description", data[0]['mtn_information']['component_description']])
                    table_data.append(["Repair Location", data[0]['repair_information']['repair_location']])
                    table_data.append(["Progress", f"{data[0]['repair_information']['progress']}%"])
                    table_data.append(["Component Status", data[0]['repair_information']['component_status']])
                    table_data.append(["Estimated Finish Date", reformat_date(data[0]['production_line']['estimated_finish_date'])])

                else:
                    message = f"Currently, **{data_timesheet[0]['mechanic']['name']}** is fixing on component **{data[0]['mtn_information']['serial_number']}**\n"
                    table_data.append(["Manufacture", data[0]['mtn_information']['model']['manufacturer']['name']])
                    table_data.append(["Model", data[0]['mtn_information']['model']['name']])
                    table_data.append(["Comp. Description", data[0]['mtn_information']['component_description']])
                    table_data.append(["Repair Location", data[0]['repair_information']['repair_location']])
                    table_data.append(["Progress", f"{data[0]['repair_information']['progress']}%"])
                    table_data.append(["Component Status", data[0]['repair_information']['component_status']])
                    table_data.append(["Estimated Finish Date", reformat_date(data[0]['production_line']['estimated_finish_date'])])

            else:
                if language == "indonesia":
                    message = f"Maaf, tidak ditemukan data untuk mekanik {component_name}"
                else:
                    message = f"Sorry, there's no data for mechanic {component_name}"
        else:
            if language == "indonesia":
                message = "Maaf, sedang terjadi error dalam server"
            else:
                message = "Sorry, there was error on server"
        
        dispatcher.utter_message(message)
        if len(table_data):
            doc.add_table(header=["Name", "Value"], data= table_data)
            dispatcher.utter_message(doc.__str__())
        return [SlotSet("mechanic_nik_001m", None)]
    

class ActionAskMechanicNIK001M(Action):
    def name(self)-> str:
        return "action_ask_mechanic_nik_001m"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any])-> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text="Tolong sebutkan NIK mekanik yang Anda cari, contohnya: 1010")
        
        else:
            dispatcher.utter_message(text="Please state the mechanic NIK you are looking for, example: 1010")
        
        return []
    

class ActionGet001MShipmentStatusForComponentRepairsTraceabilityReport(Action):
    def name(self)-> str:
        return "action_get_001m_shipment_status_for_component_repairs_traceabilty_report"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any])-> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        component_name = tracker.get_slot("component_name_001m")
        token_001m = get_001m_token(tracker)
        data = get_001m_jobs(token_001m=token_001m, q_filter="comp_name", filter_value=[component_name])
        doc = snakemd.Document()
        table_data = []
        if data:
            if len(data):
                data_shipment = get_001m_shipment(token_001m=token_001m,q_filter="job-id",filter_value=[data[0].get("id",1)])
                data_detail = get_001m_shipment_detail(token_001m=token_001m,shipment_id=data_shipment[0].get("id",1))
                if language == "indonesia":
                    message = f"Baik, status pengiriman untuk komponen **{component_name}** saat ini:\n"
                    message+= f"Job Details:\n"
                    message+= f"- Manufacture: {data_shipment[0]['manufacturer']}\n"
                    message+= f"- Model: {data_shipment[0]['model']}\n"
                    message+= f"- MTN Routable: {data_shipment[0]['serial_number']}\n"
                    message+= f"- Component Part Number: {data_shipment[0]['component']}\n"
                    message+= f"- Component Description: {data_shipment[0]['component_description']}\n"
                    message+= f"- Component Status: {data_shipment[0]['component_status']}\n"
                    message+= f"- Site Origin: {data_shipment[0]['site_origin']}\n"
                    message+= f"- Unit Origin: {data_shipment[0]['unit_origin']}\n"
                    message+= f"- Site Allocation: {data_shipment[0]['site_allocation']}\n"
                    message+= f"- Unit Allocation: {data_shipment[0]['unit_allocation']}\n"
                    message+= f"- Last Updated: {reformat_date(data_shipment[0]['updated_at'])}\n"
                    message+= f"- Process: {data_shipment[0]['status']['name']}\n"

                    message+= "\n"

                    message+=f"Progress Details:\n"

                    for i in range(len(data_detail.get("timeline",[]))):
                        message+=f"- Date: {data_detail['timeline'][i]['updated_at']}\n"
                        message+=f"Status: {data_detail['timeline'][i]['status']['name']}\n"
                        message+=f"Updated by: {data_detail['timeline'][i]['user']['nik']} - {data_detail['timeline'][i]['user']['name']} - {data_detail['timeline'][i]['user']['role']['name']} \n"
                        message+=f"Description: {data_detail['timeline'][i]['description']}\n"


                else:
                    message = f"Currently, component **{data[0]['mtn_information']['serial_number']}** is worked by:\n"
                    message+= f"Job Details:\n"
                    message+= f"- Manufacture: {data_shipment[0]['manufacturer']}\n"
                    message+= f"- Model: {data_shipment[0]['model']}\n"
                    message+= f"- MTN Routable: {data_shipment[0]['serial_number']}\n"
                    message+= f"- Component Part Number: {data_shipment[0]['component']}\n"
                    message+= f"- Component Description: {data_shipment[0]['component_description']}\n"
                    message+= f"- Component Status: {data_shipment[0]['component_status']}\n"
                    message+= f"- Site Origin: {data_shipment[0]['site_origin']}\n"
                    message+= f"- Unit Origin: {data_shipment[0]['unit_origin']}\n"
                    message+= f"- Site Allocation: {data_shipment[0]['site_allocation']}\n"
                    message+= f"- Unit Allocation: {data_shipment[0]['unit_allocation']}\n"
                    message+= f"- Last Updated: {reformat_date(data_shipment[0]['updated_at'])}\n"
                    message+= f"- Process: {data_shipment[0]['status']['name']}\n"

                    message+= "\n"

                    message+=f"Progress Details:\n"

                    for i in range(len(data_detail.get("timeline",[]))):
                        message+=f"- Date: {data_detail['timeline'][i]['updated_at']}\n"
                        message+=f"Status: {data_detail['timeline'][i]['status']['name']}\n"
                        message+=f"Updated by: {data_detail['timeline'][i]['user']['nik']} - {data_detail['timeline'][i]['user']['name']} - {data_detail['timeline'][i]['user']['role']['name']} \n"
                        message+=f"Description: {data_detail['timeline'][i]['description']}\n"

            else:
                if language == "indonesia":
                    message = f"Maaf, tidak ditemukan data untuk komponen {component_name}"
                else:
                    message = f"Sorry, there's no data for component {component_name}"
        else:
            if language == "indonesia":
                message = "Maaf, sedang terjadi error dalam server"
            else:
                message = "Sorry, there was error on server"
        
        dispatcher.utter_message(message)

        if len(table_data):
            doc.add_table(header=["Name", "Value"], data= table_data)
            dispatcher.utter_message(doc.__str__())
        
        return [SlotSet("component_name_001m", None)]



