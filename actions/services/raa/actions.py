
from typing import Text, Any, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction
import requests
import jwt
import snakemd
import logging
from datetime import datetime, timedelta, date
from babel.dates import format_datetime

from actions.services.raa.api import (
                get_attendace_raa, 
                 get_employee_perf_raa, 
                 get_information_all_departments_raa, 
                 get_information_all_position_raa, 
                 get_project_sites_raa, 
                 get_user_profile_raa, 
                 get_raa_token, 
                 get_raa_token_api
                 )

logger = logging.getLogger(__name__)
logger.info("Starting Action RAA Server")

class ActionGetAttendance(Action):
    def name(self) -> str:
        return "action_get_absence_data"  
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        query_condition = tracker.get_slot("query_condition")
        logger.info(f"Query condition : {query_condition}" )
        language = tracker.get_slot("language")
        logger.info(f"Language : {language}" )
        if query_condition == "today" or query_condition == "hari ini":
            return [FollowupAction("action_attendance_today")]
        elif query_condition == "yesterday" or query_condition == "kemarin":
            return [FollowupAction("action_attendance_yesterday")]

        elif query_condition == "last time" or query_condition == "terakhir kali":
            return [FollowupAction("action_attendance_last_time")]

        if language == "indonesia":
            return dispatcher.utter_message(text="Tidak bisa memroses pesan") 

        return dispatcher.utter_message(text="Cannot proceed your message")
    
