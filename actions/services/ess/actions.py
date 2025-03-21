
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
from actions.services.ess import ActionTimeOff
from babel.dates import format_datetime

from actions.schema import MessageSchema,MessageDatePicker,MessageRangePicker, MessageSelectOptions

from actions.services.ess.api import (get_ess_token, get_timeoff_ess, get_timeoff_latest_user_ess, get_approval_leave_off_ess, post_approval_leave_off, get_profile_ess, generate_ess_token_by_nik,
                                     get_level_from_token, fetch_data)

logger = logging.getLogger(__name__)
logger.info("Starting Action ESS Server")

class ActionTimeOffExpired(Action):
    def name(self) -> str:
        return "action_time_off_expired"  
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        leave_type = tracker.get_slot("leave_type")
        logger.info(f"Leave type condition : {leave_type}" )
        language = tracker.get_slot("language")
        if leave_type == "annual" or leave_type == "tahunan":
            return [FollowupAction("action_time_off_expired_annual")]
        elif leave_type == "big" or leave_type == "besar":
            return [FollowupAction("action_time_off_expired_big")]
        elif leave_type == "outstanding":
            return [FollowupAction("action_time_off_expired_outstanding")]

        if language == "indonesia":
            return dispatcher.utter_message(text="Tidak bisa memroses pesan") 

        return dispatcher.utter_message(text="Cannot proceed your message")

class ActionTimeOffExpiredAnnual(Action):
    def name(self) -> str:
        return "action_time_off_expired_annual"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_ess = get_ess_token(tracker)

        if token_ess is not None:
            value = get_timeoff_ess(token_ess, "annual")
            if value:
                message = ""
                for k in value:
                    if value[k]['quota_type'] == "yearly_quotas":
                        message += (f"Sisa kuota Cuti Tahunan Anda adalah **{value[k]['quota']}**, Expired: {format_datetime(datetime.strptime(value[k]['expired'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='id' if language == 'indonesia' else 'en')}")
                        message += "\n"
                if not message:
                    message = "Berdasarkan data, Anda tidak memiliki jatah cuti."
                dispatcher.utter_message(text=message)
                dispatcher.utter_message(text="Untuk selengkapnya, dapat dilihat di [Link ini](https://dev-super.apps-madhani.com/time-off/request)" if language == "indonesia" else "For further information, please visit [This Link](https://dev-super.apps-madhani.com/time-off/request)")
            else:
                dispatcher.utter_message(text="Berdasarkan data, Anda tidak memiliki jatah cuti." if language == "indonesia" else "Based on the data, you do not have any remaining Big Leave quota.")
        else:
            dispatcher.utter_message(text="Terjadi kesalahan pada pengambilan absensi" if language == "indonesia" else "There was an error while processing the request")
        return []
    
class ActionTimeOffExpiredBig(Action):
    def name(self) -> str:
        return "action_time_off_expired_big"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_ess = get_ess_token(tracker)

        if token_ess is not None:
            value = get_timeoff_ess(token_ess, "big")
            if value:
                message = ""
                for k in value:
                    if value[k]['quota_type'] == "big_quotas":
                        message += (f"Sisa kuota Cuti Besar Anda adalah **{value[k]['quota']}**, Expired: {format_datetime(datetime.strptime(value[k]['expired'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='id' if language == 'indonesia' else 'en')}")
                        message += "\n"
                if not message:
                    message = "Berdasarkan data, Anda tidak memiliki jatah cuti."
                dispatcher.utter_message(text=message)
                dispatcher.utter_message(text="Untuk selengkapnya, dapat dilihat di [Link ini](https://dev-super.apps-madhani.com/time-off/request)" if language == "indonesia" else "For further information, please visit [This Link](https://dev-super.apps-madhani.com/time-off/request)")

            else:
                dispatcher.utter_message(text="Berdasarkan data, Anda tidak memiliki jatah cuti." if language == "indonesia" else "Based on the data, you do not have any remaining Big Leave quota.")
        else:
            dispatcher.utter_message(text="Terjadi kesalahan pada pengambilan absensi" if language == "indonesia" else "There was an error while processing the request")
        return []

