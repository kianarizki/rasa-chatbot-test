# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
from actions.schema import MessageSelectOptions,MessageRangePicker,MessageDatePicker,MessageSchema

from typing import Text, Any, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction

import requests
import jwt

from actions import config

from actions.services.ess.actions import *
from actions.services.raa.actions import *
from actions.services.fms.actions import *
from actions.services.mtn001m.actions import *

from actions.services.ess.api import get_profile_ess, get_ess_token, generate_ess_token_by_nik

import snakemd
from snakemd.document import Table

import uuid
import logging
from datetime import datetime, timedelta, date
logger = logging.getLogger(__name__)
logger.info("Starting Action Server")
# in any function

LIST_APP = ("ess","001m","raa","opd")

def getAppName(intent_name):
    apps = intent_name.split("_")
    for i in range (len(apps)-1):
        if apps[i].lower() in LIST_APP:
            return apps[i].lower()
        elif apps[i].lower() == "qhse" or apps[i].lower() == "lms":
            return apps[i].lower() + "_" + apps[i+1].lower()
    return "others"

class ActionSetLanguage(Action):
    def name(self):
        return "action_set_language"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        last_intent = tracker.latest_message['intent'].get('name')
        if last_intent == "ask_language_id":
            dispatcher.utter_message(text="Bahasa diatur ke Indonesia.")
            return [SlotSet("language", "indonesia")]
        elif last_intent == "ask_language_en":
            dispatcher.utter_message(text="Language is set to English.")
            return [SlotSet("language", "english")]
        return []
    
class ActionHandleFallback(Action):
    def name(self) -> str:
        return "action_handle_fallback"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        fallback_count = tracker.get_slot("fallback_count") or 0.0
        fallback_count = float(fallback_count)

        language = tracker.get_slot("language") 

        fallback_responses = {
            "english": [
                "Sorry, I didn't understand your request. Could you please repeat?",
                "That question is beyond the scope of my knowledge. Do you want to be redirected to admin or continue with the bot? Click 'Admin' to be redirected or Click 'Continue' to continue with the bot."
            ],
            "indonesia": [
                "Maaf, saya tidak mengerti permintaan Anda. Bisa diulangi?",
                "Pertanyaan itu di luar jangkauan pengetahuan saya. Apakah Anda ingin dialihkan ke admin atau melanjutkan dengan bot? Klik 'Admin' untuk dialihkan atau Klik 'Lanjut' untuk melanjutkan dengan bot."
            ]
        }
        
        if fallback_count >= 2 and (fallback_count - 2) % 3 == 0:
            if language == "english":
                dispatcher.utter_message(
                    text=fallback_responses["english"][1],
                    buttons=[
                        {"title": "Admin", "payload": "/ask_admin_en"},
                        {"title": "Continue", "payload": "/continue_with_bot_en"},
                    ]
                )
                json_message= {
                    "text": "Choose the next action"
                }

            else:
                dispatcher.utter_message(
                    text=fallback_responses["indonesia"][1],
                    buttons=[
                        {"title": "Admin", "payload": "/ask_admin_id"},
                        {"title": "Lanjut", "payload": "/continue_with_bot_id"}
                    ]
                )
                json_message= {
                    "text": "Pilih kelanjutan proses"
                }

        else:
            if language == "english":
                dispatcher.utter_message(text=fallback_responses["english"][0])
            else:
                dispatcher.utter_message(text=fallback_responses["indonesia"][0])

        return [SlotSet("fallback_count", fallback_count + 1)]

    
class ActionContinueWithBot(Action):
    def name(self) -> str:
        return "action_continue_with_bot"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        if language == "indonesia":
            dispatcher.utter_message(response="utter_offer_response_id")
        else:
            dispatcher.utter_message(response="utter_offer_response_en")
        return []
    
class ActionInformAdminTransfer(Action):
    def name(self) -> str:
        return "action_inform_admin_transfer"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        cs_name = tracker.get_slot("cs_name")

        if cs_name:
            if language == "indonesia":
                dispatcher.utter_message(response="utter_call_operator_scenario_admin_id")
                # dispatcher.utter_message(text=f"Mohon maaf, admin {cs_name} belum dapat merespon. apakah anda ingin melanjutkan chat dengan saya atau ingin saya bantu untuk menghubungkan dengan admin lain?",
                #                          json_message={"available_at":str(datetime.now() + timedelta(minutes=5)) })

            else:
                dispatcher.utter_message(response="utter_call_operator_scenario_admin_en")
                # dispatcher.utter_message(text=f"Apologies, admin {cs_name} is currently unavailable to respond. Would you like to continue chatting with me, or would you prefer I help connect you with another admin?",
                #                          json_message={"available_at":str(datetime.now() + timedelta(minutes=5)) })

        else:
            if language == "indonesia":
                dispatcher.utter_message(text="Tidak ada admin yang tersedia untuk topik aplikasi ini.")
            else:
                dispatcher.utter_message(text="No admin in this topic application suite your needs.")  
        return [SlotSet("cs_name", None), SlotSet("asked_to_transfer_to_admin", None)]       