class ActionAttendanceToday(Action):
    def name(self) -> str:
        return "action_attendance_today"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        doc = snakemd.Document()
        table_data = []

        if language == "indonesia":
            if token_raa is not None:
                value = get_attendace_raa(token_raa, "today")
                if value is not None:
                    date = datetime.strptime(value['date'], '%Y-%m-%d')
                    message = f"Absensi pada tanggal {format_datetime(date, format='d MMMM yyyy', locale='id')}:\n"
                    table_data.append(["NIK", f"{value['nik']}"])
                    table_data.append(["Clock-in", format_datetime(datetime.strptime(value['clockin_time'], '%Y-%m-%dT%H:%M:%S.%fZ'), format='d MMMM yyyy HH:mm:ss', locale='id') if value.get('clockin_time') else "N/A"])
                    table_data.append(["Project ID (Clock-in)", f"{value['project_id_clockin']}" if value.get('project_id_clockin') else "N/A"])
                    table_data.append(["Clock-out", format_datetime(datetime.strptime(value['clockout_time'], '%Y-%m-%dT%H:%M:%S.%fZ'), format='d MMMM yyyy HH:mm:ss', locale='id') if value.get('clockout_time') else "N/A"])
                    table_data.append(["Project ID (Clock-out)", f"{value['project_id_clockout']}" if value.get('project_id_clockout') else "N/A"])
                    dispatcher.utter_message(text=message)
                    doc.add_table(header=["Deskripsi", "Nilai"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())
                else:
                    dispatcher.utter_message(text="Terjadi kesalahan pada pengambilan absensi")
            else:
                dispatcher.utter_message(text="Terjadi kesalahan pada pengambilan absensi")
        
        else:
            if token_raa is not None:
                value = get_attendace_raa(token_raa, "today")
                if value is not None:
                    date = datetime.strptime(value['date'], '%Y-%m-%d')
                    message = f"Absensi pada tanggal {format_datetime(date, format='d MMMM yyyy', locale='id')}:\n"
                    table_data.append(["NIK", f"{value['nik']}"])
                    table_data.append(["Clock-in", format_datetime(datetime.strptime(value['clockin_time'], '%Y-%m-%dT%H:%M:%S.%fZ'), format='d MMMM yyyy HH:mm:ss', locale='id') if value.get('clockin_time') else "N/A"])
                    table_data.append(["Project ID (Clock-in)", f"{value['project_id_clockin']}" if value.get('project_id_clockin') else "N/A"])
                    table_data.append(["Clock-out", format_datetime(datetime.strptime(value['clockout_time'], '%Y-%m-%dT%H:%M:%S.%fZ'), format='d MMMM yyyy HH:mm:ss', locale='id') if value.get('clockout_time') else "N/A"])
                    table_data.append(["Project ID (Clock-out)", f"{value['project_id_clockout']}" if value.get('project_id_clockout') else "N/A"])
                    dispatcher.utter_message(text=message)
                    doc.add_table(header=["Deskripsi", "Nilai"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())
                else:
                    dispatcher.utter_message(response="There was an error while processing the request")
            else:
                dispatcher.utter_message(response="There was an error while processing the request")
        return []

class ActionAttendanceYesterday(Action):
    def name(self) -> str:
        return "action_attendance_yesterday"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            language = tracker.get_slot("language")
            token_raa = get_raa_token(tracker)
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                if token_raa is not None:
                    value = get_attendace_raa(token_raa,"yesterday")
                    if value is not None:
                        date = datetime.strptime(value['date'], '%Y-%m-%d')
                        message = f"Absensi pada tanggal {format_datetime(date, format='d MMMM yyyy', locale='id')}:\n"
                        table_data.append(["NIK", f"{value['nik']}"])
                        table_data.append(["Clock-in", format_datetime(datetime.strptime(value['clockin_time'], '%Y-%m-%dT%H:%M:%S.%fZ'), format='d MMMM yyyy HH:mm:ss', locale='id') if value.get('clockin_time') else "N/A"])
                        table_data.append(["Project ID (Clock-in)", f"{value['project_id_clockin']}" if value.get('project_id_clockin') else "N/A"])
                        table_data.append(["Clock-out", format_datetime(datetime.strptime(value['clockout_time'], '%Y-%m-%dT%H:%M:%S.%fZ'), format='d MMMM yyyy HH:mm:ss', locale='id') if value.get('clockout_time') else "N/A"])
                        table_data.append(["Project ID (Clock-out)", f"{value['project_id_clockout']}" if value.get('project_id_clockout') else "N/A"])
                        dispatcher.utter_message(text=message)
                        doc.add_table(header=["Deskripsi", "Nilai"], data=table_data)
                        dispatcher.utter_message(text=doc.__str__())
                    else:
                        dispatcher.utter_message(text="Terjadi kesalahan pada pengambilan absensi")    
                else:
                    dispatcher.utter_message(text="Terjadi kesalahan pada pengambilan absensi")
            else:
                if token_raa is not None:
                    value = get_attendace_raa(token_raa, "yesterday")
                    if value is not None:
                        date = datetime.strptime(value['date'], '%Y-%m-%d')
                        message = f"Absensi pada tanggal {format_datetime(date, format='d MMMM yyyy', locale='id')}:\n"
                        table_data.append(["NIK", f"{value['nik']}"])
                        table_data.append(["Clock-in", format_datetime(datetime.strptime(value['clockin_time'], '%Y-%m-%dT%H:%M:%S.%fZ'), format='d MMMM yyyy HH:mm:ss', locale='id') if value.get('clockin_time') else "N/A"])
                        table_data.append(["Project ID (Clock-in)", f"{value['project_id_clockin']}" if value.get('project_id_clockin') else "N/A"])
                        table_data.append(["Clock-out", format_datetime(datetime.strptime(value['clockout_time'], '%Y-%m-%dT%H:%M:%S.%fZ'), format='d MMMM yyyy HH:mm:ss', locale='id') if value.get('clockout_time') else "N/A"])
                        table_data.append(["Project ID (Clock-out)", f"{value['project_id_clockout']}" if value.get('project_id_clockout') else "N/A"])
                        dispatcher.utter_message(text=message)
                        doc.add_table(header=["Deskripsi", "Nilai"], data=table_data)
                        dispatcher.utter_message(text=doc.__str__())
                    else:
                        dispatcher.utter_message(response="There was an error while processing the request")
                else:
                    dispatcher.utter_message(response="There was an error while processing the request")

            return []

class ActionAttendanceLastTime(Action):
    def name(self) -> str:
        return "action_attendance_last_time"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        doc =snakemd.Document()
        table_data = []
        if language == "indonesia":
            if token_raa is not None:
                value = get_attendace_raa(token_raa, "last time")
                if value is not None:
                    date = datetime.strptime(value['date'], '%Y-%m-%d')
                    message = f"Absensi pada tanggal {format_datetime(date, format='d MMMM yyyy', locale='id')}:\n"
                    table_data.append(["NIK", f"{value['nik']}"])
                    table_data.append(["Clock-in", format_datetime(datetime.strptime(value['clockin_time'], '%Y-%m-%dT%H:%M:%S.%fZ'), format='d MMMM yyyy HH:mm:ss', locale='id') if value.get('clockin_time') else "N/A"])
                    table_data.append(["Project ID (Clock-in)", f"{value['project_id_clockin']}" if value.get('project_id_clockin') else "N/A"])
                    table_data.append(["Clock-out", format_datetime(datetime.strptime(value['clockout_time'], '%Y-%m-%dT%H:%M:%S.%fZ'), format='d MMMM yyyy HH:mm:ss', locale='id') if value.get('clockout_time') else "N/A"])
                    table_data.append(["Project ID (Clock-out)", f"{value['project_id_clockout']}" if value.get('project_id_clockout') else "N/A"])
                    dispatcher.utter_message(text=message)
                    doc.add_table(header=["Deskripsi", "Nilai"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())
                else:
                    dispatcher.utter_message(text="Terjadi kesalahan pada pengambilan absensi")
            else:
                dispatcher.utter_message(text="Terjadi kesalahan pada pengambilan absensi")
        else:
            if token_raa is not None:
                value = get_attendace_raa(token_raa,"last_time")
                if value is not None:
                    date = datetime.strptime(value['date'], '%Y-%m-%d')
                    message = f"Absensi pada tanggal {format_datetime(date, format='d MMMM yyyy', locale='id')}:\n"
                    table_data.append(["NIK", f"{value['nik']}"])
                    table_data.append(["Clock-in", format_datetime(datetime.strptime(value['clockin_time'], '%Y-%m-%dT%H:%M:%S.%fZ'), format='d MMMM yyyy HH:mm:ss', locale='id') if value.get('clockin_time') else "N/A"])
                    table_data.append(["Project ID (Clock-in)", f"{value['project_id_clockin']}" if value.get('project_id_clockin') else "N/A"])
                    table_data.append(["Clock-out", format_datetime(datetime.strptime(value['clockout_time'], '%Y-%m-%dT%H:%M:%S.%fZ'), format='d MMMM yyyy HH:mm:ss', locale='id') if value.get('clockout_time') else "N/A"])
                    table_data.append(["Project ID (Clock-out)", f"{value['project_id_clockout']}" if value.get('project_id_clockout') else "N/A"])
                    dispatcher.utter_message(text=message)
                    doc.add_table(header=["Deskripsi", "Nilai"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())
                else:
                    dispatcher.utter_message(response="There was an error while processing the request")
            else:
                dispatcher.utter_message(response="There was an error while processing the request")
        return []

class ActionGetLeaveRequestsThisMonth(Action):
    def name(self) -> str:
        return "action_get_leave_requests_this_month"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        value = get_employee_perf_raa(token_raa=token_raa, current_month=True, perf_type="cuti", use_dummy_data=True)
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Jumlah {value['legend_name']} yang anda ajukan bulan ini sebanyak **{value['total']}** kali.\n"
                    f"Dengan Presentasi Kehadiran: {value['percentage']}\n"
                )
                dispatcher.utter_message(text=message) if value['total']!=0 else dispatcher.utter_message(text="Berdasarkan data kehadiran Anda, Anda belum mengajukan cuti pada bulan ini.")
            else:
                message = (
                    f"The number of {value['legend_name']} you submitted this month is **{value['total']}** times.\n"
                    f"With Attendance percentage: {value['percentage']}\n"
                )
                dispatcher.utter_message(text=message) if value['total']!=0 else dispatcher.utter_message(text = "Based on your attendance report, you haven't submit a leave request this month.")
        if language == "indonesia":
            dispatcher.utter_message(text="Untuk list lengkap dari performa Anda, dapat dilihat [Link ini](https://dev-super.apps-madhani.com/time-off/request)")
        else:
            dispatcher.utter_message(text="For complete list of your performance, please visit [This link](https://dev-super.apps-madhani.com/time-off/request)")
        return []
    
class ActionGetLeaveRequestsLastMonth(Action):
    def name(self) -> str:
        return "action_get_leave_requests_last_month"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        if token_raa is not None :
            value = get_employee_perf_raa(token_raa=token_raa, current_month=False, perf_type="cuti")
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Jumlah {value['legend_name']} yang anda ajukan bulan lalu sebanyak **{value['total']}** kali.\n"
                    f"Dengan Presentasi Kehadiran: {value['total']}\n"
                )
                dispatcher.utter_message(text=message) if value['total']!=0 else dispatcher.utter_message(text="Berdasarkan data kehadiran Anda, Anda belum mengajukan cuti pada bulan lalu.")
            else:
                message = (
                    f"The number of {value['legend_name']} you submitted last month is **{value['total']}** times."
                    f"With Attendance percentage: {value['percentage']}\n"
                )
                dispatcher.utter_message(text=message) if value['total']!=0 else dispatcher.utter_message(text = "Based on your attendance report, you haven't submit a leave request last month.")
        if language == "indonesia":
            dispatcher.utter_message(text="Untuk list lengkap dari performa Anda, dapat dilihat pada [Link ini](https://dev-super.apps-madhani.com/time-off/request)")
        else:
            dispatcher.utter_message(text="For complete list of your performance, please visit [This link](https://dev-super.apps-madhani.com/time-off/request)")
        return []

class ActionGetAbsenceRequestsThisMonth(Action):
    def name(self) -> str:
        return "action_get_absence_requests_this_month"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        if token_raa is not None :
            value = get_employee_perf_raa(token_raa=token_raa, current_month=True, perf_type="izin",  use_dummy_data=True)
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Jumlah {value['legend_name']} yang anda ajukan bulan ini sebanyak **{value['total']}** kali.\n"
                    f"Dengan Presentasi Kehadiran: {value['percentage']}\n"
                )
                dispatcher.utter_message(text=message) if value['total']!=0 else dispatcher.utter_message(text="Berdasarkan data kehadiran Anda, Anda belum mengajukan izin pada bulan ini.")
            else:
                message = (
                    f"The number of {value['legend_name']} you submitted this month is **{value['total']}** times."
                    f"With Attendance percentage: {value['percentage']}\n"
                )
                dispatcher.utter_message(text=message) if value['total']!=0 else dispatcher.utter_message(text = "Based on your attendance report, you haven't submit a absence request this month.")
        if language == "indonesia":
            dispatcher.utter_message(text="Untuk list lengkap dari performa Anda, dapat dilihat di [Link ini](https://dev-super.apps-madhani.com/time-off/request)")
        else:
            dispatcher.utter_message(text="For complete list of your performance, please visit [This link](https://dev-super.apps-madhani.com/time-off/request)")
        return []

class ActionGetAbsenceRequestsLastMonth(Action):
    def name(self) -> str:
        return "action_get_absence_requests_last_month"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        if token_raa is not None :
            value = get_employee_perf_raa(token_raa=token_raa, current_month=False, perf_type="izin")
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Jumlah {value['legend_name']} yang anda ajukan bulan lalu sebanyak **{value['total']}** kali.\n"
                    f"Dengan Presentasi Kehadiran: {value['percentage']}\n"
                )
                dispatcher.utter_message(text=message) if value['total']!=0 else dispatcher.utter_message(text="Berdasarkan data kehadiran Anda, Anda belum mengajukan izin pada bulan lalu.")
            else:
                message = (
                    f"The number of {value['legend_name']} you submitted last month is **{value['total']}** times."
                    f"With Attendance percentage: {value['percentage']}\n"
                )
                dispatcher.utter_message(text=message) if value['total']!=0 else dispatcher.utter_message(text = "Based on your attendance report, you haven't submit a absence request last month.")
        if language == "indonesia":
            dispatcher.utter_message(text="Untuk list lengkap dari performa Anda, dapat dilihat di [Link ini](https://dev-super.apps-madhani.com/time-off/request)")
        else:
            dispatcher.utter_message(text="For complete list of your performance, please visit [This link](https://dev-super.apps-madhani.com/time-off/request)")
        return []