class ActionTimeOffExpiredOutstanding(Action):
    def name(self) -> str:
        return "action_time_off_expired_outstanding"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_ess = get_ess_token(tracker)

        if token_ess is not None:
            value = get_timeoff_ess(token_ess, "outstanding")
            if value:
                message = ""
                for k in value:
                    if value[k]['quota_type'] == "outstanding_quotas":
                        message += (f"Sisa kuota Cuti Outstanding Anda adalah **{value[k]['quota']}**, Expired: {format_datetime(datetime.strptime(value[k]['expired'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='id' if language == 'indonesia' else 'en')}")
                        message += "\n"
                if not message:
                    message = "Berdasarkan data, Anda tidak memiliki jatah cuti."
                dispatcher.utter_message(text=message)
                dispatcher.utter_message(text="Untuk selengkapnya, dapat dilihat di [Link ini](https://dev-super.apps-madhani.com/time-off/request)" if language == "indonesia" else "For further information, please visit [This Link](https://dev-super.apps-madhani.com/time-off/request)")

            else:
                dispatcher.utter_message(text="Berdasarkan data, Anda tidak memiliki jatah cuti." if language == "indonesia" else "Based on the data, you do not have any remaining Big Leave quota.")
        else:
            dispatcher.utter_message(text="Terjadi kesalahan pada pengambilan absensi" if language == "indonesia" else "There was an error while processing the request")
        return []
    
class ActionTimeOffRemaining(Action):
    def name(self) -> str:
        return "action_time_off_remaining"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_ess = get_ess_token(tracker)

        quota_type_mapping = {
            "indonesia": {
                "yearly_quotas": "Cuti Tahunan",
                "big_quotas": "Cuti Besar",
                "outstanding_quotas": "Cuti Outstanding",
                "subtitute_quotas": "Cuti Pengganti Hari"
            },
            "english":{
                "yearly_quotas": "Annual Leave",
                "big_quotas": "Big Leave",
                "outstanding_quotas": "Outstanding Leave",
                "subtitute_quotas" : "Substitute Day Leave"
            }
        }

        if token_ess is not None:
            value = get_timeoff_ess(token_ess,"outstanding")
            if value is not None:
                    doc = snakemd.Document()
                    table_data = []
                    if language == "indonesia":
                        message = "Berikut sisa kuota cuti anda:\n"
                        for k in value:
                            quota_type = value[k]['quota_type']
                            translated_quota_type = quota_type_mapping.get(language, {}).get(quota_type, quota_type)
                            table_data.append([f"{translated_quota_type}", f"{value[k]['quota']}", f"{format_datetime(datetime.strptime(value[k]['expired'], '%Y-%m-%dT%H:%M:%SZ'), format='d MMMM yyyy', locale='id')}"])
                        dispatcher.utter_message(text = message)
                        doc.add_table(header=["Tipe", "Quota", "Expired"], data= table_data)
                        dispatcher.utter_message(text=doc.__str__())

                    else:
                        message = "Here is your remaining leave quota\n"
                        for k in value:
                            quota_type = value[k]['quota_type']
                            translated_quota_type = quota_type_mapping.get(language, {}).get(quota_type, quota_type)
                            table_data.append([f"{translated_quota_type}", f"{value[k]['quota']}", f"{format_datetime(datetime.strptime(value[k]['expired'], '%Y-%m-%dT%H:%M:%SZ'), format='d MMMM yyyy', locale='en')}"])
                        dispatcher.utter_message(text = message)
                        doc.add_table(header=["Type", "Quota", "Expired"], data= table_data)
                        dispatcher.utter_message(text=doc.__str__())

                    if language == "indonesia":
                        dispatcher.utter_message(text = "Untuk selengkapnya, dapat dilihat di [Link ini](https://dev-super.apps-madhani.com/time-off/request)")
                    else:
                        dispatcher.utter_message(text = "For further information, please visit [This link](https://dev-super.apps-madhani.com/time-off/request)")
            else:
                if language == "indonesia":
                    dispatcher.utter_message(text="Terjadi kesalahan pada pengambilan absensi")
                else:
                    dispatcher.utter_message(response="There was an error while processing the request")
        else:
            if language == "indonesia":
                dispatcher.utter_message(text="Terjadi kesalahan pada pengambilan absensi")
            else:
                dispatcher.utter_message(response="There was an error while processing the request")
        return []