class ActionTransferToAdmin(Action):
    def name(self) -> str:
        return "action_transfer_to_admin"  
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Request to get the admin (cs_name)
        sender_id = tracker.sender_id
        language = tracker.get_slot("language")

        topic_intent = tracker.get_intent_of_latest_message(False)
        # print("DISPATCHER ",dispatcher.messages)
        logger.info(f"TOPIC INTENT: {topic_intent}")
        topic = getAppName(topic_intent)
        logger.info(f"TOPIC APP: {topic}")
        profile = get_profile_ess(generate_ess_token_by_nik(tracker.sender_id))
         

        if not topic or profile == None: 
            dispatcher.utter_message(text="Terjadi kesalahan pada server / There was an error from server")
            return [SlotSet("asked_to_transfer_to_admin", False)]
        
        user_location = profile.get("project",{}).get("name","N/A")
        user_position = profile.get("position",{}).get("name","N/A")
        user_name = profile.get("name","N/A")
        internal_user_id = profile.get("id",uuid.uuid4())
        avatar_url = profile.get("image_profile","")

        user_message = tracker.get_last_event_for("user",skip=3)
        if user_message:
            user_message = user_message.get("parse_data","").get("text","")

        bot_message = tracker.get_last_event_for("bot",skip=1)
        if bot_message:
            bot_message = bot_message.get("text","")
            
        logger.info(f"USR MESS: {user_message}")
        logger.info(f"BOT MESS: {bot_message}")

        cs_name, queue_number,app_name, admin_nik = self.get_cs_name_queue(sender_id,topic,topic_intent,user_message, bot_message,user_name, user_location, user_position,internal_user_id, avatar_url)
        logger.info(f"App Name : {app_name}")
        logger.info(f"Queue Number {queue_number}")
        if not app_name:
            # dispatcher.utter_message(text="Unable to retrieve the customer service representative's name.")
            return [SlotSet("asked_to_transfer_to_admin", False)]
        
        # dispatcher.utter_message(text=f"Antrian Nomor {queue_number}")
        # return [SlotSet("cs_name", cs_name), SlotSet("asked_to_transfer_to_admin", True)]
        if queue_number and queue_number > 1:
            if language == "english":
                message = (
                    f"Your chat will be transferred to Admin {app_name} on duty. "
                    f"There are currently ({queue_number}) users in the queue before you. "
                    f"Please be patient, Admin {app_name} will assist you shortly."
                )
            else:
                message = (
                    f"Obrolan Anda akan segera dialihkan ke Admin {app_name} yang sedang bertugas. "
                    f"Saat ini ada ({queue_number}) pengguna dalam antrian sebelum Anda. "
                    f"Mohon bersabar, Admin {app_name} akan segera membantu Anda."
                )
        else:
            if language == "english":
                message = (
                    f"Your chat will be transferred to Admin {app_name} on duty. "
                    "Please be patient, Admin will assist you shortly."
                )
            else: 
                message = (
                    f"Obrolan Anda akan segera dialihkan ke Admin {app_name} yang sedang bertugas. "
                    "Mohon bersabar, Admin akan segera membantu Anda. "
                )
        dispatcher.utter_message(text=message)
        
        if language == "english":
            waiting_message = (
                "While waiting, the chat feature in this section will be limited. "
                "If you want to cancel the transfer, use the available option on the CTA button below. Thank you."
            )
        else:
            waiting_message = (
                "Selama menunggu, fitur chat di bagian ini akan dibatasi. "
                "Jika Anda ingin membatalkan pengalihan, gunakan opsi yang tersedia pada tombol CTA di bawah. Terima kasih."
            )
        dispatcher.utter_message(text=waiting_message)  
        
        return [
            SlotSet("app_name", app_name), 
            SlotSet("asked_to_transfer_to_admin", True),
            SlotSet("queue_number", queue_number)
        ]

    def get_cs_name_queue(self, sender_id, topic, topic_intent, user_message, bot_message, user_name, user_location, user_position, internal_user_id, avatar_url) -> List[Any]:
        # Define mapping for app names
        app_name_mapping = {
            "qhse_ass": "QHSE Assessment",
            "qhse_lms": "QHSE LMS",
            "001m": "001M",
            "raa": "RAA", 
            "ess": "ESS",
            "opd": "OPD",
            "others": "Others"
        }
        if topic=="lms_opd":
            topic="opd"

        try:
            # Example POST request to /getAdmin/
            response = requests.post(f"{config.CHAT_BASE_URL}handover", json={
                "app_name": topic,
                "user_id": str(sender_id),
                "user_message": user_message,
                "bot_response": bot_message,
                "bot_intent": topic_intent,
                "user_location": user_location,
                "user_name" : user_name,
                "internal_user_id":str(internal_user_id),
                "user_position":user_position,
                "avatar_url" : avatar_url

            })

            if response.status_code == 200:
                logger.info(f"app_name : {topic}")

                data = response.json()
                logger.info(f"Info data: {data}")

                # Retrieve and map app_name if necessary
                raw_app_name = data.get("data", {}).get("app_name", "")
                app_name = app_name_mapping.get(raw_app_name, raw_app_name.replace("_", " "))
                return [
                    data.get("data", {}).get("admin_name"),
                    data.get("data", {}).get("queue_number"),
                    app_name,
                    data.get("data", {}).get("admin_nik")
                ]
            else:
                logger.error(f"Invalid status code: {response.status_code}")
                return [None, None, None, None]
        
        except requests.exceptions.RequestException as e:
            # Handle any exceptions during the request
            logger.error(f"Error occured while fetching cs_name: {e}")
            return [None, None, None, None]