class ActionGetAlphaAbsenceRequestsThisMonth(Action):
    def name(self) -> str:
        return "action_get_alpha_absence_requests_this_month"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        if token_raa is not None :
            value = get_employee_perf_raa(token_raa=token_raa, current_month=False, perf_type="alpha/mangkir",  use_dummy_data=True)
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Jumlah {value['legend_name']} yang anda ajukan bulan ini sebanyak **{value['total']}** kali.\n"
                    f"Dengan Presentasi Kehadiran: {value['percentage']}\n"
                )
                dispatcher.utter_message(text=message) if value['total']!=0 else dispatcher.utter_message(text="Berdasarkan data kehadiran Anda, Anda belum pernah mangkir pada bulan ini.")
            else:
                message = (
                    f"The number of {value['legend_name']} you submitted this month is **{value['total']}** times.\n"
                    f"With Attendance percentage: {value['percentage']}\n"
                )
                dispatcher.utter_message(text=message) if value['percentage']!=0 else dispatcher.utter_message(text = "Based on your attendance report, you haven't alpha this month.")
        if language == "indonesia":
            dispatcher.utter_message(text="Untuk list lengkap dari performa Anda, dapat dilihat di [Link ini](https://dev-super.apps-madhani.com/time-off/request)")
        else:
            dispatcher.utter_message(text="For complete list of your performance, please visit [This link](https://dev-super.apps-madhani.com/time-off/request)")
        return []
    
