from typing import Text, Any, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction
import requests
import jwt
import snakemd
from babel.dates import format_datetime
import logging
from datetime import datetime, timedelta, date

from actions.schema import MessageSelectOptions,MessageSchema,MessageRangePicker,MessageDatePicker

from actions.services.ess.api import (get_ess_token, get_profile_ess, fetch_data_timeoff)

logger = logging.getLogger(__name__)
logger.info("Starting Action ESS TimeOff Actions")

class ActionESSGetSummaryEmployeeLeaveInfo(Action):
    def name(self) -> str:
        return "action_get_ess_summary_employee_leave_info"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_ess = get_ess_token(tracker)
        date_summary_employee_leave = tracker.get_slot("date_summary_employee_leave")
        
        try:
            user_nik = get_profile_ess(token_ess)
            if user_nik is None:
                logger.error("User NIK not found from token ess")
                return [SlotSet('date_summary_employee_leave', None)]
            
            user_nik = user_nik.get("nik")
            # stmt = ("""
            #         SELECT ul.nik
            #             FROM user_levels ul
            #             JOIN levels l ON l.id = ul.level_id
            #             WHERE l.sequence < (
            #                 SELECT l.sequence
            #                 FROM user_levels ul_sub
            #                 JOIN levels l ON l.id = ul_sub.level_id
            #                 WHERE ul_sub.nik = %s LIMIT 1 ) 
            #                 """
            #         )
            # available_user = fetch_data(stmt, (user_nik,))
            # if not available_user:
            #     logger.error(f"User with NIK {user_nik} not found")
            
            stmt = (
                """
                SELECT to2.nik, to2.request_date , to2.active_date , sa.status, tot.name , u.name AS nama 
                        FROM time_off to2 
                            JOIN status_approval sa  ON sa.id = to2.status_id 
                            JOIN time_off_type tot ON to2.time_off_type_id  = tot.id
                            JOIN users u ON u.nik = to2.nik 
                        WHERE u.nik != %s  AND to2.request_date >= %s AND to2.active_date <=%s
                    """
                    )
            
            value = fetch_data_timeoff(stmt, (user_nik,date_summary_employee_leave,date_summary_employee_leave))
            logger.info(value)
            logger.info(date_summary_employee_leave)
            if not value:
                logger.error(f"User with NIK {user_nik} not found or no timeoff data")
                return [SlotSet('date_summary_employee_leave', None)]

            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                try:
                    formatted_date = format_datetime(datetime.strptime(date_summary_employee_leave, "%Y-%m-%d"), "d MMMM yyyy", locale="id")
                except Exception:
                    formatted_date = date_summary_employee_leave
                
                message = (f"Berikut list karyawan yang cuti pada tanggal {formatted_date}\n")
                for idx, k in enumerate(value, start=1):
                    table_data.append([
                        f"{idx}",
                        f"{k['nik']}",
                        f"{k['nama']}",
                        f"{format_datetime(k['request_date'], 'EEEE, d MMMM yyyy', locale='id' if language == 'indonesia' else 'en')}",
                        f"{format_datetime(k['active_date'], 'EEEE, d MMMM yyyy', locale='id' if language == 'indonesia' else 'en')}",
                        f"{k['name']}"
                    ])
                dispatcher.utter_message(message)
                doc.add_table(header=["No","NIK","Nama","Tanggal Pengajuan","Tanggal Cuti Berakhir","Jenis Cuti / Ijin"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())
                return [SlotSet('date_summary_employee_leave', None)]

            else:
                try:
                    formatted_date = format_datetime(datetime.strptime(date_summary_employee_leave, "%Y-%m-%d"), "d MMMM yyyy", locale="en")
                except Exception:
                    formatted_date = date_summary_employee_leave
                
                message = (f"Here is the list of employees who are off on {formatted_date}\n")
                for idx, k in enumerate(value, start=1):
                    table_data.append([
                        f"{idx}",
                        f"{k['nik']}",
                        f"{k['nama']}",
                        f"{format_datetime(k['request_date'], 'EEEE, d MMMM yyyy', locale='id' if language == 'indonesia' else 'en')}",
                        f"{format_datetime(k['active_date'], 'EEEE, d MMMM yyyy', locale='id' if language == 'indonesia' else 'en')}",
                        f"{k['name']}"
                    ])
                dispatcher.utter_message(message)
                doc.add_table(header=["No","NIK","Name","Submission Date","End of Leave Date","Leave Type"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())
                return [SlotSet('date_summary_employee_leave', None)]
                                    
        except Exception as e:
            logger.error(f"Error to execute ActionESSGetLeaveByNIK : {e}")
            if language == 'indonesia':
                message = "Terdapat kesalahan dari server"
            else:
                message = "There was an error from server"
            dispatcher.utter_message(message)
            return [SlotSet('date_summary_employee_leave', None)]

      
class AskInputNIKSubordinate(Action):
    def name(self):
        return "action_ask_date_summary_employee_leave"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        message = MessageSchema("options")
        message_date_picker = MessageDatePicker("Pilih Tanggal/ Choose Date")
        message.add_date_picker(message_date_picker)

        if language == "indonesia":
            dispatcher.utter_message(text = "Silakan masukkan tanggal. Harap gunakan format YYYY-mm-dd, contoh: 2024-12-01", json_message=message.to_dict())
        else:
            dispatcher.utter_message(text = "Please enter the date. Use the format YYYY-mm-dd, for example: 2024-12-01", json_message=message.to_dict())
        return []