class ActionCancelHandoverYes(Action):
    def name(self) -> str:
        return "action_cancel_handover_yes"  
    def action_cancel(self,sender_id):
        try:
            # Example POST request to /getAdmin/
            response = requests.get(f"{config.CHAT_BASE_URL}chat/state?type=user&sender_id={sender_id}")

            if response.status_code == 200:
                data = response.json()
                ticket_id = data.get("data", {}).get("status"),
                try : 
                    res_cancel = requests.put(f"{config.CHAT_BASE_URL}handover/cancel",json={
                        "ticket_id": ticket_id,
                    })
                    if res_cancel.status_code == 200:
                        return True
                    else:
                        return False
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error occured while reqs: {e}")
                    return False
            else:
                logger.error(f"Invalid status code: {response.status_code}")
                return False
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error occured while reqs: {e}")
            return False
        
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        sender_id = tracker.sender_id
        language = tracker.get_slot("language")

        if self.action_cancel(sender_id):
            if language == "indonesia":
                dispatcher.utter_message(text="Handover dengan admin telah dibatalkan. Percakapan akan dilanjutkan dengan bot.")

                dispatcher.utter_message(response="utter_greet_id")
            else:
                dispatcher.utter_message(text="Handover has been cancelled. Chat will be continued with the bot")

                dispatcher.utter_message(response="utter_greet_en")
        else:
            if language == "indonesia":
                dispatcher.utter_message(text="Telah terjadi kesalahan dalam handover. Handover akan tetap dilanjutkan")
            else:
                dispatcher.utter_message(text="An error occurred during handover. Handover will continue")
        return 
    
class ActionCancelHandoverNo(Action):
    def name(self) -> str:
        return "action_cancel_handover_no"  
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        if language == "indonesia":
            dispatcher.utter_message(text="Baik handover akan tetap dilanjutkan. Mohon bersabar untuk menunggu admin")
        else:
            dispatcher.utter_message(text="Handover will be continue to be held. Please be patient while waiting for the admin")
        return 
    
class ActionShowDatePicker(Action):
    def name(self) -> str:
        return "action_show_date_picker"  
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        message = MessageSchema("options")

        message_date_picker = MessageDatePicker("ini date picker")
        message.add_date_picker(message_date_picker)

        if language == "indonesia":
            dispatcher.utter_message(text="Ini date picker", json_message=message.to_dict())
        else:
            dispatcher.utter_message(text="This is date picker",json_message=message.to_dict())
        return 
    

class ActionShowRangePicker(Action):
    def name(self) -> str:
        return "action_show_range_picker"  
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        message = MessageSchema("options")

        message_range_picker = MessageRangePicker("ini range picker")
        message.add_date_picker(message_range_picker)
        if language == "indonesia":
            dispatcher.utter_message(text="Ini range picker", json_message=message.to_dict())
        else:
            dispatcher.utter_message(text="This is range picker",json_message=message.to_dict())
        return 
    
class ActionShowSelectOptions(Action):
    def name(self) -> str:
        return "action_show_select_options"  
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        message = MessageSchema("options")

        message_select = MessageSelectOptions("ini select",[{"label":"label 1", "value":"value 1"},{"label":"label 2", "value":"value 2"}])
        message.add_date_picker(message_select)
        # print(message.to_dict())
        if language == "indonesia":
            dispatcher.utter_message(text="Ini select options", json_message=message.to_dict())
        else:
            dispatcher.utter_message(text="This is select options",json_message=message.to_dict())
        return 
    
class ActionShowSelectOptionsWithText(Action):
    def name(self) -> str:
        return "action_show_select_options_with_text"  
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        if language == "indonesia":
            dispatcher.utter_message(text="Ini select options", json_message={"sender_type":"options","type":"select","title":"ini select options", "options":[{"label":"label 1", "value":"value 1","label":"label 2", "value":"value 2"}]})
        else:
            dispatcher.utter_message(text="This is select options",json_message={"sender_type":"options","type":"select","title":"ini select options","options":[{"label":"label 1", "value":"value 1","label":"label 2", "value":"value 2"}]})
        return 

### Get SuperAPP Detail User ###



## NOTE : https://app.diagrams.net/#G1dMBSDDBEd2I9oL_9qEcnJiguVvlyle-_#%7B%22pageId%22%3A%22nKWvoLxFLcw61cbSu53L%22%7D