class ActionGetAlphaAbsenceRequestsLastMonth(Action):
    def name(self) -> str:
        return "action_get_alpha_absence_requests_last_month"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        if token_raa is not None :
            value = get_employee_perf_raa(token_raa=token_raa, current_month=False, perf_type="alpha/mangkir")
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Jumlah {value['legend_name']} yang anda ajukan bulan lalu sebanyak **{value['total']}** kali.\n"
                    f"Dengan Presentasi Kehadiran: {value['percentage']}\n"
                )
                dispatcher.utter_message(text=message) if value['total']!=0 else dispatcher.utter_message(text="Berdasarkan data kehadiran Anda, Anda belum pernah mangkir pada bulan lalu.")
            else:
                message = (
                    f"The number of {value['legend_name']} you submitted last month is **{value['total']}** times.\n"
                    f"With Attendance percentage: {value['percentage']}\n"
                )
                dispatcher.utter_message(text=message) if value['total']!=0 else dispatcher.utter_message(text = "Based on your attendance report, you haven't alpha last month.")
        if language == "indonesia":
            dispatcher.utter_message(text="Untuk list lengkap dari performa Anda, dapat dilihat di [Link ini](https://dev-super.apps-madhani.com/time-off/request)")
        else:
            dispatcher.utter_message(text="For complete list of your performance, please visit [This link](https://dev-super.apps-madhani.com/time-off/request")
        return []