class ActionTimeOffList(Action):
    def name(self) -> str:
        return "action_time_off_list"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        if language == "indonesia":
            dispatcher.utter_message(text="Untuk list lengkap dari cuti Anda, dapat dilihat di [Link ini](https://dev-super.apps-madhani.com/time-off/request)")
        else:
            dispatcher.utter_message(text="For complete list of your time off requests, please visit [This Link](https://dev-super.apps-madhani.com/time-off/request)")
        return []

class ActionLastApprovalTimeOffStatus(Action):
    def name(self) -> str:
        return "action_last_approval_time_off_status"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_ess = get_ess_token(tracker)
        value = get_timeoff_latest_user_ess(token_ess=token_ess,status_type="")
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = f"Cuti terbaru/terakhir yang Anda ajukan adalah **{value['time_off_type']}**.\nBerikut detail status:\n"
                table_data.append(["Tanggal Pengajuan", f"{value['created_at']}"])
                table_data.append(["Status", f"{value['status']}"])
                table_data.append(["Tanggal Cuti / Ijin", f"{format_datetime(datetime.strptime(value['request_date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='id')}"])
                dispatcher.utter_message(text=message)
                doc.add_table(header=["Deskripsi", "Nilai"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = f"The latest/last leave you applied for is **{value['time_off_type']}**.\nHere are the status details:\n"
                table_data.append(["Submission Date", f"{value['created_at']}"])
                table_data.append(["Status", f"{value['status']}"])
                table_data.append(["Leave / Permission Date", f"{format_datetime(datetime.strptime(value['request_date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='en')}"])
                dispatcher.utter_message(text=message)
                doc.add_table(header=["Description", "Value"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia":
            dispatcher.utter_message(text="Untuk list lengkap dari cuti Anda, dapat dilihat di [Link ini](https://dev-super.apps-madhani.com/time-off/request)")
        else:
            dispatcher.utter_message(text="For complete list of your time off requests, please visit [This Link](https://dev-super.apps-madhani.com/time-off/request)")
        return []
    
class ActionGetLastTimeOff(Action):
    def name(self) -> str:
        return "action_get_last_approval_time_off"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_ess = get_ess_token(tracker)
        value = None
        if token_ess is not None :
            value = get_timeoff_latest_user_ess(token_ess=token_ess,status_type="")
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = f"Cuti terakhir yang anda ajukan adalah pada tanggal {format_datetime(datetime.strptime(value['request_date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='id')}.\nBerikut detail status:\n"
                table_data.append(["Jenis Cuti", f"{value['time_off_type']}"])
                table_data.append(["Status", f"{value['status']}"])                
                dispatcher.utter_message(text=message)
                doc.add_table(header=["Deskripsi", "Nilai"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())
            else:
                message = f"The last leave you requested was on {format_datetime(datetime.strptime(value['request_date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='en')}.\nHere are the status details:\n"
                table_data.append(["Leave Type", f"{value['time_off_type']}"])
                table_data.append(["Status", f"{value['status']}"])                
                dispatcher.utter_message(text=message)
                doc.add_table(header=["Description", "Value"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia":
            dispatcher.utter_message(text="Untuk list lengkap dari cuti Anda, dapat dilihat di [Link ini](https://dev-super.apps-madhani.com/time-off/request)")
        else:
            dispatcher.utter_message(text="For complete list of your time off requests, please visit [This link](https://dev-super.apps-madhani.com/time-off/request)")
        return []

class ActionESSLeaveConfirmation(Action):
    def name(self) -> str:
        return "action_ess_leave_confirmation"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_ess = get_ess_token(tracker)
        leave_req_type = tracker.get_slot("leave_req_type")
        leave_req_date_from = tracker.get_slot("leave_req_date_from")
        leave_req_date_until = tracker.get_slot("leave_req_date_until")
        leave_req_reason = tracker.get_slot("leave_req_reason")
        approver_nik = tracker.get_slot("approver_nik")
        list_approver = approver_nik.split(" ")

        value = None
        if token_ess is not None :
            value = get_approval_leave_off_ess(token_ess=token_ess)

        message = ""
        if language == "indonesia":
            message = (
                f"Ini adalah rincian cuti yang akan Anda ajukan: \n"
                f" - Jenis Cuti: {leave_req_type} \n"
                f" - Tanggal Cuti: {leave_req_date_from} - {leave_req_date_until}\n"
                f" - Alasan Cuti/Ijin: {leave_req_reason}\n"
                f" - Tangal Pengajuan: {date.today().strftime('%d/%m/%Y')}\n"

            )
            dispatcher.utter_message(text=message)
            if value != None:
                message = f"Berikut daftar Approver yang dipilih: \n"
                for level in value['data']:
                    message += (
                        f"No. {level['sequence']}\n"
                        f"Level Jabatan: {level['level_name']}\n"
                    )
                    for approver in level['designated_person']:
                        if approver['nik'] in list_approver:
                            message += (
                                f" - NIK: {approver['nik']}, Nama: {approver['name']}\n"
                        )
                dispatcher.utter_message(text=message)
                
        else:
            message = (
                f"These are the details of the leave you will apply for: \n"
                f" - Leave Type: {leave_req_type}\n"
                f" - Leave Date: {leave_req_date_from} - {leave_req_date_until}\n"
                f" - Reason for Leave/Permission: {leave_req_reason}\n"
                f" - Submission Date: {date.today().strftime('%d/%m/%Y')}\n"
            )
            
            dispatcher.utter_message(text=message)
            if value != None:
                message = f"Below is the list of chosen Approvers: \n"
                for level in value['data']:
                    message += (
                        f"No. {level['sequence']}\n"
                        f"Position Level: {level['level_name']}\n"
                    )
                    for approver in level['designated_person']:
                        if approver['nik'] in list_approver:
                            message += (
                                f" - NIK: {approver['nik']}, Name: {approver['name']}\n"
                        )
                dispatcher.utter_message(text=message)
        return []

class ActionESSPostLeaveTimeOff(Action):
    def name(self) -> str:
        return "action_ess_post_leave_timeoff"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_ess = get_ess_token(tracker)
        leave_req_type = tracker.get_slot("leave_req_type")
        leave_req_date_from = tracker.get_slot("leave_req_date_from")
        leave_req_date_until = tracker.get_slot("leave_req_date_until")
        leave_req_reason = tracker.get_slot("leave_req_reason")
        approver_nik = tracker.get_slot("approver_nik")

        value = {
                "success": False,
                "message_en": f"Failed to submit leave request",
                "message_id": f"Gagal mengirim permintaan cuti"
            }  
        if token_ess is not None :
            value = post_approval_leave_off(token_ess, leave_req_type,leave_req_date_from, leave_req_date_until, leave_req_reason, approver_nik)

        if language == "indonesia":
            message = (
                f"{value['message_id']} \n"
            )
            dispatcher.utter_message(text=message)
     
        else:
            message = (
                f"{value['message_en']} \n"
            )
            dispatcher.utter_message(text=message)
        return [SlotSet('leave_req_type',None),SlotSet('leave_req_reason',None), SlotSet('leave_req_date_until',None),SlotSet('leave_req_date_from',None), SlotSet('approver_nik',None)]

class AskLeaveReqType(Action):
    def name(self):
        return "action_ask_leave_req_type"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_ess = get_ess_token(tracker)

        quota_type_mapping = {
            "indonesia": {
                "yearly_quotas": "Cuti Tahunan",
                "big_quotas": "Cuti Besar",
                "outstanding_quotas": "Cuti Outstanding",
                "subtitute_quotas": "Cuti Pengganti Hari"

            },
            "english":{
                "yearly_quotas": "Annual Leave",
                "big_quotas": "Big Leave",
                "outstanding_quotas": "Outstanding Leave",
                "subtitute_quotas": "Substitute Day Leave"
            }
        }
        if token_ess:
            value = get_timeoff_ess(token_ess, "all")  
            logger.info(f"Quota data received: {value}")
            
            if value:
                custom_message = MessageSchema("options")
                selections = MessageSelectOptions("Pilih Jenis Cuti / Select Timeoff Type")
                options = []
                if language == "indonesia":
                    message = (
                        "Jenis cuti apa yang ingin Anda ajukan?\n"
                        "Berikut jenis cuti Anda yang tersedia:\n"
                    )
                    for k in value:
                        quota_type = value[k]['quota_type']
                        translated_quota_type = quota_type_mapping.get(language, {}).get(quota_type, quota_type)
                        message += f"- Tipe: {translated_quota_type}, Kuota Tersisa: {value[k]['quota']}\n"
                        options.append({
                            "label": f"Tipe: {translated_quota_type}, Kuota Tersisa: {value[k]['quota']}",
                            "value": translated_quota_type.lower(),
                        })
                    message += "\nContoh pengisian: Cuti Tahunan, Cuti Sakit, Cuti Besar.\nSilakan ketik salah satu jenis cuti yang tersedia di atas sesuai dengan kuota yang masih tersisa"
                else:
                    message = (
                        "What type of leave do you want to apply for?\n"
                        "Here are your available leave types:\n"
                    )
                    for k in value:
                        quota_type = value[k]['quota_type']
                        translated_quota_type = quota_type_mapping.get(language, {}).get(quota_type, quota_type)
                        message += f"- Type: {translated_quota_type}, Remaining Quota: {value[k]['quota']}\n"
                        options.append({
                            "label": f"Tipe: {translated_quota_type}, Kuota Tersisa: {value[k]['quota']}",
                            "value": quota_type_mapping['indonesia'].get(quota_type, ""),
                        })
                    message += "\nExample of filling: Annual Leave, Sick Leave, Big Leave.\nPlease type one of the available leave types above according to the remaining quota"
                selections.options = options
                custom_message.add_select(selections)
                dispatcher.utter_message(text=message,json_message=custom_message.to_dict())
            else:
                if language == "indonesia":
                    dispatcher.utter_message(
                        text="Maaf, kami tidak dapat mengambil informasi kuota cuti Anda saat ini"
                    )
                else:
                    dispatcher.utter_message(
                        text="Sorry, we are unable to retrieve your leave quota information at the moment"
                    )
        else:
            if language == "indonesia":
                dispatcher.utter_message(text="Terjadi kesalahan saat memproses permintaan")
            else:
                dispatcher.utter_message(text="There was an error while processing the request")
        return []

class AskLeaveReqReason(Action):
    def name(self):
        return "action_ask_leave_req_reason"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "Masukan alasan Anda mengajukan cuti atau ijin?")
        else:
            dispatcher.utter_message(text = "Please state the reason for your leave or permission application?")
        return []

class AskLeaveReqDateFrom(Action):
    def name(self):
        return "action_ask_leave_req_date_from"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        message = MessageSchema("options").add_date_picker(MessageDatePicker("Pilih tanggal / Choose Date"))

        if language == "indonesia":
            dispatcher.utter_message(text = "Kapan tanggal cuti yang ingin diajukan? Harap masukkan dalam format YYYY-MM-DD, contohnya: 2024-12-01",json_message=message.to_dict())
        else:
            dispatcher.utter_message(text = "When is the leave date you want to apply for? Please enter in YYYY-MM-DD format, for example: 2024-12-01",json_message=message.to_dict())
        return []
    
class AskLeaveReqDateUntil(Action):
    def name(self):
        return "action_ask_leave_req_date_until"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        message = MessageSchema("options").add_date_picker(MessageDatePicker("Pilih tanggal / Choose Date"))

        if language == "indonesia":
            dispatcher.utter_message(text = "Hingga kapan tanggal cuti yang ingin diajukan? Harap masukkan dalam format YYYY-MM-DD, contohnya: 2024-12-01",json_message=message.to_dict())
        else:
            dispatcher.utter_message(text = "Until what date do you want to apply for leave? Please enter in YYYY-MM-DD format, for example: 2024-12-01",json_message=message.to_dict())
        return []

class AskApproverNIK(Action):
    def name(self):
        return "action_ask_approver_nik"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_ess = get_ess_token(tracker)
        value = get_approval_leave_off_ess(token_ess=token_ess)
        custom_message = MessageSchema("options")
        
        if language == "indonesia":
            message = f"Berikut adalah Approver yang tersedia untuk dipilih:\n"
            
            for level in value['data']:
                message += (
                    f"No. {level['sequence']}\n"
                    f"Level Jabatan: {level['level_name']}\n"
                )
                selections = MessageSelectOptions(f"Pilih NIK dari Level: {level['level_name']}")
                options= []
                
                for approver in level['designated_person']:
                    message += (
                        f" - NIK: {approver['nik']}, Nama: {approver['name']}\n"
                    )
                    options.append({
                        "label": f" NIK: {approver['nik']}, Nama: {approver['name']}",
                        "value": approver['nik']
                    })
                selections.options = options
                custom_message.add_select_option(selections)

            dispatcher.utter_message(text=message)
            dispatcher.utter_message(text = "Silakan masukkan NIK approver Anda untuk melanjutkan, pisahkan dengan spasi (contoh: 1010 ADMIN01 ADMIN02)", json_message=custom_message.to_dict())
        
        else:
            message = f"Here are the Approver available to choose from: \n"
            for level in value['data']:
                message += (
                    f"No. {level['sequence']}\n"
                    f"Position Level: {level['level_name']}\n"
                )
                for approver in level['designated_person']:
                    message += (
                        f" - NIK: {approver['nik']}, Name: {approver['name']}\n"
                    )
            dispatcher.utter_message(text=message)
            dispatcher.utter_message(text = "Please enter your approver's NIK to continue, separated by a space (example: 1010 ADMIN01 ADMIN02)")
        return []

class ActionESSGetLeaveByNIK(Action):
    def name(self) -> str:
        return "action_ess_get_leave_by_nik"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_ess = get_ess_token(tracker)
        nik = tracker.get_slot("input_nik_subordinate")
        quota_type_mapping = {
            "indonesia": {
                "yearly_quotas": "Cuti Tahunan",
                "big_quotas": "Cuti Besar",
                "outstanding_quotas": "Cuti Outstanding",
                "subtitute_quotas": "Cuti Pengganti Hari"
            },
            "english":{
                "yearly_quotas": "Annual Leave",
                "big_quotas": "Big Leave",
                "outstanding_quotas": "Outstanding Leave",
                "subtitute_quotas": "Substitute Day Leave"
            }
        }
        try:
            token_nik = generate_ess_token_by_nik(nik)
            profile = get_profile_ess(token_nik)
            logger.info(f"Profile {profile}")
            all_levels = fetch_data('SELECT id, name, sequence FROM levels')
            logger.info(f"All levels : {all_levels}")
            all_levels = [
                {'id': 1, 'name': 'Non Staff', 'sequence': 8},
                {'id': 2, 'name': 'Foreman', 'sequence': 6},
                {'id': 3, 'name': 'Supervisor', 'sequence': 5},
                {'id': 4, 'name': 'Superintendent', 'sequence': 4},
                {'id': 5, 'name': 'Manager', 'sequence': 1},
                {'id': 6, 'name': 'Function Manager', 'sequence': 2},
                {'id': 7, 'name': 'BOD', 'sequence': 3},
                {'id': 8, 'name': 'Staff', 'sequence': 7}
            ]

            requester_sequence = all_levels[profile['level']['id'] -1 ]['sequence']
            logger.info(f"Requester Sequence : {requester_sequence}")
            # logger.info(f"User Sequence : {get_level_from_token(token_ess)}")

            user_sequence = all_levels[get_level_from_token(token_ess) -1]['sequence']
            # logger.info(f"Requester Sequence : {requester_sequence}")
            logger.info(f"User Sequence : {user_sequence}")

            if user_sequence > requester_sequence:
                value = get_timeoff_ess(token_nik,"user_sequence")
                doc = snakemd.Document()
                table_data = []
                if language == "indonesia":
                    message = (f"Berikut sisa kuota cuti bawahan Anda dengan NIK **{nik}**\n"
                    )
                    for k in value:
                        quota_type = value[k]['quota_type']
                        translated_quota_type = quota_type_mapping.get(language, {}).get(quota_type, quota_type)
                        table_data.append([f"{translated_quota_type}", f"{value[k]['quota']}", f"{format_datetime(datetime.strptime(value[k]['expired'], '%Y-%m-%dT%H:%M:%S.%fZ'),'EEEE, d MMMM yyyy', locale='id')}"])
                        message += "\n"
                    dispatcher.utter_message(message)
                    doc.add_table(header=["Jenis Cuci / Ijin","Kuota","Expired"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())
                    return [SlotSet('input_nik_subordinate', None)]

                else:
                    message = (f"The following is your subordinate's remaining leave quota with NIK **{nik}**\n"
                    ) 
                    for k in value:
                        quota_type = value[k]['quota_type']
                        translated_quota_type = quota_type_mapping.get(language, {}).get(quota_type, quota_type)
                        table_data.append([f"{translated_quota_type}", f"{value[k]['quota']}", f"{format_datetime(datetime.strptime(value[k]['expired'], '%Y-%m-%dT%H:%M:%S.%fZ'),'EEEE, d MMMM yyyy', locale='en')}"])
                        message += "\n"
                    dispatcher.utter_message(message)
                    doc.add_table(header=["Leave Type","Quota","Expired"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())
                    return [SlotSet('input_nik_subordinate', None)]
            
            else:
                if language == 'indonesia':
                    message = "Anda tidak memiliki hak akses untuk melihat cuti dengan NIK tersebut"
                else:
                    message = "You do not have access to view leave with this NIK"
                
                dispatcher.utter_message(message)
                return [SlotSet('input_nik_subordinate', None)]
                        
        except Exception as e:
            logger.error(f"Error to execute ActionESSGetLeaveByNIK : {e}")
            if language == 'indonesia':
                message = "Terdapat kesalahan dari server"
            else:
                message = "There was an error from server"
            
            dispatcher.utter_message(message)
            return [SlotSet('input_nik_subordinate', None)]
            
class AskInputNIKSubordinate(Action):
    def name(self):
        return "action_ask_input_nik_subordinate"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "Silakan masukkan NIK bawahan Anda untuk melanjutkan")
        else:
            dispatcher.utter_message(text = "Please enter your subordinate's NIK to continue")
        return []
    
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import re
class ValidateGetLeaveRequestForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_get_leave_request_form"

    def validate_leave_req_date_from(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate date from."""
        
        # Regular expression to match "YYYY-MM-DD"
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        
        # Check if the date matches the pattern and if it's a valid date
        if isinstance(slot_value, str) and re.match(date_pattern, slot_value):
            try:
                # Try parsing the date to make sure it's valid
                datetime.strptime(slot_value, "%Y-%m-%d")
                return {"leave_req_date_from": slot_value}
            except ValueError:
                # If the date is invalid (e.g., 2025-02-30), return None
                dispatcher.utter_message(text = "Invalid date/ Tanggal invalid")
                
                return {"leave_req_date_from": None}
        else:
            # If it doesn't match the format or isn't a string, return None
            dispatcher.utter_message(text = "Invalid date/ Tanggal invalid")

            return {"leave_req_date_from": None}
    
    def validate_leave_req_date_until(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate date until."""
        
        # Regular expression to match "YYYY-MM-DD"
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        
        # Check if the date matches the pattern and if it's a valid date
        if isinstance(slot_value, str) and re.match(date_pattern, slot_value):
            try:
                # Try parsing the date to make sure it's valid
                datetime.strptime(slot_value, "%Y-%m-%d")
                return {"leave_req_date_until": slot_value}
            except ValueError:
                # If the date is invalid (e.g., 2025-02-30), return None
                dispatcher.utter_message(text = "Invalid date/ Tanggal invalid")

                return {"leave_req_date_until": None}
        else:
            # If it doesn't match the format or isn't a string, return None
            dispatcher.utter_message(text = "Invalid date/ Tanggal invalid")

            return {"leave_req_date_until": None}
        #leave_req_type

    def validate_leave_req_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate date until."""
        
        # Check if the date matches the pattern and if it's a valid date
        if slot_value in ["cuti besar", "cuti tahunan", "cuti pengganti hari", "besar", "tahunan", "pengganti hari", "annual leave", "substitute leave", "big leave", "annual", "substitute", "big"]:
            return {"leave_req_type": slot_value} 
        else:
            # If it doesn't match the format or isn't a string, return None
            dispatcher.utter_message(text = "Invalid leave type/ Tipe cuti invalid")

            return {"leave_req_type": None}
        #leave_req_type
    def validate_approver_nik(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
        ) -> Dict[Text, Any]:
            """Validate approver nik."""
            return {"approver_nik": slot_value}
    
    def validate_leave_req_reason(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
        ) -> Dict[Text, Any]:
            """Validate leave req reason."""
            return {"leave_req_reason": slot_value}
    