class ActionGetPresenceThisMonth(Action):
    def name(self) -> str:
        return "action_get_presence_this_month"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        if token_raa is not None :
            value = get_employee_perf_raa(token_raa=token_raa, current_month=True, perf_type="hadir", use_dummy_data=True)
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Total ke{value['legend_name']}an Anda di bulan ini sebanyak **{value['total']}** kali.\n"
                    f"Dengan Presentasi Kehadiran: {value['percentage']}\n"
                )
                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"Your total attendance this month is **{value['total']}** times.\n"
                    f"With Attendance percentage: {value['percentage']}\n"
                )
                dispatcher.utter_message(text=message)
        if language == "indonesia":
            dispatcher.utter_message(text="Untuk list lengkap dari performa Anda, dapat dilihat di [Link ini](https://dev-super.apps-madhani.com/time-off/request)")
        else:
            dispatcher.utter_message(text="For complete list of your performance, please visit [This link](https://dev-super.apps-madhani.com/time-off/request)")
        return []

class ActionGetPresenceLastMonth(Action):
    def name(self) -> str:
        return "action_get_presence_last_month"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        if token_raa is not None :
            value = get_employee_perf_raa(token_raa=token_raa, current_month=False, perf_type="hadir", use_dummy_data=True)
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Total ke{value['legend_name']}an Anda di bulan lalu sebanyak **{value['total']}** kali.\n"
                    f"Dengan Presentasi Kehadiran: {value['percentage']}\n"
                )
                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"Your total attendance last month is **{value['total']}** times.\n"
                    f"With Attendance percentage: {value['percentage']}\n"
                )
                dispatcher.utter_message(text=message)
        if language == "indonesia":
            dispatcher.utter_message(text="Untuk list lengkap dari performa Anda, dapat dilihat di [Link ini](https://dev-super.apps-madhani.com/time-off/request)")
        else:
            dispatcher.utter_message(text="For complete list of your performance, please visit [This link](https://dev-super.apps-madhani.com/time-off/request)")
        return []

class ActionGetProjectSitesMadhani(Action):
    def name(self) -> str:
        return "action_get_project_sites_madhani"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        if token_raa is not None :
            value = get_project_sites_raa(token_raa=token_raa)
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Saat ini jumlah total project site di Madhani sebanyak **{len(value)}**\n"
                    f"Berikut adalah daftar project site di Madhani: "
                    f"{', '.join(value)}"

                )
                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"Currently, the total number of project sites at Madhani is **{len(value)}**\n"
                    f"Here is the list of project sites at Madhani: "
                    f"{', '.join(value)}"

                )
                dispatcher.utter_message(text=message)
        if language == "indonesia":
            dispatcher.utter_message(text="Untuk list lengkap dari projek Madhani, dapat dilihat di [Link ini](https://dev-raa-super.apps-madhani.com/project-configuration)")
        else:
            dispatcher.utter_message(text="For complete list of Madhani Projects, please visit [This link](https://dev-raa-super.apps-madhani.com/project-configuration)")
        return []

class ActionGetUserProfileRole(Action):
    def name(self) -> str:
        return "action_get_user_profile_role"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        if token_raa is not None :
            value = get_user_profile_raa(token_raa=token_raa)
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Anda terdaftar dengan role **{value['role_name']}** di aplikasi ini \n"
                    f"Semoga ini membantu Anda dalam memahami peran Anda! \n"
                )
                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"You are registered with the role **{value['role_name']}** in this application\n"
                    f"Hope this helps you in understanding your role! \n"
                )
                dispatcher.utter_message(text=message)
        if language == "indonesia":
            dispatcher.utter_message(text="Untuk informasi lengkap dari profil Anda, dapat dilihat di [Link ini](https://dev-raa-super.apps-madhani.com/user-detail)")
        else:
            dispatcher.utter_message(text="For complete information of your profiles, please visit [This link](https://dev-raa-super.apps-madhani.com/user-detail)")
        return []

class ActionGetUserProfileDepartment(Action):
    def name(self) -> str:
        return "action_get_user_profile_department"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        if token_raa is not None :
            value = get_user_profile_raa(token_raa=token_raa)
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Saat ini, Anda terdaftar di department **{value['department_name']}**, dan Anda memiliki peran sebagai **{value['role_name']}** di aplikasi ini.\n"
                )
                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"Currently, you are registered in **{value['department_name']}** department, and you have the role as **{value['role_name']}** in this application.\n"
                )
                dispatcher.utter_message(text=message)
        if language == "indonesia":
            dispatcher.utter_message(text="Untuk informasi lengkap dari profil Anda, dapat dilihat di [Link ini](https://dev-raa-super.apps-madhani.com/user-detail)")
        else:
            dispatcher.utter_message(text="For complete information of your profiles, please visit [This link](https://dev-raa-super.apps-madhani.com/user-detail)")
        return []

class ActionGetUserProfilePosition(Action):
    def name(self) -> str:
        return "action_get_user_profile_position"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        if token_raa is not None :
            value = get_user_profile_raa(token_raa=token_raa)
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Posisi Anda yang tercatat di sistem ini adalah **{value['position_name']}**. Semoga ini membantu Anda dalam memahami posisi Anda!"
                )
                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"Your position recorded in this system is **{value['position_name']}**. Hope this helps you in understanding your position!\n"
                )
                dispatcher.utter_message(text=message)
        if language == "indonesia":
            dispatcher.utter_message(text="Untuk informasi lengkap dari profil Anda, dapat dilihat [Link ini](https://dev-raa-super.apps-madhani.com/user-detail)")
        else:
            dispatcher.utter_message(text="For complete information of your profiles, please visit [This link](https://dev-raa-super.apps-madhani.com/user-detail)")
        return []

class ActionGetUserProfileEmail(Action):
    def name(self) -> str:
        return "action_get_user_profile_email"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        if token_raa is not None :
            value = get_user_profile_raa(token_raa=token_raa)
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = "Alamat email yang terdaftar pada akun Anda adalah: \n"
                table_data.append(["Email", f"{value['email']}"])
                table_data.append(["Password", f"{value['password']}"])
                dispatcher.utter_message(text=message)
                doc.add_table(header=["Deskripsi", "Nilai"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())
            else:
                message = "The email address registered to your account is: \n"
                table_data.append(["Email", f"{value['email']}"])
                table_data.append(["Password", f"{value['password']}"])
                dispatcher.utter_message(text=message)
                doc.add_table(header=["Description", "Value"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia":
            dispatcher.utter_message(text="Untuk informasi lengkap dari profil Anda, dapat dilihat di [Link ini](https://dev-raa-super.apps-madhani.com/user-detail)")
        else:
            dispatcher.utter_message(text="For complete information of your profiles, please visit [This link](https://dev-raa-super.apps-madhani.com/user-detail)")
        return []

class ActionGetUserProfileProjectSite(Action):
    def name(self) -> str:
        return "action_get_user_profile_project_site"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        if token_raa is not None :
            value = get_user_profile_raa(token_raa=token_raa)
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Saat ini, Anda ditugaskan di project site **{value['project_name']}**. Semoga informasi ini membantu!"
                )
                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"Currently, you are assigned to the project site **{value['project_name']}**. Hope this information helps!"
                )
                dispatcher.utter_message(text=message)
        if language == "indonesia":
            dispatcher.utter_message(text="Untuk informasi lengkap dari profil Anda, dapat dilihat di [Link ini](https://dev-raa-super.apps-madhani.com/user-detail)")
        else:
            dispatcher.utter_message(text="For complete information of your profiles, please visit [This link](https://dev-raa-super.apps-madhani.com/user-detail)")
        return []

class ActionGetUserProfilePhoneNumber(Action):
    def name(self) -> str:
        return "action_get_user_profile_phone_number"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        if token_raa is not None :
            value = get_user_profile_raa(token_raa=token_raa)
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = ("Nomor telepon yang terdaftar di akun Anda adalah: \n")
                table_data.append(["Nomor HP", f"{value['phone']}"])
                table_data.append(["Nomor WhatsApp", f"{value['nomor_wa']}"])
                dispatcher.utter_message(text=message)
                doc.add_table(header=["Deskripsi", "Nilai"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())
            else:
                message = ("Your registered phone numbers are: \n")
                table_data.append(["Phone Number", f"{value['phone']}"])
                table_data.append(["WhatsApp Number", f"{value['nomor_wa']}"])
                dispatcher.utter_message(text=message)
                doc.add_table(header=["Description", "Value"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())
        if language == "indonesia":
            dispatcher.utter_message(text="Untuk informasi lengkap dari profil Anda, dapat dilihat di [Link ini](https://dev-raa-super.apps-madhani.com/user-detail)")
        else:
            dispatcher.utter_message(text="For complete information of your profiles, please visit [This link](https://dev-raa-super.apps-madhani.com/user-detail)")
        return []

class ActionGetUserProfileHireDate(Action):
    def name(self) -> str:
        return "action_get_user_profile_hire_date"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        if token_raa is not None :
            value = get_user_profile_raa(token_raa=token_raa)
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Anda bergabung dengan PT Madhani Talatah Nusantara pada tanggal {format_datetime(datetime.strptime(value['date_of_hire'], '%Y-%m-%dT%H:%M:%SZ'), format='d MMMM yyyy', locale='id')}"
                )
                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"You joined PT Madhani Talatah Nusantara on {format_datetime(datetime.strptime(value['date_of_hire'], '%Y-%m-%dT%H:%M:%SZ'), format='d MMMM yyyy', locale='en')}"
                )
                dispatcher.utter_message(text=message)
        if language == "indonesia":
            dispatcher.utter_message(text="Untuk informasi lengkap dari profil Anda, dapat dilihat di [Link ini](https://dev-raa-super.apps-madhani.com/user-detail)")
        else:
            dispatcher.utter_message(text="For complete information of your profiles, please visit [This link](https://dev-raa-super.apps-madhani.com/user-detail)")
        return []

class ActionGetPositionsMadhani(Action):
    def name(self) -> str:
        return "action_get_positions_madhani"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        if token_raa is not None :
            value = get_information_all_position_raa(token_raa=token_raa)
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Posisi yang tersedia di Madhani saat ini berjumlah **{len(value)}** \n"
                    f"Berikut adalah beberapa daftar posisi yang ada di Madhani: \n"
                ) 
                for number, line in enumerate(value[:min(len(value),10)]):
                    message += f"{number+1}. {line}\n"
                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"Currently, the number of available positions at Madhani is **{len(value)}**\n"
                    f"Here are some of the available positions at Madhani: \n"
                )
                for number, line in enumerate(value[:min(len(value),10)]):
                    message += f"{number+1}. {line}\n"
                dispatcher.utter_message(text=message)
        if language == "indonesia":
            dispatcher.utter_message(text= "Jika Anda ingin melihat lebih banyak informasi atau daftar lengkap posisi di Madhani, Anda dapat mengunjungi [Link ini](https://dev-raa-super.apps-madhani.com/user-management)")
            
        else:
            dispatcher.utter_message(text="If you would like to see more information or a complete list of positions at Madhani, you can visit [This link](https://dev-raa-super.apps-madhani.com/user-management)")
        return []

class ActionGetTotalPositionsMadhani(Action):
    def name(self) -> str:
        return "action_get_total_positions_madhani"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        if token_raa is not None :
            value = get_information_all_position_raa(token_raa=token_raa)
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Total posisi yang tersedia di Madhani saat ini berjumlah **{len(value)}**\n"
                )
                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"The total positions available at Madhani currently amount to **{len(value)}**\n" 

                )
                dispatcher.utter_message(text=message)
        if language == "indonesia":
            dispatcher.utter_message(text= "Jika Anda ingin melihat lebih banyak informasi tentang posisi-posisi Madhani tersebut, Anda dapat mengunjungi [Link ini](https://dev-raa-super.apps-madhani.com/user-management)")
            
        else:
            dispatcher.utter_message(text="If you would like to see more information about these positions, you can visit [This link](https://dev-raa-super.apps-madhani.com/user-management)")
        return []

class ActionGetDepartmentsMadhani(Action):
    def name(self) -> str:
        return "action_get_departments_madhani"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        if token_raa is not None :
            value = get_information_all_departments_raa(token_raa=token_raa)
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Department yang tersedia di Madhani saat ini berjumlah **{len(value)}**\n"
                    f"Berikut adalah daftar department di Madhani: \n"
                )
                for number, line in enumerate(value):
                    message += f"{number+1}. {line}\n"
                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"Currently, the number of available departments at Madhani is **{len(value)}**\n"
                    f"Here is the list of departments at Madhani: \n"
                )
                for number, line in enumerate(value):
                    message += f"{number+1}. {line}\n"
                dispatcher.utter_message(text=message)
        if language == "indonesia":
            dispatcher.utter_message(text= "Untuk melihat daftar lengkap department Madhani, Anda dapat mengunjungi [Link ini](https://dev-raa-super.apps-madhani.com/user-management)")
            
        else:
            dispatcher.utter_message(text="To view the full list of departments at Madhani, you can visit [This link](https://dev-raa-super.apps-madhani.com/user-management)")
        return []

class ActionGetTotalDepartmentsMadhani(Action):
    def name(self) -> str:
        return "action_get_total_departments_madhani"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_raa = get_raa_token(tracker)
        value = None
        if token_raa is not None :
            value = get_information_all_departments_raa(token_raa=token_raa)
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Total department yang tersedia di Madhani saat ini berjumlah **{len(value)}**\n"
                )

                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"The total departments available at Madhani currently amount to **{len(value)}**\n"
                )
                dispatcher.utter_message(text=message)
        if language == "indonesia":
            dispatcher.utter_message(text= "Jika Anda ingin melihat lebih banyak informasi tentang department Madhani, Anda dapat mengunjungi [Link ini](https://dev-raa-super.apps-madhani.com/user-management)")
            
        else:
            dispatcher.utter_message(text="If you would like to see more information about Madhani's departments, you can visit [This Link](https://dev-raa-super.apps-madhani.com/user-management)")
        return []
    

