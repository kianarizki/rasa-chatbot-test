from typing import Text, Any, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction
from rasa_sdk.events import ReminderScheduled
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.interfaces import Tracker
import locale
import requests
import jwt
import datetime
import snakemd
import matplotlib.pyplot as plt
import io
import base64
import numpy as np

from actions.schema import MessageSelectOptions,MessageSchema,MessageRangePicker,MessageDatePicker

from babel.dates import format_datetime

import logging
logger = logging.getLogger(__name__)

logger.info("Starting Action FMS Server")

from datetime import datetime, timedelta, date, timezone

from actions.services.fms import ActionGetFMSProductionByDateShift, ActionGetFMSProductionCoalByDateShift, ActionGetFMSProductionToday, ActionGetFMSProductionWasteByDateShift, ActionKPIOperator
from actions.services.fms.api  import get_all_equipments_fms, get_fms_token, get_all_equipments_categoires_fms, get_all_work_orders_fms, get_all_fleet_setting_fms, get_all_work_area_by_site_fms, get_equipment_breakdown_fms


class ActionGetEquipmentCountFMS(Action):
    def name(self) -> str:
        return "action_get_fms_equipment_count"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        value = None
        if token_fms is not None :
            value = get_all_equipments_fms(token_fms,"total","")
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Terkait data yang tersedia saat ini, PT Madhani Talatah Nusantara tercatat memiliki total **{value['total_equipments']}** unit\n"
                )
                if value['total_equipments'] == 0:
                    message = "Saat ini tidak ada data unit yang ditemukan."

                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"Regarding currently available data, PT Madhani Talatah Nusantara is recorded as having a total **{value['total_equipments']}** units\n"
                )
                if value['total_equipments'] == 0:
                    message = "No unit data found at this time."

                dispatcher.utter_message(text=message)
        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data unit.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing unit data.")
        return []

class ActionCheckUnitByTypeFMS(Action):
    def name(self) -> str:
        return "action_get_fms_check_unit_by_type"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        equipment_type_name = tracker.get_slot("equipment_type_name")
        site_name = tracker.get_slot("site_name")
        logger.info(f"Language: {language}")
        logger.info(f"Equipment type: {equipment_type_name}, Site Name: {site_name}")

        value = None
        if token_fms is not None :
            if site_name is not None:
                value = get_all_equipments_fms(token_fms,"equipment_site", [equipment_type_name, site_name])
            else:
                value = get_all_equipments_fms(token_fms,"equipment", equipment_type_name)
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Ya, unit dengan tipe {equipment_type_name} tersedia di site {site_name if site_name!=None else ''}. \nBerikut adalah daftar unit yang tersedia dengan tipe tersebut di site {site_name if site_name!=None else ''}: \n"
                )
                for i in range(len(value['units'])):
                    table_data.append([f"{i+1}", f"{value['units'][i]['unit_name']}"])

                if value['total_equipments'] == 0 and site_name != None:
                    message = f"Maaf, tidak ditemukan unit dengan tipe {equipment_type_name} di site {site_name}."
                elif value['total_equipments'] == 0 :
                    message += f"Saya tidak mengenali tipe unit {equipment_type_name}. Pastikan tipe unit yang Anda masukkan sudah benar"

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Kode Unit"], data= table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"Yes, there is a unit of type {equipment_type_name} at site {site_name if site_name!=None else ''}. \nThe following is a list of available units of that type at site {site_name if site_name!=None else ''}: \n"
                )
                for i in range(len(value['units'])):
                    table_data.append([f"{i+1}", f"{value['units'][i]['unit_name']}"])

                if value['total_equipments'] == 0 and site_name != None:
                    message = f"Sorry, no units with type {equipment_type_name} were found on site {site_name}."
                elif value['total_equipments'] == 0 :
                    message += f"I do not recognize the unit type {equipment_type_name}. Make sure the unit type you entered is correct"

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Unit Code"], data= table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data unit.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing unit data.")
        
        return [SlotSet("equipment_type_name", None), SlotSet("site_name", None)]

class ActionAskEquipmentTypeName(Action):
    def name(self):
        return "action_ask_equipment_type_name"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "Tolong sebutkan tipe unit yang Anda cari, contohnya: Excavator, Rigid Dump Truck atau Truck Coal")
        else:
            dispatcher.utter_message(text = "Please state the type of unit you are looking for, for example: Excavator, Rigid Dump Truck or Truck Coal")
        return []
    
class ActionAskSiteName(Action):
    def name(self):
        return "action_ask_site_name"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "Di lokasi site mana Anda ingin mencari informasi ini? Mohon sebutkan nama atau ID site, contohnya: 001A, 001D atau 001M")
        else:
            dispatcher.utter_message(text = "At which site location do you want to find this information? Please state the name or site ID, for example: 001A, 001D or 001M")
        return []

class ActionGetTypeOfUnitFMS(Action):
    def name(self) -> str:
        return "action_get_fms_type_of_unit"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        unit_code = tracker.get_slot("unit_code")
        logger.info(f"Language: {language}")
        logger.info(f"Unit Code: {unit_code}")
        
        value = None
        if token_fms is not None :
            value = get_all_equipments_fms(token_fms,"search", unit_code)
        logger.info(f"API Response: {value}")

        if value is not None:
            if language == "indonesia":
                message = (
                    f"Maaf, saya tidak menemukan informasi untuk unit dengan kode {unit_code}.\n"
                )
           
                if len(value['units']) != 0 :
                    message = f"Unit dengan kode **{unit_code}** adalah tipe **{value['units'][0]['equipment_type']}**"
                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"Sorry, I couldn't find information for the unit with code {unit_code}.\n"
                )
           
                if len(value['units']) != 0 :
                    message = f"The unit with code **{unit_code}** is type **{value['units'][0]['equipment_type']}**"

                dispatcher.utter_message(text=message)
        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data unit.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing unit data.")
        return [SlotSet("unit_code", None)]

class ActionGetFMSUnitPurchaseDate(Action):
    def name(self) -> str:
        return "action_get_fms_unit_purchase_date"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        unit_code = tracker.get_slot("unit_code")
        logger.info(f"Language: {language}")
        logger.info(f"Unit Code: {unit_code}")        
        value = None
        if token_fms is not None :
            value = get_all_equipments_fms(token_fms,"search", unit_code)
        logger.info(f"API Response: {value}")

        if value is not None:
            if language == "indonesia":
                message = (
                    f"Maaf, saya tidak menemukan data pembelian untuk unit {unit_code}\n"
                )
           
                if len(value['units']) != 0 :
                    message = f"Unit **{unit_code}** dibeli pada tahun {value['units'][0]['purchase_date'].year}, tepatnya pada tanggal {format_datetime(value['units'][0]['purchase_date'], 'EEEE, d MMMM yyyy', locale='id')}"
                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"Sorry, I couldn't find purchase information for the unit with code {unit_code}.\n"
                )
           
                if len(value['units']) != 0 :
                    message = f"The unit with code **{unit_code}** is bought at  {value['units'][0]['purchase_date'].year}, exactly at {format_datetime(value['units'][0]['purchase_date'], 'EEEE, d MMMM yyyy', locale='en')}"

                dispatcher.utter_message(text=message)
        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data unit.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing unit data.")
        return [SlotSet("unit_code", None)]

class ActionGetFMSUnitsWithStatus(Action):
    def name(self) -> str:
        return "action_get_fms_units_with_status"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        unit_status = tracker.get_slot("unit_status")
        logger.info(f"Language: {language}")
        logger.info(f"Unit Status: {unit_status}")
        
        value = None
        if token_fms is not None :
            value = get_all_equipments_fms(token_fms,"is_active", "true" if unit_status=="aktif" else "false")
        logger.info(f"API Response: {value}")

        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (f"Maaf, tidak ada unit yang ditemukan dengan status {unit_status}.\n")
           
                if len(value['units']) != 0 :
                    message = f"Berikut adalah daftar unit dengan status {unit_status}:\n"
                    for i in range (len(value['units'])):
                        table_data.append([f"{i+1}", f"{value['units'][i]['unit_name']}", f"{value['units'][i]['equipment_type']}", f"{value['units'][i]['site_name']}"])
                
                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Kode Unit","Tipe Equipment","Site"], data= table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (f"Sorry, I couldn't find information for the unit with status {unit_status}.\n")
           
                if len(value['units']) != 0 :
                    message = f"The following is a list of units with status {unit_status}:\n."
                    for i in range (len(value['units'])):
                        table_data.append([f"{i+1}", f"{value['units'][i]['unit_name']}", f"{value['units'][i]['equipment_type']}", f"{value['units'][i]['site_name']}"])
                
                dispatcher.utter_message(text=message)
                doc.add_table(header=["No","Unit Code","Equipment Type","Site"], data= table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data unit.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing unit data.")
        return [SlotSet("unit_status", None)]

class ActionGetFMSUnitInformation(Action):
    def name(self) -> str:
        return "action_get_fms_unit_information"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        unit_code = tracker.get_slot("unit_code")
        logger.info(f"Language: {language}")
        logger.info(f"Unit Status: {unit_code}")

        value = None
        if token_fms is not None :
            value = get_all_equipments_fms(token_fms,"search", unit_code)
        logger.info(f"API Response: {value}")

        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (f"Maaf, tidak ada unit yang ditemukan dengan kode {unit_code}.\n")
                
                if len(value['units']) != 0:
                    message = f"Berikut adalah detail informasi tentang unit {unit_code}:"
                    table_data.append(["Tipe Equipment", f"{value['units'][0]['equipment_type']}"])
                    table_data.append(["Kategori Equipment", f"{value['units'][0]['equipment_category_name']}"])
                    table_data.append(["Manufacture", f"{value['units'][0]['manufacture_name']}"])
                    table_data.append(["Model", f"{value['units'][0]['model']}"])
                    table_data.append(["Modification", f"{value['units'][0]['modification_description']}"])
                    table_data.append(["Unit Serial Number", f"{value['units'][0]['serial_number']}"])
                    table_data.append(["Head Unit Serial Number", f"{value['units'][0]['head_unit_sn']}"])
                    table_data.append(["Nearon Serial Number", f"{value['units'][0]['nearon_sn']}"])
                    table_data.append(["Lokasi Project Site", f"{value['units'][0]['location']}"])
                    table_data.append(["Status Berjalan", f"{value['units'][0]['condition_status']}"])
                    table_data.append(["Status", f"{'Aktif' if value['units'][0]['is_active'] else 'Tidak Aktif'}"])
                    table_data.append(["Tanggal Pembelian", f"{format_datetime(value['units'][0]['purchase_date'],'EEEE, d MMMM yyyy', locale='id')}"])
                
                dispatcher.utter_message(text=message)
                doc.add_table(header=["Deskripsi", "Nilai"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())
                
            else:
                message = (f"Sorry, I couldn't find information for the unit with code {unit_code}.\n")
           
                if len(value['units']) != 0 :
                    message = f"The following is detailed information about the unit {unit_code}:"
                    table_data.append(["Equipment Type", f"{value['units'][0]['equipment_type']}"])
                    table_data.append(["Equipment Category", f"{value['units'][0]['equipment_category_name']}"])
                    table_data.append(["Manufacture",f"{value['units'][0]['manufacture_name']}"])
                    table_data.append(["Model", f"{value['units'][0]['model']}"])
                    table_data.append(["Modification", f"{value['units'][0]['modification_description']}"])
                    table_data.append(["Unit Serial Number", f"{value['units'][0]['serial_number']}"])
                    table_data.append(["Head Unit Serial Number", f"{value['units'][0]['head_unit_sn']}"])
                    table_data.append(["Nearon Serial Number", f"{value['units'][0]['nearon_sn']}"])
                    table_data.append(["Project Site Location", f"{value['units'][0]['location']}"])
                    table_data.append(["Running Status", f"{value['units'][0]['condition_status']}"])
                    table_data.append(["Status", f"{'Active' if value['units'][0]['is_active'] else 'Inactive'}"])
                    table_data.append(["Purchase Date", f"{format_datetime(value['units'][0]['purchase_date'],'EEEE, d MMMM yyyy', locale='en')}"])
                    
                dispatcher.utter_message(text=message)
                doc.add_table(header=["Description", "Value"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data unit.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing unit data.")
        return [SlotSet("unit_code", None)]

class ActionGetFMSUnitModificationStatus(Action):
    def name(self) -> str:
        return "action_get_fms_unit_modification_status"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        unit_code = tracker.get_slot("unit_code")
        logger.info(f"Language: {language}")
        logger.info(f"Unit Code: {unit_code}")
        
        value = None
        if token_fms is not None :
            value = get_all_equipments_fms(token_fms,"search", unit_code)
        logger.info(f"API Response: {value}")

        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (f"Maaf, saya tidak menemukan data untuk unit {unit_code}. Mohon periksa kembali kode unitnya.\n")
           
                if len(value['units']) != 0 :
                    message = f"Ya, Unit **{unit_code}** telah dimodifikasi dengan rincian sebagai berikut:"
                    table_data.append(["Nama Modifikasi", f"{value['units'][0]['modification_name']}"])
                    table_data.append(["Deskripsi", f"{value['units'][0]['modification_description']}"])
                    
                dispatcher.utter_message(text=message) 
                doc.add_table(header=["Deskripsi", "Nilai"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())
            else:
                message = (f"Sorry, I didn't find data for unit {unit_code}. Please double check the unit code.\n")
           
                if len(value['units']) != 0 :
                    message = f"Yes, Unit **{unit_code}** has been modified with the following details:"
                    table_data.append(["Modification Name", f"{value['units'][0]['modification_name']}"])
                    table_data.append(["Description", f"{value['units'][0]['modification_description']}"])
                    
                dispatcher.utter_message(text=message)
                doc.add_table(header=["Description", "Value"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data unit.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing unit data.")
        return [SlotSet("unit_code", None)]

class ActionGetFMSUnitSerialNumber(Action):
    def name(self) -> str:
        return "action_get_fms_unit_serial_number"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        unit_code = tracker.get_slot("unit_code")
        logger.info(f"Language: {language}")
        logger.info(f"Unit Code: {unit_code}")
        
        value = None
        if token_fms is not None :
            value = get_all_equipments_fms(token_fms,"search", unit_code)
        logger.info(f"API Response: {value}")

        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (f"Maaf, saya tidak menemukan data untuk unit {unit_code}.\n" )
           
                if len(value['units']) != 0 :
                    message = f"Serial number untuk unit **{unit_code}** adalah {value['units'][0]['serial_number']}"
                    table_data.append(["Head Unit Serial Number", f"{value['units'][0]['head_unit_sn']}"])
                    table_data.append(["Nearon Serial Number", f"{value['units'][0]['nearon_sn']}"])
                    
                dispatcher.utter_message(text=message)
                doc.add_table(header=["Deskripsi", "Nilai"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (f"Sorry, I couldn't find information for the unit with code {unit_code}.\n")
           
                if len(value['units']) != 0 :
                    message = f"Serial number for unit **{unit_code}** is {value['units'][0]['serial_number']}"
                    table_data.append(["Head Unit Serial Number", f"{value['units'][0]['head_unit_sn']}"])
                    table_data.append(["Nearon Serial Number", f"{value['units'][0]['nearon_sn']}"])
                    
                dispatcher.utter_message(text=message)
                doc.add_table(header=["Description", "Value"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data unit.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing unit data.")
        return [SlotSet("unit_code", None)]

class ActionAskUnitCode(Action):
    def name(self):
        return "action_ask_unit_code"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "Tolong sebutkan kode unit yang Anda cari, contohnya: BD-6074, TR-5014 atau TR-04102SCO")
        else:
            dispatcher.utter_message(text = "Please state the code of unit you are looking for, for example: BD-6074, TR-5014 or TR-04102SCO")
        return []

class ActionGetCountUnitsByTypeFMS(Action):
    def name(self) -> str:
        return "action_get_fms_count_units_by_type"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        equipment_type_name = tracker.get_slot("equipment_type_name")
        value = None
        if token_fms is not None :
            value = get_all_equipments_fms(token_fms,"search", equipment_type_name)
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Saat ini terdapat **{value['total_equipments']}** unit dengan tipe **{equipment_type_name}**\n"
                )
           
                if value['total_equipments'] == 0 :
                    message = f"Tidak ada unit yang terdaftar dengan tipe {equipment_type_name}"
                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"No units listed with type {equipment_type_name}.\n"
                )
           
                if value['total_equipments'] != 0 :
                    message = f"There are currently **{value['total_equipments']}** units of type **{equipment_type_name}**"

                dispatcher.utter_message(text=message)
        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data unit.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing unit data.")
        return [SlotSet("equipment_type_name",None)]

class ActionGetFMSTotalCategoryEquipment(Action):
    def name(self) -> str:
        return "action_get_fms_total_category_equipment"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        value = None
        if token_fms is not None :
            value = get_all_equipments_categoires_fms(token_fms,"total","")
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Saat ini terdapat **{value['total_equipments']}** kategori equipment yang terdaftar di Madhani\n"
                )
                if value['total_equipments'] == 0:
                    message = "Maaf, saya tidak dapat menemukan data kategori equipment saat ini"

                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"There are currently **{value['total_equipments']}** equipment categories listed in Madhani\n"
                )
                if value['total_equipments'] == 0:
                    message = "No category equipment data found at this time."

                dispatcher.utter_message(text=message)
        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data unit.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing unit data.")
        return []
    
class ActionGetFMSCategoryEquipment(Action):
    def name(self) -> str:
        return "action_get_fms_category_equipment"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)

        value = None
        if token_fms is not None :
            value = get_all_equipments_categoires_fms(token_fms,"total","")

        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Berikut beberapa kategori equipment yang ada di Madhani:\n"
                )
                for i in range(len(value['equipment_category'])):
                    table_data.append([f"{i+1}", f"{value['equipment_category'][i]['category_name']}", f"{'Active' if value['equipment_category'][i]['is_active'] else 'Nonactive'}", f"{value['equipment_category'][i]['equipment_type']}"]) 
                            
                dispatcher.utter_message(text=message)
                doc.add_table(header=["No","Nama Kategori Equipment","Status","Jumlah Jenis"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"Following are several categories of equipment available at Madhani:\n"
                )
                for i in range(len(value['equipment_category'])):
                    table_data.append([f"{i+1}", f"{value['equipment_category'][i]['category_name']}", f"{'Active' if value['equipment_category'][i]['is_active'] else 'Nonactive'}", f"{value['equipment_category'][i]['equipment_type']}"]) 
               
                dispatcher.utter_message(text=message)
                doc.add_table(header=["No","Equipment Category Name","Status","Number of Type"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, saya tidak dapat menemukan data kategori equipment saat ini.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, I can't find equipment category data at this time.")
        return []
    
class ActionGetFMSEquipmentTypesInCategory(Action):
    def name(self) -> str:
        return "action_get_fms_equipment_types_in_category"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        category_slot = tracker.get_slot("equipment_category_name")
        value = None

        if token_fms is not None and category_slot is not None:
            value = get_all_equipments_categoires_fms(token_fms,"search",category_slot)

        if value is not None  :
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Berikut adalah tipe equipment dalam kategori **{category_slot}**:\n"
                )
                for i in range(len(value['equipment_type'])):
                    table_data.append([f"{i+1}", f"{value['equipment_type'][i]}"])

                if len(value['equipment_type'])==0:
                    message = f"Maaf, saya tidak dapat menemukan kategori {category_slot}."
                
                dispatcher.utter_message(text=message)
                doc.add_table(header=["No", "Tipe Equipment"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"The following are the types of equipment in the **{category_slot}** category:\n"
                )
                for i in range(len(value['equipment_type'])):
                    table_data.append([f"{i+1}", f"{value['equipment_type'][i]}"])

                if len(value['equipment_type'])==0:
                    message = f"Sorry, I couldn't find the category {category_slot}."
                
                dispatcher.utter_message(text=message)
                doc.add_table(header=["No", "Equipment Type"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())
                
        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Tidak ada tipe equipment yang terdaftar dalam kategori tersebut.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="There's no type equipment available on that category")
        return [SlotSet("equipment_category_name",None)]
    
class ActionAskEquipmentCategoryName(Action):
    def name(self):
        return "action_ask_equipment_category_name"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "Tolong sebutkan kategori equipment yang Anda cari, contohnya: Amphibis, Big Digger, Dump Truck atau Small Excavator")
        else:
            dispatcher.utter_message(text = "Please state the category of equipment you are looking for, for example: Amphibis, Big Digger, Dump Truck or Small Excavator")
        return []

class ActionGetFMSEquipmentCategoryStatus(Action):
    def name(self) -> str:
        return "action_get_fms_equipment_category_status"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        category_slot = tracker.get_slot("equipment_category_name")
        value = None

        if token_fms is not None and category_slot is not None:
            value = get_all_equipments_categoires_fms(token_fms, "search", category_slot)

        if value and 'equipment_category' in value and len(value['equipment_category']) > 0:
            is_active_status_id = 'Aktif' if value['equipment_category'][0]['is_active'] else 'Tidak Aktif'
            if language == "indonesia":
                message = (
                    f"Status untuk kategori equipment **{category_slot}** saat ini adalah **{is_active_status_id}**\n"
                )
                if len(value['equipment_type']) == 0:
                    message = f"Maaf, saya tidak dapat menemukan kategori {category_slot}."
                
                dispatcher.utter_message(text=message) 
            else:
                is_active_status_en = 'Active' if value['equipment_category'][0]['is_active'] else 'Inactive'
                message = (
                    f"The current status for the equipment category **{category_slot}** is **{is_active_status_en}** \n"
                )
                if len(value['equipment_type']) == 0:
                    message = f"Sorry, I couldn't find the category {category_slot}."
                
                dispatcher.utter_message(text=message)

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text="Terjadi kesalahan dari server.")
        elif language == "english" and value is None:
            dispatcher.utter_message(text="There was a mistake from server.")

        return [SlotSet("equipment_category_name", None)]

class ActionGetFMSEquipmentCategoryFromStatus(Action):
    def name(self) -> str:
        return "action_get_fms_equipment_category_from_status"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        equipment_category_status = tracker.get_slot("equipment_category_status")
        value = None

        status_mapping = {
            "aktif" : True,
            "tidak aktif": False,
            "active":True,
            "inactive": False,
        }
        is_active_status = status_mapping.get(equipment_category_status.lower(), None)

        if token_fms is not None and is_active_status is not None:
            value = get_all_equipments_categoires_fms(token_fms, "is_active", is_active_status)

        if value is not None:
            doc = snakemd.Document()
            table_data = []

            header_status = "Aktif" if is_active_status else "Tidak Aktif"
            if language == "indonesia":
                message = (
                    f"Berikut beberapa kategori equipment yang memiliki status **{header_status}** yang ada di Madhani:\n"
                )
                for i in range(len(value['equipment_category'])):
                    status = "Aktif" if value['equipment_category'][i]['is_active'] else "Tidak Aktif"
                    table_data.append([f"{i+1}", f"{value['equipment_category'][i]['category_name']}", f"{status}", f"{value['equipment_category'][i]['equipment_type']}"])

                if len(value['equipment_category']) == 0:
                    message = f"Maaf, saya tidak dapat menemukan kategori dengan status {header_status}."
                
                dispatcher.utter_message(text=message)
                doc.add_table(header=["No", "Nama Kategori Equipment", "Status", "Jumlah Jenis"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"The following are several equipment categories that have **{header_status}** status in Madhani:\n"
                )
                for i in range(len(value['equipment_category'])):
                    status = "Active" if value['equipment_category'][i]['is_active'] else "Inactive"
                    table_data.append([f"{i+1}", f"{value['equipment_category'][i]['category_name']}", f"{status}", f"{value['equipment_category'][i]['equipment_type']}"])

                if len(value['equipment_category']) == 0:
                    message = f"Sorry, I couldn't find equipment category data with the current {header_status} status."
                
                dispatcher.utter_message(text=message)
                doc.add_table(header=["No", "Equipment Category Name", "Status", "Number of Type"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text="Terjadi kesalahan pada server")
        elif language == "english" and value is None:
            dispatcher.utter_message(text="There was an error from server")
        return [SlotSet("equipment_category_status", None)]

class ActionGetFMSTotalEquipmentFromType(Action):
    def name(self) -> str:
        return "action_get_fms_total_equipment_category_from_type"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        equipment_type_name = tracker.get_slot("equipment_type_name")
        category_slot = tracker.get_slot("equipment_category_name")
        value = None
        if token_fms is not None and equipment_type_name and category_slot is not None :
            value = get_all_equipments_categoires_fms(token_fms,"search",category_slot)
        if value is not None :
            if language == "indonesia":
                message = (
                    f"Ada **{value['total_equipments']}** kategori **{category_slot}** yang memiliki tipe equipment **{equipment_type_name}** di Madhani\n"
                )
                if len(value['equipment_type'])==0:
                    message = f"Maaf, saat ini saya tidak dapat menemukan data kategori equipment dengan tipe {category_slot}"
                
                dispatcher.utter_message(text=message) 

            else:
                message = (
                    f"There are **{value['total_equipments']}** categories of **{category_slot}** that have the equipment type **{equipment_type_name}** in Madhani\n"
                )

                if len(value['equipment_type'])==0:
                    message = f"Sorry, I can't find equipment category data with type {category_slot} at this time"
                dispatcher.utter_message(text=message)

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Terjadi kesalahan dari server.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="There was a mistake from server")
        return [SlotSet("equipment_type_name",None), SlotSet("equipment_category_name",None)]   

class ActionGetFMSWOBySite(Action):
    def name(self) -> str:
        return "action_get_fms_wo_by_site"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        work_order_site_name  = tracker.get_slot("work_order_site_name")
        value = None
        if token_fms is not None :
            value = get_all_work_orders_fms(token_fms,"site_id",work_order_site_name)

        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Berikut adalah detail daftar work order yang terdaftar di site **{work_order_site_name}**:\n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['pit_name']}", f"{value['data'][i]['shift_name']}", f"{format_datetime(datetime.strptime(value['data'][i]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='id')}"])
                
                if value['total'] == 0:
                    message = f"Maaf, tidak ada work order yang ditemukan untuk site {work_order_site_name}."

                dispatcher.utter_message(text=message)
                doc.add_table(header=["No","Nomor Work Order","Pit","Shift","Tanggal"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"The following is a detailed list of work orders registered on site **{work_order_site_name}**:\n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['pit_name']}", f"{value['data'][i]['shift_name']}", f"{format_datetime(datetime.strptime(value['data'][i]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='en')}"])

                if value['total'] == 0:
                    message = f"Sorry, no work orders were found for site {work_order_site_name}."

                dispatcher.utter_message(text=message)
                doc.add_table(header=["No","Work Order Number","Pit","Shift","Date"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("work_order_site_name",None)]

class ActionAskWorkOrderSiteName(Action):
    def name(self):
        return "action_ask_work_order_site_name"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "Di lokasi site mana Anda ingin mencari informasi work order ini? Mohon sebutkan nama atau ID site, contohnya: 001A, 001D atau 001M")
        else:
            dispatcher.utter_message(text = "At which site location do you want to look for this work order information? Please state the name or site ID, for example: 001A, 001D or 001M")
        return []

class ActionGetFMSLastShiftOfWorkOrder(Action):
    def name(self) -> str:
        return "action_get_fms_last_shift_of_work_order"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        shift_name  = tracker.get_slot("shift_name")
        value = None

        if token_fms is not None :
            value = get_all_work_orders_fms(token_fms,"shift_name",shift_name)

        if value is not None:
            if language == "indonesia":
                message = (
                    f"Work Order terakhir Anda yang tercatat pada shift **{shift_name}**, berikut detail informasi nya:\n"                        
                )
                message += (
                    f"- Nomor Work Order: {value['data'][0]['work_order_no']}\n"
                    f"- Pit: {value['data'][0]['pit_name']}\n"
                    f"- Site: {value['data'][0]['site_name']}\n"
                    f"- Tanggal: {format_datetime(datetime.strptime(value['data'][0]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='id')}\n"
                )
                if value['total'] == 0:
                    message = f"Maaf, tidak ada work order yang ditemukan untuk shift {shift_name}."
                dispatcher.utter_message(text=message)

            else:
                message = (
                    f"Your last Work Order was recorded on shift **{shift_name}**, here is the detailed information:\n"                        
                )
                message += (
                    f"- Work Order Number: {value['data'][0]['work_order_no']}\n"
                    f"- Pit: {value['data'][0]['pit_name']}\n"
                    f"- Site: {value['data'][0]['site_name']}\n"
                    f"- Date: {format_datetime(datetime.strptime(value['data'][0]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='en')}\n"
                )
                if value['total'] == 0:
                    message = f"Sorry, no work orders were found for shift {shift_name}."
                dispatcher.utter_message(text=message)

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("shift_name",None)]
    
class ActionAskShiftName(Action):
    def name(self):
        return "action_ask_shift_name"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "Silahkan sebutkan shift, contohnya: Day atau Night")
        else:
            dispatcher.utter_message(text = "Please state the shift, for example: Day or Night")
        return [] 
    
class ActionGetFMSActiveWorkOrders(Action):
    def name(self) -> str:
        return "action_get_fms_active_work_orders"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        value = None

        if token_fms is not None :
            value = get_all_work_orders_fms(token_fms,"is_active",True)

        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Berikut adalah daftar work order Anda yang berstatus **aktif**:\n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['site_name']}", f"{value['data'][i]['pit_name']}", f"{value['data'][i]['shift_name']}", f"{format_datetime(datetime.strptime(value['data'][0]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='id')}"])

                if value['total'] == 0:
                    message = f"Maaf, tidak ada work order yang ditemukan untuk shift akfif."

                dispatcher.utter_message(text=message)
                doc.add_table(header=["No","Nomor Work Order","Site","Pit","Shift","Tanggal"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"The following is a detailed list of work orders that has status **active**: \n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['site_name']}", f"{value['data'][i]['pit_name']}", f"{value['data'][i]['shift_name']}", f"{format_datetime(datetime.strptime(value['data'][0]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='en')}"])

                if value['total'] == 0: 
                    message = f"Sorry, no work orders were found for active shift."

                dispatcher.utter_message(text=message)
                doc.add_table(header=["No","Work Order Number","Site","Pit","Shift","Date"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return []
    
class ActionGetFMSWOByShift(Action):
    def name(self) -> str:
        return "action_get_fms_wo_by_shift"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        shift_name = tracker.get_slot("shift_name")
        value = None

        if token_fms is not None :
            value = get_all_work_orders_fms(token_fms,"shift_name",shift_name)

        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Berikut adalah daftar Work Order Anda yang bekerja pada shift {shift_name}: \n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['site_name']}", f"{value['data'][i]['pit_name']}"])

                if value['total'] == 0:
                    message = f"Maaf, tidak ada work order yang ditemukan untuk shift {shift_name}."

                dispatcher.utter_message(text=message)
                doc.add_table(header=["No","Nomor Work Order","Site","Pit"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"The following is a detailed list of work orders that on shift **{shift_name}**: "                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['site_name']}", f"{value['data'][i]['pit_name']}"])

                if value['total'] == 0:
                    message = f"Sorry, no work orders were found for shift {shift_name}."

                dispatcher.utter_message(text=message)
                doc.add_table(header=["No","Work Order Number","Site","Pit"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("shift_name",None)]

class ActionAskDate(Action):
    def name(self):
        return "action_ask_date"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "Silakan masukkan tanggal. Harap gunakan format YYYY-mm-dd, contoh: 2024-12-01. Anda juga dapat mengetikkan 'hari ini', 'kemarin siang', atau 'kemarin malam'")
        else:
            dispatcher.utter_message(text = "Please enter the date. Use the format YYYY-mm-dd, for example: 2024-12-01. You can also type 'today', 'last noon', or 'last night")
        return []
    
class ActionGetFMSWorkOrdersByDate(Action):
    def name(self) -> str:
        return "action_get_fms_work_orders_by_date"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        date_slot = tracker.get_slot("date")
        value = None
        if token_fms is not None :
            if date_slot == "kemarin siang" or date_slot == "last noon":
                today = datetime.now().date()
                yesterday = today - timedelta(days=1)
                formatted_yesterday = yesterday.strftime('%Y-%m-%d')
                date_slot = formatted_yesterday
                value = get_all_work_orders_fms(token_fms,"date_shift",[date_slot,"Day"])
            
            elif date_slot == "kemarin malam" or date_slot == "last night":
                today = datetime.now().date()
                yesterday = today - timedelta(days=1)
                formatted_yesterday = yesterday.strftime('%Y-%m-%d')
                date_slot = formatted_yesterday
                value = get_all_work_orders_fms(token_fms,"date_shift",[date_slot,"Night"])
            
            elif date_slot == "hari ini" or date_slot == "today":
                today = datetime.now().date().strftime('%Y-%m-%d')
                date_slot = today
                value = get_all_work_orders_fms(token_fms,"date",date_slot)
                
            else:
                value = get_all_work_orders_fms(token_fms,"date",date_slot)

        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Terdapat **{value['total']}** work order Anda yang tercatat pada tanggal {format_datetime(datetime.strptime(date_slot, '%Y-%m-%d'), 'd MMMM yyyy', locale='id')}.\nBerikut adalah daftarnya:\n" 
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['site_name']}", f"{value['data'][i]['shift_name']}", f"{value['data'][i]['pit_name']}"])

                if value['total'] == 0:
                    message = f"Maaf, tidak ada work order pada tanggal {format_datetime(datetime.strptime(date_slot, '%Y-%m-%d'), 'd MMMM yyyy', locale='id')}."

                dispatcher.utter_message(text=message)
                doc.add_table(header=["No","Nomor Work Order","Site","Shift","Pit"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"There are **{value['total']}** of your work orders recorded on {format_datetime(datetime.strptime(date_slot, '%Y-%m-%d'), 'd MMMM yyyy', locale='en')}.\nHere is the list:"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['site_name']}", f"{value['data'][i]['shift_name']}", f"{value['data'][i]['pit_name']}"])

                if value['total'] == 0:
                    message = f"Sorry, no work orders were found at {format_datetime(datetime.strptime(date_slot, '%Y-%m-%d'), 'd MMMM yyyy', locale='en')}."
               
                dispatcher.utter_message(text=message)
                doc.add_table(header=["No","Work Order Number","Site","Shift","Pit"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("date",None)]

class ActionGetFMSWorkOrdersBySiteDate(Action):
    def name(self) -> str:
        return "action_get_fms_work_orders_by_site_date"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        date_slot = tracker.get_slot("date")
        site_name = tracker.get_slot("work_order_number_site_name")
        value = None
        if token_fms is not None and site_name is not None:
            if date_slot == "kemarin siang" or date_slot == "last noon":
                today = datetime.now().date()
                yesterday = today - timedelta(days=1)
                formatted_yesterday = yesterday.strftime('%Y-%m-%d')
                date_slot = formatted_yesterday
                value = get_all_work_orders_fms(token_fms,"site_last_day",[site_name,date_slot,"Day"])
            
            elif date_slot == "kemarin malam" or date_slot == "last night":
                today = datetime.now().date()
                yesterday = today - timedelta(days=1)
                formatted_yesterday = yesterday.strftime('%Y-%m-%d')
                date_slot = formatted_yesterday
                value = get_all_work_orders_fms(token_fms,"site_last_night",[site_name,date_slot,"Night"])
            
            elif date_slot == "hari ini" or date_slot == "today":
                today = datetime.now().date().strftime('%Y-%m-%d')
                date_slot = today
                value = get_all_work_orders_fms(token_fms,"site_date",[site_name,date_slot])
                
            else:
                value = get_all_work_orders_fms(token_fms,"site_date",[site_name,date_slot])
        
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            total_work_orders = value.get("total",0)
            if total_work_orders > 0:
                if language == "indonesia":
                    message = (
                        f"Berikut work order Anda pada tanggal {format_datetime(datetime.strptime(date_slot, '%Y-%m-%d'), 'd MMMM yyyy', locale='id')} pada site {site_name}: \n"                        
                    )
                    for i in range(len(value['data'])):
                        table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['shift_name']}", f"{value['data'][i]['pit_name']}", f"{format_datetime(datetime.strptime(value['data'][i]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='id')}"])

                    if value['total'] == 0:
                        message = f"Maaf, tidak ada work order pada tanggal {format_datetime(datetime.strptime(date_slot, '%Y-%m-%d'), 'd MMMM yyyy', locale='id')} pada site {site_name}."

                    dispatcher.utter_message(text=message) 
                    doc.add_table(header=["No","Nomor Work Order","Shift","Pit","Tanggal"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())

                else:
                    message = (
                        f"The following is your work order on the date {format_datetime(datetime.strptime(date_slot, '%Y-%m-%d'), 'd MMMM yyyy', locale='id')} on site {site_name}: \n "                        
                    )
                    for i in range(len(value['data'])):
                        table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['shift_name']}", f"{value['data'][i]['pit_name']}", f"{format_datetime(datetime.strptime(value['data'][i]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='en')}"])

                    if value['total'] == 0:
                        message = f"Sorry, no work orders were found at {format_datetime(datetime.strptime(date_slot, '%Y-%m-%d'), 'd MMMM yyyy', locale='en')} in site {site_name}."

                    dispatcher.utter_message(text=message) 
                    doc.add_table(header=["No","Work Order Number","Shift","Pit","Date"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("date",None), SlotSet("work_order_number_site_name",None)]
    
class ActionAskWorkOrderNumberSiteName(Action):
    def name(self):
        return "action_ask_work_order_number_site_name"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "Di site mana Anda ingin mengetahui nomor work order yang tercatat? Mohon sebutkan nama atau ID site, contohnya: 001A, 001D, atau 001M")
        else:
            dispatcher.utter_message(text = "At which site would you like to check the recorded work order number? Please state the name or site ID, for example: 001A, 001D, or 001M")
        return []
    
class ActionGetFMSWorkOrdersBySiteToday(Action):
    def name(self) -> str:
        return "action_get_fms_work_orders_by_site_today"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        current_date = datetime.now().date()
        formatted_date = current_date.strftime('%Y-%m-%d')
        date_slot = formatted_date
        site_name = tracker.get_slot("work_order_number_site_name")
        logger.info(f"Action: action_get_fms_work_orders_by_site_today")
        value = None

        if token_fms is not None :
            value = get_all_work_orders_fms(token_fms,"site_date",[site_name,date_slot])
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Berikut adalah nomor work order Anda untuk site {site_name} pada hari ini:\n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['shift_name']}", f"{value['data'][i]['pit_name']}", f"{format_datetime(datetime.strptime(value['data'][i]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='id')}"])

                if value['total'] == 0:
                    message = f"Maaf, tidak ada work order pada hari ini di site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Nomor Work Order","Shift","Pit","Tanggal"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"The following is your work order number for site {site_name} today:\n "                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['shift_name']}", f"{value['data'][i]['pit_name']}", f"{format_datetime(datetime.strptime(value['data'][i]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='en')}"])

                if value['total'] == 0:
                    message = f"Sorry, no work orders were found today in site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Work Order Number","Shift","Pit","Date"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("date",None), SlotSet("work_order_number_site_name",None)]
    
class ActionGetFMSWorkOrdersBySiteLastNight(Action):
    def name(self) -> str:
        return "action_get_fms_work_orders_by_site_last_night"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("work_order_number_site_name")
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        formatted_yesterday = yesterday.strftime('%Y-%m-%d')
        shift_name = "Night"
        logger.info(f"Action: action_get_fms_work_orders_by_site_last_night")
        value = None
        if token_fms is not None :
            value = get_all_work_orders_fms(token_fms,"site_last_night",[site_name,formatted_yesterday ,shift_name])
            
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Berikut adalah nomor work order Anda untuk site {site_name} pada kemarin malam:\n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['shift_name']}", f"{value['data'][i]['pit_name']}", f"{format_datetime(datetime.strptime(value['data'][i]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='id')}"])

                if value['total'] == 0:
                    message = f"Maaf, tidak ada work order pada kemarin malam di site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Nomor Work Order","Shift","Pit","Tanggal"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"The following is your work order number for site {site_name} as of last night:\n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['shift_name']}", f"{value['data'][i]['pit_name']}", f"{format_datetime(datetime.strptime(value['data'][i]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='en')}"])

                if value['total'] == 0:
                    message = f"Sorry, no work orders were found at yesterday night in site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Work Order Number","Shift","Pit","Date"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("work_order_number_site_name",None)]
    
class ActionGetFMSWorkOrdersBySiteLastDay(Action):
    def name(self) -> str:
        return "action_get_fms_work_orders_by_site_last_Day"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("work_order_number_site_name")
        value = None
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        formatted_yesterday = yesterday.strftime('%Y-%m-%d')
        shift_name = "Day"
        logger.info(f"Action: action_get_fms_work_orders_by_site_last_Day")
        if token_fms is not None :
            value = get_all_work_orders_fms(token_fms,"site_last_day",[site_name, formatted_yesterday,shift_name])
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Berikut adalah nomor work order Anda untuk site {site_name} pada kemarin siang: \n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['shift_name']}", f"{value['data'][i]['pit_name']}", f"{format_datetime(datetime.strptime(value['data'][i]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='id')}"])

                if value['total'] == 0:
                    message = f"Maaf, tidak ada work order pada kemarin siang di site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Nomor Work Order","Shift","Pit","Tanggal"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"The following is your work order number for site {site_name} as of last noon: \n "                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['shift_name']}", f"{value['data'][i]['pit_name']}", f"{format_datetime(datetime.strptime(value['data'][i]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='en')}"])

                if value['total'] == 0:
                    message = f"Sorry, no work orders were found at last noon in site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Work Order Number","Shift","Pit","Date"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("work_order_number_site_name",None)]

class ActionGetFMSWorkOrdersToday(Action):
    def name(self) -> str:
        return "action_get_fms_work_orders_today"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        current_date = datetime.now().strftime('%Y-%m-%d')
        logger.info(f"Action: action_get_fms_work_orders_today")
        value = None
        if token_fms is not None :
            value = get_all_work_orders_fms(token_fms,"date",current_date)
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            total_work_orders = value.get("total", 0)
            if total_work_orders > 0:
                if language == "indonesia":
                    message = (
                        f"Terdapat **{total_work_orders}** work order yang tercatat hari ini, {format_datetime(datetime.strptime(current_date, '%Y-%m-%d'), 'd MMMM yyyy', locale='id')}.\nBerikut adalah daftar work order tersebut:\n"                        
                    )
                    for i in range(len(value['data'])):
                        table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['shift_name']}", f"{value['data'][i]['pit_name']}", f"{value['data'][i]['site_name']}", f"{format_datetime(datetime.strptime(value['data'][i]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='id')}"])

                    if value['total'] == 0:
                        message = f"Maaf, tidak ada work order pada tanggal {format_datetime(datetime.strptime(current_date, '%Y-%m-%d'), 'd MMMM yyyy', locale='id')}."

                    dispatcher.utter_message(text=message) 
                    doc.add_table(header=["No","Nomor Work Order","Shift","Pit","Site","Tanggal"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())

                else:
                    message = (
                        f"There are **{total_work_orders}** work orders recorded today, {format_datetime(datetime.strptime(current_date, '%Y-%m-%d'), 'd MMMM yyyy', locale='en')}.\nThe following is a list of work orders:\n"                        
                    )
                    for i in range(len(value['data'])):
                        table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['shift_name']}", f"{value['data'][i]['pit_name']}", f"{value['data'][i]['site_name']}", f"{format_datetime(datetime.strptime(value['data'][i]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='en')}"])

                    if value['total'] == 0:
                        message = f"Sorry, no work orders were found at {format_datetime(datetime.strptime(current_date, '%Y-%m-%d'), 'd MMMM yyyy', locale='en')}."

                    dispatcher.utter_message(text=message)
                    doc.add_table(header=["No","Work Order Number","Shift","Pit","Site","Date"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("date",None)]

class ActionGetFMSWorkOrdersLastNoon(Action):
    def name(self) -> str:
        return "action_get_fms_work_orders_last_noon"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        current_date = datetime.now().date()
        logger.info(f"Action: action_get_fms_work_orders_last_noon")
        yesterday = current_date - timedelta(days=1)
        formatted_date = yesterday.strftime('%Y-%m-%d')
        date_slot = formatted_date
        value = None
        if token_fms is not None :
            value = get_all_work_orders_fms(token_fms,"date_shift",[date_slot,"Day"])
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            total_work_orders = value.get("total", 0)
            if total_work_orders > 0:
                if language == "indonesia":
                    message = (
                        f"Terdapat **{total_work_orders}** work order yang tercatat pada kemarin siang.\nBerikut adalah daftar work order tersebut:\n"                        
                    )
                    for i in range(len(value['data'])):
                        table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['shift_name']}", f"{value['data'][i]['pit_name']}", f"{value['data'][i]['site_name']}", f"{format_datetime(datetime.strptime(value['data'][i]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='id')}"])

                    if value['total'] == 0:
                        message = f"Maaf, tidak ada work order pada kemarin siang."

                    dispatcher.utter_message(text=message) 
                    doc.add_table(header=["No","Nomor Work Order","Shift","Pit","Site","Tanggal"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())

                else:
                    message = (
                        f"There are **{total_work_orders}** work orders recorded last noon.\nThe following is a list of work orders:\n"                        
                    )
                    for i in range(len(value['data'])):
                        table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['shift_name']}", f"{value['data'][i]['pit_name']}", f"{value['data'][i]['site_name']}", f"{format_datetime(datetime.strptime(value['data'][i]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='en')}"])

                    if value['total'] == 0:
                        message = f"Sorry, no work orders were found at last noon."

                    dispatcher.utter_message(text=message)
                    doc.add_table(header=["No","Work Order Number","Shift","Pit","Site","Date"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("date",None), SlotSet("shift_name",None)]
    
class ActionGetFMSWorkOrdersLastNight(Action):
    def name(self) -> str:
        return "action_get_fms_work_orders_last_night"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        current_date = datetime.now().date()
        yesterday = current_date - timedelta(days=1)
        formatted_date = yesterday.strftime('%Y-%m-%d')
        date_slot = formatted_date
        value = None
        if token_fms is not None :
            value = get_all_work_orders_fms(token_fms,"date_shift",[date_slot,"Night"])
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            total_work_orders = value.get("total", 0)
            if total_work_orders > 0:
                if language == "indonesia":
                    message = (
                        f"Terdapat **{total_work_orders}** work order yang tercatat pada kemarin malam.\nBerikut adalah daftar work order tersebut:\n"                        
                    )
                    for i in range(len(value['data'])):
                        table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['shift_name']}", f"{value['data'][i]['pit_name']}", f"{value['data'][i]['site_name']}", f"{format_datetime(datetime.strptime(value['data'][i]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='id')}"])

                    if value['total'] == 0:
                        message = f"Maaf, tidak ada work order pada kemarin malam."
                    dispatcher.utter_message(text=message) 
                    doc.add_table(header=["No","Nomor Work Order","Shift","Pit","Site","Tanggal"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())

                else:
                    message = (
                        f"There are **{total_work_orders}** work orders recorded last night.\nThe following is a list of work orders:\n"                        
                    )
                    for i in range(len(value['data'])):
                        table_data.append([f"{i+1}", f"{value['data'][i]['work_order_no']}", f"{value['data'][i]['shift_name']}", f"{value['data'][i]['pit_name']}", f"{value['data'][i]['site_name']}", f"{format_datetime(datetime.strptime(value['data'][i]['date'], '%Y-%m-%dT%H:%M:%SZ'), 'd MMMM yyyy', locale='en')}"])

                    if value['total'] == 0:
                        message = f"Sorry, no work orders were found at last night."
                    dispatcher.utter_message(text=message)
                    doc.add_table(header=["No","Work Order Number","Shift","Pit","Site","Date"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("date",None), SlotSet("shift_name",None)]

class ActionGetFMSWorkOrdersDayCondition(Action):
    def name(self) -> str:
        return "action_get_fms_work_orders_day_condition"  
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        day_condition = tracker.get_slot("day_condition")
        logger.info(f"Day condition : {day_condition}" )
        language = tracker.get_slot("language")
        logger.info(f"Language : {language}" )
        if day_condition == "today" or day_condition == "hari ini":
            return [FollowupAction("action_get_fms_work_orders_today")]
        elif day_condition == "last noon" or day_condition == "kemarin siang":
            return [FollowupAction("action_get_fms_work_orders_last_noon")]
        elif day_condition == "last night" or day_condition == "kemarin malam":
            return [FollowupAction("action_get_fms_work_orders_last_night")]
        
        if language == "indonesia":
            return dispatcher.utter_message(text="Tidak bisa memroses pesan") 

        return dispatcher.utter_message(text="Cannot proceed your message")
    
class ActionGetFMSWorkOrdersBySiteDayCondition(Action):
    def name(self) -> str:
        return "action_get_fms_work_orders_by_site_day_condition"  
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        day_condition = tracker.get_slot("day_condition")
        logger.info(f"Day condition : {day_condition}" )
        language = tracker.get_slot("language")
        logger.info(f"Language : {language}" )
        if day_condition == "today" or day_condition == "hari ini":
            return [FollowupAction("action_get_fms_work_orders_by_site_today")]
        elif day_condition == "last noon" or day_condition == "kemarin siang":
            return [FollowupAction("action_get_fms_work_orders_by_site_last_Day")]

        elif day_condition == "last night" or day_condition == "kemarin malam":
            return [FollowupAction("action_get_fms_work_orders_by_site_last_night")]

        if language == "indonesia":
            return dispatcher.utter_message(text="Tidak bisa memroses pesan") 

        return dispatcher.utter_message(text="Cannot proceed your message")
    
class ActionGetFMSWABySite(Action):
    def name(self) -> str:
        return "action_get_fms_wa_by_site"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        work_area_site_name = tracker.get_slot("work_area_site_name")
        value = None
        if token_fms is not None :
            value = get_all_work_area_by_site_fms(token_fms,"search","",work_area_site_name)
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Berikut adalah daftar work area yang ada di site {work_area_site_name}: \n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['name']}", f"{value['data'][i]['pit_name']}"])

                if value['total'] == 0:
                    message = f"Maaf, tidak ada work area yang ditemukan untuk site {work_area_site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Work Area","Pit"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"The following is a list of work areas on site {work_area_site_name}: \n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['name']}", f"{value['data'][i]['pit_name']}"])

                if value['total'] == 0:
                    message = f"Sorry, no work areas were found for site. {work_area_site_name}"

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Work Area","Pit"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("work_area_site_name",None)]

class ActionAskWorkAreaSiteName(Action):
    def name(self):
        return "action_ask_work_area_site_name"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "Di lokasi site mana Anda ingin mencari informasi work area ini? Mohon sebutkan nama atau ID site, contohnya: 001A, 001D atau 001M")
        else:
            dispatcher.utter_message(text = "At which site location do you want to find information on this work area? Please state the name or site ID, for example: 001A, 001D or 001M")
        return []
    
class ActionGetFMSTotalWABySite(Action):
    def name(self) -> str:
        return "action_get_fms_total_wa_by_site"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        work_area_site_name = tracker.get_slot("work_area_site_name")
        value = None
        if token_fms is not None :
            value = get_all_work_area_by_site_fms(token_fms,"search","",work_area_site_name)
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Ada **{value['total']}** work area yang berada di site {work_area_site_name}\n"                        
                )

                if value['total'] == 0:
                    message = f"Saat ini, tidak ada work area Anda yang pada site {work_area_site_name}"

                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"There are **{value['total']}** work areas located in site {work_area_site_name}\n"                        
                )

                if value['total'] == 0:
                    message = f"Currently, theres no work area located in site {work_area_site_name}"

                dispatcher.utter_message(text=message)
        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("work_area_site_name",None)]

class ActionGetFMSAskWABySiteDisposal(Action):
    def name(self) -> str:
        return "action_get_fms_ask_wa_by_site_disposal"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        work_area_site_name = tracker.get_slot("work_area_site_name")
        work_area_name = tracker.get_slot("work_area_name")
        value = None
        if token_fms is not None :
            value = get_all_work_area_by_site_fms(token_fms,"search",work_area_name,work_area_site_name)
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Ya, Work Area **{work_area_name}** adalah area disposal \n"                        
                )
                if value['total'] == 0:
                    message = f"Sorry, no work area with the name {work_area_name} was found."

                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"Yes, Work Area **{work_area_name}** is a disposal area"                        
                )

                if value['total'] == 0:
                    message = f"Sorry, no work areas were found for site {work_area_site_name}"

                dispatcher.utter_message(text=message)
        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= f"Maaf, tidak ditemukan work area dengan nama {work_area_name}.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text=f"Sorry, no work areas were found for work area {work_area_name}")

        return [SlotSet("work_area_site_name",None), SlotSet("work_area_name",None)]

class ActionAskWorkAreaName(Action):
    def name(self):
        return "action_ask_work_area_name"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "Tolong sebutkan nama work area yang ingin Anda cek, contohnya: G09, Front 1 atau Front 2")
        else:
            dispatcher.utter_message(text = "Please state the name of the work area you want to check, for example: G09, Front 1 or Front 2")
        return []
    
class ActionGetFMSTotalWABySiteDisposal(Action):
    def name(self) -> str:
        return "action_get_fms_total_wa_by_site_disposal"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        work_area_site_name = tracker.get_slot("work_area_site_name")
        value = None
        if token_fms is not None :
            value = get_all_work_area_by_site_fms(token_fms,"disposal","true",work_area_site_name)
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Ada **{value['total']}** work area yang berada di site **{work_area_site_name}** yang merupakan area disposal.\nBerikut adalah daftar work area pada site {work_area_site_name} yang merupakan disposal:\n"                       
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['name']}", f"{value['data'][i]['pit_name']}"])

                if value['total'] == 0:
                    message = f"Saat ini, tidak ada work area di {work_area_site_name} yang merupakan area disposal.\n"

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Work Area","Pit"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())
            else:
                message = (
                    f"There are **{value['total']}** work areas located in site **{work_area_site_name}** that are disposal area.\nThe following is a list of work areas on site {work_area_site_name} which are disposal:\n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['name']}", f"{value['data'][i]['pit_name']}"])

                if value['total'] == 0:
                    message = f"Currently, there are no work areas in {work_area_site_name} that are disposal areas.\n"

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Work Area","Pit"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("work_area_site_name",None)]

class ActionGetFMSWABySiteInventory(Action):
    def name(self) -> str:
        return "action_get_fms_wa_by_site_inventory"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        work_area_name = tracker.get_slot("work_area_name")
        work_area_site_name = tracker.get_slot("work_area_site_name")
        value = None
        if token_fms is not None :
            value = get_all_work_area_by_site_fms(token_fms,"search",work_area_name,work_area_site_name)
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Total inventory yang tersimpan pada work area {work_area_name} di site {work_area_site_name} berjumlah **{value['data'][0]['inventory']}** unit.\n"                        
                )

                if value['total'] == 0:
                    message = f"Maaf, tidak ada work area {work_area_name} yang ditemukan untuk site {work_area_site_name}."

                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"The total inventory stored in work area {work_area_name} at site {work_area_site_name} is **{value['data'][0]['inventory']}** units. "                        
                )
                if value['total'] == 0:
                    message = f"Sorry, no work area {work_area_name} were found for site {work_area_site_name}."

                dispatcher.utter_message(text=message)
        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= f"Maaf, tidak ada work area {work_area_name} yang ditemukan untuk site {work_area_site_name}.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text=f"Sorry, no work area {work_area_name} were found for site {work_area_site_name}.")
        return [SlotSet("work_area_site_name",None), SlotSet("work_area_name",None)]

class ActionGetFMSTotalFleet(Action):
    def name(self) -> str:
        return "action_get_fms_total_fleet"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        value = None
        if token_fms is not None :
            value = get_all_fleet_setting_fms(token_fms,"total","")
        if value is not None:
            if language == "indonesia":
                message = (
                    f"Berdasarkan data terkini, total fleet yang terdaftar di Madhani mencapai **{value['total']}** unit\n"                        
                )
               
                if value['total'] == 0:
                    message = f"Saat ini tidak ada fleet yang terdaftar di sistem FMS."

                dispatcher.utter_message(text=message) 
            else:
                message = (
                    f"Based on the latest data, the total fleet registered at Madhani has reached **{value['total']}** units\n"                        
                )
               
                if value['total'] == 0:
                    message = f"Currently there are no fleets registered in the FMS system."

                dispatcher.utter_message(text=message)
        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return []

class ActionGetFMSExcavatorBySite(Action):
    def name(self) -> str:
        return "action_get_fms_excavator_by_site"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        value = None
        if token_fms is not None :
            value = get_all_fleet_setting_fms(token_fms,"search_site",["ex", site_name])
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Berikut excavator yang digunakan pada site {site_name}: \n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['excavator_model']['manufacture']}", f"{value['data'][i]['excavator_model']['name']}"])

                if value['total'] == 0:
                    message = f"Maaf, tidak ada excavator di site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Nama Excavator","Manufacture Excavator","Tipe Excavator"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"Here are the excavators in site {site_name}: \n "                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['excavator_model']['manufacture']}", f"{value['data'][i]['excavator_model']['name']}"])

                if value['total'] == 0:
                    message = f"Sorry, no work excavators in site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Excavator Name","Excavator Manufacture","Excavator Type"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("site_name",None)]

class ActionGetFMSTotalFleetBySite(Action):
    def name(self) -> str:
        return "action_get_fms_total_fleet_by_site"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        value = None
        if token_fms is not None :
            value = get_all_fleet_setting_fms(token_fms,"site_id",site_name)
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = f"Berdasarkan data terkini, terdapat **{value['total']}** fleet yang terdaftar pada site {site_name}.\nBerikut adalah daftar fleet yang tersedia di site {site_name}:\n"                        

                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['excavator_model']['manufacture']}", f"{value['data'][i]['excavator_model']['name']}", f"{value['data'][i]['excavator_operator']}", f"{value['data'][i]['activity_name']}", f"{value['data'][i]['work_area_name']}", f"{value['data'][i]['material_id']}", f"{value['data'][i]['productivity_target']['value']} {value['data'][i]['productivity_target']['unit']}"])

                if value['total'] == 0:
                    message = f"Maaf, tidak ada fleet yang terdaftar pada site {site_name}."

                dispatcher.utter_message(text=message)
                doc.add_table(header=["No","Nama Excavator","Manufacture Excavator","Tipe Excavator","Nama Operator Excavator","Aktivitas","Work Area","Deskripsi/Nama Material","Target Produksi"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"Based on the latest data, there are **{value['total']}** fleets registered on site {site_name}. Here is the list of fleets available at the {site_name} site"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['excavator_model']['manufacture']}", f"{value['data'][i]['excavator_model']['name']}", f"{value['data'][i]['excavator_operator']}", f"{value['data'][i]['activity_name']}", f"{value['data'][i]['work_area_name']}", f"{value['data'][i]['material_id']}", f"{value['data'][i]['productivity_target']['value']} {value['data'][i]['productivity_target']['unit']}"])

                if value['total'] == 0:
                    message = f"Sorry, there are no fleets registered on site {site_name}."

                dispatcher.utter_message(text=message)
                doc.add_table(header=["No","Excavator Name","Excavator Manufacture","Excavator Type","Excavator Operator Name","Activity","Work Area","Material Description/Name","Production Target"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("site_name",None)]

class ActionGetFMSExcavatorOperatorBySiteFleet(Action):
    def name(self) -> str:
        return "action_get_fms_excavator_operator_by_site_fleet"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        value = None
        if token_fms is not None :
            value = get_all_fleet_setting_fms(token_fms,"search_site",["ex", site_name])
        if value is not None:
            doc =snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Berikut detail informasi operator excavator yang tercatat di site {site_name}: \n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['excavator_model']['manufacture']}", f"{value['data'][i]['excavator_model']['name']}", f"{value['data'][i]['excavator_operator']}"])

                if value['total'] == 0:
                    message = f"Maaf, tidak ada excavator di site {site_name}."

                dispatcher.utter_message(text=message)
                doc.add_table(header=["No","Nama Excavator","Manufacture Excavator","Tipe Excavator","Nama Operator Excavator"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"The following is detailed excavator operator information recorded on site {site_name}: \n "                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['excavator_model']['manufacture']}", f"{value['data'][i]['excavator_model']['name']}", f"{value['data'][i]['excavator_operator']}"])

                if value['total'] == 0:
                    message = f"Sorry, no work excavators in site {site_name}."

                dispatcher.utter_message(text=message)
                doc.add_table(header=["No","Excavator Name","Excavator Manufacture","Excavator Type","Excavator Operator Name"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("site_name",None)]

class ActionGetFMSActivityBySite(Action):
    def name(self) -> str:
        return "action_get_fms_activity_by_site"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        activity_site_name = tracker.get_slot("activity_site_name")
        value = None
        if token_fms is not None :
            value = get_all_fleet_setting_fms(token_fms,"search_site",["", activity_site_name])
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Berikut detail informasi aktivitas pada site {activity_site_name}: \n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['activity_name']}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['excavator_operator']}", f"{value['data'][i]['work_area_name']}", f"{value['data'][i]['material_id']}"])

                if value['total'] == 0:
                    message = f"Maaf, tidak ada aktivitas di site {activity_site_name}."

                dispatcher.utter_message(text=message)
                doc.add_table(header=["No","Aktivitas","Nama Excavator","Nama Operator Excavator","Work Area","Deskripsi/Nama Material"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())
            else:
                message = (
                    f"The following is detailed activity information on site {activity_site_name}: \n "                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['activity_name']}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['excavator_operator']}", f"{value['data'][i]['work_area_name']}", f"{value['data'][i]['material_id']}"])
                    
                if value['total'] == 0:
                    message = f"Sorry, no work activity in site {activity_site_name}."

                dispatcher.utter_message(text=message)
                doc.add_table(header=["No","Activity","Excavator Name","Excavator Operator Name","Work Area","Material Description/Name"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("activity_site_name",None)]

class ActionAskActivitySiteName(Action):
    def name(self):
        return "action_ask_activity_site_name"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "Silakan sebutkan site yang ingin Anda ketahui aktivitasnya, contohnya: 001A, 001D atau 001M")
        else:
            dispatcher.utter_message(text = "Please state the site whose activity you want to know, for example: 001A, 001D or 001M")
        return []

class ActionGetFMSTotalHaulerBySite(Action):
    def name(self) -> str:
        return "action_get_fms_total_hauler_by_site"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        value = None
        if token_fms is not None :
            value = get_all_fleet_setting_fms(token_fms,"limit_site",["", site_name])
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                total_hauler =0 
                for i in range(len(value['data'])):
                    for j in range(len(value['data'][i]['haulers'])):
                        if value['data'][i]['haulers'][j]['class_name'] != "" or value['data'][i]['haulers'][j]['class_name']!= "N/A":
                            total_hauler +=1
                message = (
                    f"Berdasarkan data terkini, terdapat {total_hauler} hauler yang bekerja pada site {site_name}. Berikut adalah daftar Hauler yang bekerja pada site {site_name}: \n" 
                )
                cnt= 0 
                for i in range(len(value['data'])):
                    for j in range(len(value['data'][i]['haulers'])):
                        if value['data'][i]['haulers'][j]['class_name']!= "" or value['data'][i]['haulers'][j]['class_name']!= "N/A":
                            table_data.append([f"{cnt+1}", f"{value['data'][i]['haulers'][j]['equipment_type_name']}", f"{value['data'][i]['haulers'][j]['class_name']}", f"{value['data'][i]['haulers'][j]['amount']}"])
                            cnt +=1

                if value['total'] == 0:
                    message = f"Maaf, tidak ada hauler ditemukan di site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Nama Hauler","Kelas Hauler","Jumlah Unit"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())
            else:
                total_hauler =0 
                for i in range(len(value['data'])):
                    for j in range(len(value['data'][i]['haulers'])):
                        if value['data'][i]['haulers'][j]['class_name'] != "" or value['data'][i]['haulers'][j]['class_name']!= "N/A":
                            total_hauler +=1
                message = (
                    f"Based on the latest data, there are {total_hauler} haulers working at site {site_name}. The following is a list of Haulers working on site {site_name}:\n"                      
                )
                cnt= 0 
                for i in range(len(value['data'])):
                    for j in range(len(value['data'][i]['haulers'])):
                        if value['data'][i]['haulers'][j]['class_name']!= "" or value['data'][i]['haulers'][j]['class_name']!= "N/A":
                            table_data.append([f"{cnt+1}", f"{value['data'][i]['haulers'][j]['equipment_type_name']}", f"{value['data'][i]['haulers'][j]['class_name']}", f"{value['data'][i]['haulers'][j]['amount']}"])
                            cnt +=1
                            
                if value['total'] == 0:
                    message = f"Sorry, no haulers found on site {site_name}."
                
                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Hauler Name","Hauler Class","Number of Units"], data= table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("site_name",None)]

class ActionGetFMSTotalEquipmentBySiteFleet(Action):
    def name(self) -> str:
        return "action_get_fms_total_equipment_by_site_fleet"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        equipment_site_name = tracker.get_slot("equipment_site_name")
        value = None
        if token_fms is not None :
            value = get_all_fleet_setting_fms(token_fms,"limit_site",["", equipment_site_name])
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                total =0 
                for i in range(len(value['data'])):
                    total += len(value['data'][i]['equipments'])
                if total > 0:
                    message = (
                        f"Berdasarkan data terkini, terdapat **{total}** equipment yang bekerja pada site {equipment_site_name}.\nBerikut adalah daftar equipment yang bekerja pada site {equipment_site_name}: \n"                  
                    )
                    cnt = 0
                    for i in range(len(value['data'])):
                        for j in range(len(value['data'][i]['equipments'])):
                            if value['data'][i]['equipments'][j]:
                                table_data.append([f"{cnt+1}", f"{value['data'][i]['equipments'][j]['name']}", f"{value['data'][i]['equipments'][j]['type']}"])
                                cnt+=1
                else:
                    message = f"Maaf, tidak ada equipment ditemukan di site {equipment_site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Nama Equipment","Tipe Equiment"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                total =0 
                for i in range(len(value['data'])):
                    total += len(value['data'][i]['equipments'])
                if total >0 :
                    message = (
                        f"Based on the latest data, there are {total} equipments working at site {equipment_site_name}. The following is a list of equipment that works on site {equipment_site_name}:\n"                      
                    )
                    cnt = 0
                    for i in range(len(value['data'])):
                        for j in range(len(value['data'][i]['equipments'])):
                            if value['data'][i]['equipments'][j]:
                                table_data.append([f"{cnt+1}", f"{value['data'][i]['equipments'][j]['name']}", f"{value['data'][i]['equipments'][j]['type']}"])
                                cnt+=1
                else:
                    message = f"Sorry, no equipment found in site {equipment_site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Equipment Name","Equipment Type"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("equipment_site_name",None)]

class ActionAskEquipmentSiteName(Action):
    def name(self):
        return "action_ask_equipment_site_name"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "Di site mana Anda ingin mengetahui jumlah equipment yang bekerja? Mohon sebutkan nama atau ID site, contohnya: 001A, 001D, atau 001M")
        else:
            dispatcher.utter_message(text = "At which site would you like to know the number of equipment in operation? Please state the name or site ID, for example: 001A, 001D, or 001M")
        return []
    
class ActionGetFMSTargetProductionBySite(Action):
    def name(self) -> str:
        return "action_get_fms_target_production_by_site"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        value = None
        if token_fms is not None :
            value = get_all_fleet_setting_fms(token_fms,"search_site",["", site_name])
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Berikut adalah target produksi tiap fleet pada site {site_name}: \n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['productivity_target']['value']} {value['data'][i]['productivity_target']['unit']}"])

                if value['total'] == 0:
                    message = f"Maaf, tidak ada target produksi fleet ditemukan di site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Nama Fleet","Target Produksi"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"The following is the production target for each fleet at site {site_name}: \n "                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['productivity_target']['value']} {value['data'][i]['productivity_target']['unit']}"])

                if value['total'] == 0:
                    message = f"Sorry, no production target found in site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Fleet Name","Production Target"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("site_name",None)]

class ActionGetFMSMachFactorBySite(Action):
    def name(self) -> str:
        return "action_get_fms_mach_factor_by_site"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        value = None
        if token_fms is not None :
            value = get_all_fleet_setting_fms(token_fms,"search_site",["", site_name])
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Match factor untuk tiap fleet pada site {site_name} saat ini adalah sebagai berikut: \n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['matching_fleet']}"])

                if value['total'] == 0:
                    message = f"Maaf, tidak ada match factor fleet ditemukan di site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Nama Fleet","Match Factor"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"The match factor for each fleet at the {site_name} site is currently as follows: \n "                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['matching_fleet']}"])

                if value['total'] == 0:
                    message = f"Sorry, no match factor found in site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Fleet Name","Match Factor"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("site_name",None)]

class ActionGetFMSHaulTimeBySite(Action):
    def name(self) -> str:
        return "action_get_fms_haul_time_by_site"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        value = None
        if token_fms is not None :
            value = get_all_fleet_setting_fms(token_fms,"search_site",["", site_name])
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Durasi hauling untuk setiap fleet di site {site_name} adalah sebagai berikut: \n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['haul_time']}"])

                if value['total'] == 0:
                    message = f"Maaf, tidak ada haul time ditemukan di site {site_name}."
                
                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Nama Fleet","Durasi Hauling (Menit)"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"The hauling duration for each fleet at the {site_name} site is as follows: \n "                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['haul_time']}"])
            
                if value['total'] == 0:
                    message = f"Sorry, no haul time found in site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Fleet Name","Hauling Duration (Minutes)"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("site_name",None)]

class ActionGetFMSDumpTimeBySite(Action):
    def name(self) -> str:
        return "action_get_fms_dump_time_by_site"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        value = None
        if token_fms is not None :
            value = get_all_fleet_setting_fms(token_fms,"search_site",["", site_name])
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Durasi dumping untuk setiap fleet di site {site_name} adalah sebagai berikut: \n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['dump_time']}"])

                if value['total'] == 0:
                    message = f"Maaf, tidak ada dump time ditemukan di site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Nama Fleet","Durasi Dumping (Menit)"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"The dumping duration for each fleet at the {site_name} site is as follows: \n "                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['dump_time']}"])
     
                if value['total'] == 0:
                    message = f"Sorry, no dump time found in site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Fleet Name","Dumping Duration (Minutes)"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("site_name",None)]
    
class ActionGetFMSSpotTimeBySite(Action):
    def name(self) -> str:
        return "action_get_fms_spot_time_by_site"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        value = None
        if token_fms is not None :
            value = get_all_fleet_setting_fms(token_fms,"search_site",["", site_name])
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Durasi Spotting untuk setiap fleet di site {site_name} adalah sebagai berikut:\n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['spot_time']}"])
  
                if value['total'] == 0:
                    message = f"Maaf, tidak ada spot time ditemukan di site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Nama Fleet","Durasi Spotting (Menit)"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"Spotting duration for each fleet on site {site_name} is as follows: \n "                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['spot_time']}"])

                if value['total'] == 0:
                    message = f"Sorry, no spot time found in site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Fleet Name","Spotting Duration (Minutes)"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("site_name",None)]
    
class ActionGetFMSLoaderCycleTimeBySite(Action):
    def name(self) -> str:
        return "action_get_fms_loader_cycle_time_by_site"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        value = None
        if token_fms is not None :
            value = get_all_fleet_setting_fms(token_fms,"search_site",["", site_name])
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Durasi siklus loader untuk setiap fleet di site {site_name} adalah sebagai berikut:\n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['loader_cycle_time']}"])

                if value['total'] == 0:
                    message = f"Maaf, tidak ada durasi siklus loader ditemukan di site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Nama Fleet","Durasi Siklus Loader (Menit)"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"The loader cycle duration for each fleet at site {site_name} is as follows \n "                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['loader_cycle_time']}"])
   
                if value['total'] == 0:
                    message = f"Sorry, no loader cycle duration found in site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Fleet Name","Loader Cycle Duration (Minutes)"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("site_name",None)]
    
class ActionGetFMSReturnTimeBySite(Action):
    def name(self) -> str:
        return "action_get_fms_return_time_by_site"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        value = None
        if token_fms is not None :
            value = get_all_fleet_setting_fms(token_fms,"search_site",["", site_name])
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Durasi return untuk setiap fleet di site {site_name} adalah sebagai berikut:\n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['return_time']}"])
     
                if value['total'] == 0:
                    message = f"Maaf, tidak ada return time ditemukan di site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Nama Fleet","Waktu Return (Menit)"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"The return duration for each fleet at the {site_name} site is as follows: \n "                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['return_time']}"])

                if value['total'] == 0:
                    message = f"Sorry, no return time found on site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Fleet Name","Return Time (Minutes)"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("site_name",None)]

class ActionGetFMSTotalProductionBySite(Action):
    def name(self) -> str:
        return "action_get_fms_total_production_by_site"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        value = None
        if token_fms is not None :
            value = get_all_fleet_setting_fms(token_fms,"search_site",["", site_name])
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Jumlah produksi untuk tiap fleet pada site {site_name} adalah sebagai berikut: \n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['excavator_productivity_actual']['value']} {value['data'][i]['excavator_productivity_actual']['unit']}"])

                if value['total'] == 0:
                    message = f"Maaf, tidak ada produksi ditemukan di site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Nama Fleet","Jumlah Produksi"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"The production quantities for each fleet at site {site_name} are as follows: \n "                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['excavator_productivity_actual']['value']} {value['data'][i]['excavator_productivity_actual']['unit']}"])

                if value['total'] == 0:
                    message = f"Sorry, no production number found in site {site_name}."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Fleet Name","Production Quantity"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("site_name",None)]

class ActionGetFMSProductionPerCycle(Action):
    def name(self) -> str:
        return "action_get_fms_production_per_cycle"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        value = None
        if token_fms is not None :
            value = get_all_fleet_setting_fms(token_fms,"search_site",["", site_name])
        if value is not None:
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Jumlah produksi untuk tiap fleet pada site {site_name} dalam satu cycle adalah sebagai berikut: \n"                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['excavator_production_cycle']['value']} {value['data'][i]['excavator_production_cycle']['unit']}"])
    
                if value['total'] == 0:
                    message = f"Maaf, tidak ada produksi ditemukan di site {site_name} dalam satu cycle."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Nama Fleet","Jumlah Produksi"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"The production quantity for each fleet at the {site_name} site in one cycle is as follows: \n "                        
                )
                for i in range(len(value['data'])):
                    table_data.append([f"{i+1}", f"{value['data'][i]['excavator_code']}", f"{value['data'][i]['excavator_production_cycle']['value']} {value['data'][i]['excavator_production_cycle']['unit']}"])

                if value['total'] == 0:
                    message = f"Sorry, no production was found on site {site_name} in one cycle."

                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Fleet Name","Production Quantity"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("site_name",None)]
     
class ActionGetFMSTop10Equipment(Action):
    def name(self) -> str:
        return "action_get_fms_top10_equipment"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logging.info(f'Executing action : {self.name}')
        language = tracker.get_slot("language") or "indonesia"
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        category_name = tracker.get_slot("equipment_category")
        logger.info(f"Kategori: {category_name}")
        
        if not token_fms:
            dispatcher.utter_message(text="Token FMS tidak tersedia. Mohon coba lagi nanti.")
            return []
        
        category_map = {
            "jam operasional": ("hm", "Jam operasional"),
            "jarak tempuh": ("km", "Jarak Tempuh"),
            "kapasitas": ("capacity", "Kapasitas"),
            "operating hours": ("hm", "Operating Hours"),
            "distance traveled": ("km", "Distance Traveled"),
            "capacity": ("capacity", "Capacity")
        }
        
        try:
            key, label = category_map[category_name.lower()]     
        except KeyError:
            key, label = "count", "Total"

        value = get_all_equipments_fms(token_fms, "top10", site_name)
        if value is None or "units" not in value:
            dispatcher.utter_message(
                text=f"Maaf, tidak ada data equipment ditemukan untuk site {site_name}."
            )
            return [SlotSet("site_name", None), SlotSet("equipment_category", None)]
        
        equipment_list = value["units"]
        count = {}
        for unit in equipment_list:
            try:
                count[unit['unit_name']]['count'] += 1
            except KeyError:
                count[unit['unit_name']] = {'hm': unit['hm'], 'km': unit['km'], 'count': 1, 'capacity': unit['capacity'], 'equipment_category_name': unit['equipment_category_name']}
            except TypeError:
                continue

        if key == "hm":
            value = sorted(count, key= lambda x : count[x].get('hm', 0), reverse=True)
        elif key == "km":
            value = sorted(count, key= lambda x : count[x].get('km', 0), reverse=True)
        elif key == "capacity":
            value = sorted(count, key= lambda x : count[x].get('capacity', 0), reverse=True)
        else:
            value = sorted(count, key= lambda x : count[x].get('count', 0), reverse=True)
        
        if not count:
            dispatcher.utter_message(
                text=f"Maaf, tidak ada equipment ditemukan untuk site {site_name} pada kategori {label}."
            )
            return [SlotSet("site_name", None), SlotSet("equipment_category", None)]
        
        doc = snakemd.Document()
        table_data = []
        if language == "indonesia":
            message = f"Berikut adalah 10 equipment dengan {label} tertinggi untuk site {site_name}:\n"
            for i, equipment in enumerate(value[:10], start=1):
                table_data.append([f"{i}", f"{equipment}", f"{count[equipment].get('equipment_category_name', 'Tidak diketahui')}", f"{count[equipment].get(key, 'Tidak diketahui'):.2f}"])
                if i == 10:
                    break
            dispatcher.utter_message(text=message) 
            doc.add_table(header=["No","Kode Equipment","Kategori",f"{label}"], data=table_data)
            dispatcher.utter_message(text=(doc.__str__()))

        else:
            message = f"Here are the top 10 equipment with the highest {label} for site {site_name}:\n"
            for i, equipment in enumerate(value[:10], start=1):
                table_data.append([f"{i}", f"{equipment}", f"{count[equipment].get('equipment_category_name', 'Tidak diketahui')}", f"{count[equipment].get(key, 'Tidak diketahui'):.2f}"])
                if i == 10:
                    break
            dispatcher.utter_message(text=message) 
            doc.add_table(header=["No","Equipment Code","Category",f"{label}"], data=table_data)
            dispatcher.utter_message(text=(doc.__str__()))

        equipment_names = [equipment for equipment in value[:10]]
        equipment_values = [
            np.nan_to_num(count[equipment].get(key, 0))  
            for equipment in value[:10]
        ]

        logger.info(f"Equipment Names: {equipment_names}")
        logger.info(f"Equipment Values: {equipment_values}")

        if all(value == 0 for value in equipment_values):
            if language == "indonesia":
                dispatcher.utter_message(text="Tidak ada data yang valid untuk ditampilkan.")
            else: 
                dispatcher.utter_message(text="There is no valid data to display.")
            return [SlotSet("site_name", None), SlotSet("equipment_category", None)]

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(equipment_values, labels=equipment_names, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
        ax.set_xlabel(label)
        ax.set_title(f"Top 10 Equipment for {site_name}")

        image_stream = io.BytesIO()
        fig.savefig(image_stream, format='png')
        image_stream.seek(0)  

        image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')
        
        dispatcher.utter_message(text="Berikut adalah grafik untuk Top 10 equipment:") if language == "indonesia" else dispatcher.utter_message(text="Here is the plot for the top 10 equipment:")
        dispatcher.utter_message(text=f"![Top 10](data:image/png;base64,{image_base64})")

        return [SlotSet("site_name", None), SlotSet("equipment_category", None)]

class ActionGetFMSRequestTop10Equipment(Action):
    def name(self) -> str:
        return "action_get_fms_request_top10_equipment"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logging.info(f'Executing action : {self.name}')
        language = tracker.get_slot("language") or "indonesia"
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        category_name = tracker.get_slot("category_name")
        equipment_top10_category = tracker.get_slot("equipment_top10_category")
        logger.info(f"Kategori: {category_name}")
        logger.info(f"Kategori Top 10: {equipment_top10_category}")
        
        if not token_fms:
            dispatcher.utter_message(text="Token FMS tidak tersedia. Mohon coba lagi nanti.")
            return []
        
        category_map = {
            "jam operasional": ("hm", "Jam Operasional"),
            "jarak tempuh": ("km", "Jarak Tempuh"),
            "kapasitas": ("capacity", "Kapasitas"),
            "operating hours": ("hm", "Operating Hours"),
            "distance traveled": ("km", "Distance Traveled"),
            "capacity": ("capacity", "Capacity")
        }
        
        try:
            key, label = category_map[equipment_top10_category.lower()]     
        except KeyError:
            key,label = "count", "Total"
        
        value = get_all_equipments_fms(token_fms, "top10", site_name)
        if value is None or "units" not in value:
            dispatcher.utter_message(
                text=f"Maaf, tidak ada data equipment ditemukan untuk site {site_name}."
            )
                    
        equipment_list = value["units"]
        count = {}
        for unit in equipment_list:
            try:
                # count[unit['code']]['hm'] = unit['hm']
                # count[unit['code']]['km'] = unit['km']
                count[unit['unit_name']]['count'] +=1
                # count[unit['capacity']]['capacity'] = unit['capacity']
            except KeyError:
                count[unit['unit_name']] = {'hm': unit['hm'], 'km': unit['km'], 'count': 1, 'capacity': unit['capacity'], 'equipment_category_name': unit['equipment_category_name']}
            except TypeError:
                continue

        if key == "hm":
            value = sorted(count, key= lambda x : count[x].get('hm', 0), reverse=True)
        elif key == "km":
            value = sorted(count, key= lambda x : count[x].get('km', 0), reverse=True)
        elif key == "capacity":
            value = sorted(count, key= lambda x : count[x].get('capacity', 0), reverse=True)
        else:
            value = sorted(count, key= lambda x : count[x].get('count', 0), reverse=True)
        
        if not count:
            dispatcher.utter_message(
                text=f"Maaf, tidak ada equipment ditemukan untuk site {site_name} pada kategori {label}."
            )
            return [SlotSet("site_name", None), SlotSet("equipment_top10_category", None)]
        
        doc = snakemd.Document()
        table_data = []
        if language == "indonesia":
            message = f"Berikut adalah 10 equipment dengan {label} tertinggi untuk site {site_name}:\n"
            for i, equipment in enumerate(value, start=1):
                table_data.append([f"{i}", f"{equipment}", f"{count[equipment].get('equipment_category_name', 'Tidak diketahui')}", f"{count[equipment].get(key, 'Tidak diketahui')}"])
                if i ==10:
                    break
            dispatcher.utter_message(text=message) 
            doc.add_table(header=["No","Kode Equipment","Kategori",f"{label}"], data=table_data)
            dispatcher.utter_message(text=(doc.__str__()))

        else:
            message = f"Here are the top 10 equipment with the highest {label} for site {site_name}:\n"
            for i, equipment in enumerate(value, start=1):
                table_data.append([f"{i}", f"{equipment}", f"{count[equipment].get('equipment_category_name', 'Tidak diketahui')}", f"{count[equipment].get(key, 'Tidak diketahui')}"])
                if i ==10:
                    break
            dispatcher.utter_message(text=message) 
            doc.add_table(header=["No","Equipment Code","Category",f"{label}"], data=table_data)
            dispatcher.utter_message(text=(doc.__str__()))

        equipment_names = [equipment for equipment in value[:10]]
        equipment_values = [
            np.nan_to_num(count[equipment].get(key, 0))  
            for equipment in value[:10]
        ]

        logger.info(f"Equipment Names: {equipment_names}")
        logger.info(f"Equipment Values: {equipment_values}")

        if all(value == 0 for value in equipment_values):
            dispatcher.utter_message(text="Tidak ada data yang valid untuk ditampilkan.")
            return [SlotSet("site_name", None), SlotSet("equipment_category", None)]
        
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(equipment_values, labels=equipment_names, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
        ax.set_xlabel(label)
        ax.set_title(f"Top 10 Equipment for {site_name}")

        image_stream = io.BytesIO()
        fig.savefig(image_stream, format='png')
        image_stream.seek(0)

        image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

        dispatcher.utter_message(text="Berikut adalah grafik untuk Top 10 equipment:") if language == "indonesia" else dispatcher.utter_message(text="Here is the plot for the top 10 equipment:")
        dispatcher.utter_message(text=f"![Top 10](data:image/png;base64,{image_base64})")
        
        return [SlotSet("site_name", None), SlotSet("category_name", None), SlotSet("equipment_top10_category", None)]

class ActionGetFMSTop10Fleet(Action):
    def name(self) -> str:
        return "action_get_fms_top10_fleet"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        category_name = tracker.get_slot("fleet_category")
        logger.info(f"Kategori: {category_name}")
        value = None
        if token_fms is not None:
            value = get_all_fleet_setting_fms(token_fms, "limit_site", ["", site_name])
        
        if value is not None:
            category_map = {
                "jarak tempuh": ("distance_meters", "Jarak Tempuh"),
                "muatan": ("payload", "Muatan"),
                "jam operasional": ("hour_meter", "Jam Operasional"),
                "bahan bakar": ("fuel_level", "Bahan Bakar"),
                "jumlah produksi": ("excavator_productivity_actual", "Jumlah Produksi"),
                "distance traveled": ("distance_meters", "Distance Traveled"),
                "payload": ("payload", "Payload"),
                "operating hours": ("hour_meter", "Operating Hours"),
                "fuel": ("fuel_level", "Fuel"),
                "production amount": ("excavator_productivity_actual", "Production Amount")
            }
            try:
                key, label = category_map[category_name.lower()]
            except KeyError:
                key, label = "count", "Total"

            count = {}
            for unit in value['data']:
                try:
                    count[unit['excavator_code']]['count'] += 1
                except KeyError:
                    count[unit['excavator_code']] = {
                        "distance_meters": unit['excavator_telemetry']['distance_meters'],
                        "payload": unit['excavator_telemetry']['payload'],
                        "hour_meter": unit['excavator_telemetry']['hour_meter'],
                        "fuel_level": unit['excavator_telemetry']['fuel_level'],
                        "excavator_productivity_actual": unit['excavator_productivity_actual']['value'],
                        "excavator_productivity_actual_unit": unit['excavator_productivity_actual']['unit'],
                        "excavator_type_name": unit['excavator_model']['name'],
                        "count": 0
                    }
            if key == "distance_meters":
                value = sorted(count, key=lambda x: count[x].get('distance_meters', 0) or 0, reverse=True)
            elif key == "payload":
                value = sorted(count, key=lambda x: count[x].get('payload', 0) or 0, reverse=True)
            elif key == "hour_meter":
                value = sorted(count, key=lambda x: count[x].get('hour_meter', 0) or 0, reverse=True)
            elif key == "fuel_level":
                value = sorted(count, key=lambda x: count[x].get('fuel_level', 0) or 0, reverse=True)
            elif key == "excavator_productivity_actual":
                value = sorted(count, key=lambda x: count[x].get('excavator_productivity_actual', 0) or 0, reverse=True)
            else:
                value = sorted(count, key=lambda x: count[x].get('count', 0) or 0, reverse=True)
            
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = f"Berikut adalah 10 fleet dengan {label} tertinggi untuk site {site_name}:\n"
                for i, k in enumerate(value):
                    table_data.append([f"{i+1}", f"{k}", f"{count[k]['excavator_type_name']}", f"{count[k].get(key, 'Tidak diketahui')}"])
                    if i == 10:
                        break
                if len(value) == 0:
                    message = f"Maaf, tidak ada fleet ditemukan di site {site_name}."
                dispatcher.utter_message(text=message)
                doc.add_table(header=["No", "Kode Excavator", "Tipe Excavator", f"{label}"], data=table_data)
                dispatcher.utter_message(text=(doc.__str__()))

            else:
                message = f"Here are 10 fleets with highest {label} for site {site_name}:\n"
                for i, k in enumerate(value):
                    table_data.append([f"{i+1}", f"{k}", f"{count[k]['excavator_type_name']}", f"{count[k].get(key, 'Tidak diketahui')}"])
                    if i == 10:
                        break
                if len(value) == 0:
                    message = f"Sorry, no fleet found at site {site_name}."
                dispatcher.utter_message(text=message)
                doc.add_table(header=["No", "Excavator Code", "Excavator Type", f"{label}"], data=table_data)
                dispatcher.utter_message(text=(doc.__str__()))
            
            fleet_names = [count[k]['excavator_type_name'] for k in value[:10]]
            fleet_values = [
                np.nan_to_num(count[k].get(key, 0))
                for k in value[:10]
            ]

            if all(value == 0 for value in fleet_values):
                if language == "indonesia":
                    dispatcher.utter_message(text="Tidak ada data yang valid untuk ditampilkan.")
                else: 
                    dispatcher.utter_message(text="There is no valid data to display.")
                return [SlotSet("site_name", None), SlotSet("equipment_category", None)]
            
            logger.info(f"Fleet Names: {fleet_names}")
            logger.info(f"Fleet Values: {fleet_values}")

            fig, ax = plt.subplots(figsize=(8, 8))
            ax.pie(fleet_values, labels=fleet_names, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
            ax.set_xlabel(label)
            ax.set_title(f"Top 10 Fleets for {site_name}")
            
            image_stream = io.BytesIO()
            fig.savefig(image_stream, format='png')
            image_stream.seek(0)

            image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

            dispatcher.utter_message(text="Berikut adalah grafik untuk Top 10 fleet:") if language == "indonesia" else dispatcher.utter_message(text="Here is the plot for the top 10 fleet:")
            dispatcher.utter_message(text=f"![Top 10](data:image/png;base64,{image_base64})")

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text="Maaf, terjadi masalah saat mengakses data.")
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")

        return [SlotSet("site_name", None), SlotSet("fleet_category", None)]

class ActionGetFMSRequestTop10Fleet(Action):
    def name(self) -> str:
        return "action_get_fms_request_top10_fleet"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        category_name = tracker.get_slot("category_name")
        fleet_top10_category = tracker.get_slot("fleet_top10_category")
        logger.info(f"Kategori: {category_name}")
        logger.info(f"Kategori Top 10: {fleet_top10_category}")
        value = None
        if token_fms is not None :
            value = get_all_fleet_setting_fms(token_fms,"limit_site",["",site_name] )
        if value is not None:
            category_map = {
                "jarak tempuh": ("distance_meters", "Jarak Tempuh"),
                "muatan": ("payload", "Muatan"),
                "jam operasional": ("hour_meter", "Jam Operasional"),
                "bahan bakar": ("fuel_level", "Bahan Bakar"),
                "jumlah produksi": ("excavator_productivity_actual", "Jumlah Produksi"),
                "distance traveled": ("distance_meters", "Distance Traveled"),
                "payload": ("payload", "Payload"),
                "operating hours": ("hour_meter", "Operating Hours"),
                "fuel": ("fuel_level", "Fuel"),
                "production amount": ("excavator_productivity_actual", "Production Amount")
            }
            try:
                key, label = category_map[fleet_top10_category.lower()]     
            except KeyError:
                key, label = "count", "Total"

            count = {}
            for unit in value['data']:
                try:
                    count[unit['excavator_code']]['count']+=1
                except KeyError:
                    count[unit['excavator_code']] = {
                        "distance_meters": unit['excavator_telemetry']['distance_meters'],
                        "payload": unit['excavator_telemetry']['payload'],
                        "hour_meter": unit['excavator_telemetry']['hour_meter'],
                        "fuel_level": unit['excavator_telemetry']['fuel_level'],
                        "excavator_productivity_actual": unit['excavator_productivity_actual']['value'],
                        "excavator_productivity_actual_unit": unit['excavator_productivity_actual']['unit'],
                        "excavator_type_name" : unit['excavator_model']['name'],
                        "count" : 0
                    }
            if key == "distance_meters":
                value = sorted(count, key=lambda x: count[x].get('distance_meters', 0) or 0, reverse=True)
            elif key == "payload":
                value = sorted(count, key=lambda x: count[x].get('payload', 0) or 0, reverse=True)
            elif key == "hour_meter":
                value = sorted(count, key=lambda x: count[x].get('hour_meter', 0) or 0, reverse=True)
            elif key == "fuel_level":
                value = sorted(count, key=lambda x: count[x].get('fuel_level', 0) or 0, reverse=True)
            elif key == "excavator_productivity_actual":
                value = sorted(count, key=lambda x: count[x].get('excavator_productivity_actual', 0) or 0, reverse=True)
            else:
                value = sorted(count, key=lambda x: count[x].get('count', 0) or 0, reverse=True)
            
            doc = snakemd.Document()
            table_data = []
            if language == "indonesia":
                message = (
                    f"Berikut adalah 10 equipment dengan {label} tertinggi untuk site {site_name}:\n"                        
                )
                for i,k in enumerate(value):
                    table_data.append([f"{i+1}", f"{k}", f"{count[k]['excavator_type_name']}", f"{count[k].get(key, 'Tidak diketahui')}"])
                    if i==10:
                        break
                if len(value) == 0:
                    message = f"Maaf, tidak ada fleet ditemukan di site {site_name}."
                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Kode Excavator","Tipe Excavator",f"{label}"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            else:
                message = (
                    f"Here are 10 fleets with highest {label} for site {site_name}:\n"                        
                )
                for i,k in enumerate(value):
                    table_data.append([f"{i+1}", f"{k}", f"{count[k]['excavator_type_name']}", f"{count[k].get(key, 'Tidak diketahui')}"])
                    if i==10:
                        break
                if len(value) == 0:
                    message = f"Sorry, no fleet found at site {site_name}."
                dispatcher.utter_message(text=message) 
                doc.add_table(header=["No","Excavator Code","Excavator Type",f"{label}"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

            fleet_names = [count[k]['excavator_type_name'] for k in value[:10]]
            fleet_values = [
                np.nan_to_num(count[k].get(key, 0))
                for k in value[:10]
            ]

            if all(value == 0 for value in fleet_values):
                if language == "indonesia":
                    dispatcher.utter_message(text="Tidak ada data yang valid untuk ditampilkan.")
                else: 
                    dispatcher.utter_message(text="There is no valid data to display.")
                return [SlotSet("site_name", None), SlotSet("equipment_category", None)]

            logger.info(f"Fleet Names: {fleet_names}")
            logger.info(f"Fleet Values: {fleet_values}")

            fig, ax = plt.subplots(figsize=(8, 8))
            ax.pie(fleet_values, labels=fleet_names, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
            ax.set_xlabel(label)
            ax.set_title(f"Top 10 Fleets for {site_name}")
            
            image_stream = io.BytesIO()
            fig.savefig(image_stream, format='png')
            image_stream.seek(0)

            image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

            dispatcher.utter_message(text="Berikut adalah grafik untuk Top 10 fleet:") if language == "indonesia" else dispatcher.utter_message(text="Here is the plot for the top 10 fleet:")
            dispatcher.utter_message(text=f"![Top 10](data:image/png;base64,{image_base64})")

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        return [SlotSet("site_name",None), SlotSet("category_name", None), SlotSet("fleet_top10_category",None)]
    
class ActionGetFMSTop10Breakdown(Action):
    def name(self) -> str:
        return "action_get_fms_top10_breakdown"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        category_name = tracker.get_slot("breakdown_category")
        logger.info(f"Kategori Breakdown: {category_name}")
        value = None
        
        if token_fms is not None:
            value = get_equipment_breakdown_fms(token_fms, "", [site_name])

        if value is not None:
            category_map = {
                "penyebab breakdown": ("faults_name", "Penyebab Breakdown"),
                "sering breakdown": ("equipment_code", "Frekuensi Equipment Breakdown"),
                "breakdown causes": ("faults_name", "Breakdown Causes"),
                "frequently break down": ("equipment_code", "Equipment Breakdown Frequency")
            }
            try:
                key, label = category_map[category_name.lower()]
            except KeyError:
                dispatcher.utter_message(text="Kategori tidak ditemukan / Unknown category.")
                return [SlotSet("site_name", None), SlotSet("breakdown_category", None)]
        
            count = {}
            breakdown_causes = {}  
            downtime_details = {}  
            downtime_logs = {}  
            total_downtime = {}  

            if key == "faults_name":
                for unit in value['data']:
                    for fault in unit.get('faults', []):
                        fault_name = fault['name']
                        count[fault_name] = count.get(fault_name, 0) + 1
                sorted_breakdowns = sorted(count.items(), key=lambda x: x[1], reverse=True)

                if language == "indonesia":
                    message = f"Berikut adalah 10 Penyebab Breakdown tertinggi untuk site {site_name}:\n"
                else:
                    message = f"Here are the top 10 Breakdown Causes for site {site_name}:\n"
                
                for idx, (item, freq) in enumerate(sorted_breakdowns, 1):
                    if idx > 10:
                        break
                    message += f"{idx}. {item}: {freq}\n"
                dispatcher.utter_message(text=message)

                # Pie chart for Breakdown Causes
                breakdown_names = [item for item, _ in sorted_breakdowns[:10]]
                breakdown_values = [freq for _, freq in sorted_breakdowns[:10]]

                breakdown_values = [0 if value is None or np.isnan(value) else value for value in breakdown_values]

                if all(value == 0 for value in breakdown_values):
                    if language == "indonesia":
                        dispatcher.utter_message(text="Tidak ada data yang valid untuk ditampilkan.")
                    else: 
                        dispatcher.utter_message(text="There is no valid data to display.")
                    return [SlotSet("site_name", None), SlotSet("equipment_category", None)]

                logger.info(f"Breakdown Names: {breakdown_names}")
                logger.info(f"Breakdown Values: {breakdown_values}")

                fig, ax = plt.subplots(figsize=(8, 8))
                ax.pie(breakdown_values, labels=breakdown_names, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
                ax.set_title(f"Top 10 Breakdown Causes for {site_name}")

                image_stream = io.BytesIO()
                fig.savefig(image_stream, format='png')
                image_stream.seek(0)

                image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

                dispatcher.utter_message(text="Berikut adalah grafik untuk top 10 breakdown causes:") if language == "indonesia" else dispatcher.utter_message(text="Here is the plot for top 10 breakdown causes:")
                dispatcher.utter_message(text=f"![Top 10 Breakdown Causes](data:image/png;base64,{image_base64})")
                return [SlotSet("site_name", None), SlotSet("breakdown_category", None)]

            elif key == "equipment_code":
                for unit in value['data']:
                    eq_code = unit['equipment_code']
                    count[eq_code] = count.get(eq_code, 0) + 1

                    faults = [fault['name'] for fault in unit.get('faults', [])]
                    if eq_code not in breakdown_causes:
                        breakdown_causes[eq_code] = set()  
                    breakdown_causes[eq_code].update(faults)

                    created_at_str = unit.get('created_at', None)
                    ended_at_str = unit.get('ended_at', None)

                    if created_at_str and ended_at_str:
                        created_at = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                        ended_at = datetime.strptime(ended_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                        downtime = (ended_at - created_at).total_seconds() / 3600  
                        downtime_details[eq_code] = downtime_details.get(eq_code, 0) + downtime
                        total_downtime[eq_code] = total_downtime.get(eq_code, 0) + downtime  

                        if eq_code not in downtime_logs:
                            downtime_logs[eq_code] = []
                        downtime_logs[eq_code].append(f"From {created_at} to {ended_at} ({downtime:.2f} hours)")

                sorted_breakdowns = sorted(count.items(), key=lambda x: x[1], reverse=True)

                if language == "indonesia":
                    message = f"Berikut adalah 10 {label} tertinggi untuk site {site_name}:\n"
                    downtime_header = "\n   - Detail Downtime:\n"
                else:
                    message = f"Here are the top 10 {label} for site {site_name}:\n"
                    downtime_header = "\n   - Detail Downtime:\n"

                doc = snakemd.Document()
                table_data = []
                for idx, (item, freq) in enumerate(sorted_breakdowns, 1):
                    if idx > 10:
                        break

                    cause_text = ""
                    total_downtime_value = total_downtime.get(item, 0)

                    if key == "equipment_code":
                        all_causes = ", ".join(breakdown_causes.get(item, []))  
                        cause_text = f"Penyebab: {all_causes}" if language == "indonesia" else f" - Causes: {all_causes}"
                        detail_downtime = downtime_header
                        for log in downtime_logs.get(item, []):
                            detail_downtime += f"     * {log}\n"

                        if language == "indonesia":
                            table_data.append([f"{idx}", f"{item}", f"{freq}", f"{cause_text}", f"{total_downtime_value:.2f}"])
                        else:
                            table_data.append([f"{idx}", f"{item}", f"{freq}", f"{cause_text}", f"{total_downtime_value:.2f}"])

                if language == "indonesia":
                    dispatcher.utter_message(text=message)
                    doc.add_table(header=["No", "Kode Equipment", "Frekuensi Breakdown", "Penyebab", "Total Durasi Downtime (Jam)"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())
                else:
                    dispatcher.utter_message(text=message)
                    doc.add_table(header=["No", "Equipment Code", "Breakdown Frequency", "Causes", "Total Downtime Duration (Hours)"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())

                # Bar chart for equipment breakdown frequencies
                breakdown_names = [item for item, _ in sorted_breakdowns[:10]]  
                breakdown_values = [freq for _, freq in sorted_breakdowns[:10]]  

                breakdown_values = [0 if value is None or np.isnan(value) else value for value in breakdown_values]

                if all(value == 0 for value in breakdown_values):
                    if language == "indonesia":
                        dispatcher.utter_message(text="Tidak ada data yang valid untuk ditampilkan.")
                    else: 
                        dispatcher.utter_message(text="There is no valid data to display.")
                    return [SlotSet("site_name", None), SlotSet("equipment_category", None)]
                
                logger.info(f"Breakdown Names: {breakdown_names}")
                logger.info(f"Breakdown Values: {breakdown_values}")

                fig, ax = plt.subplots(figsize=(8, 8))
                ax.pie(breakdown_values, labels=breakdown_names, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
                ax.set_xlabel("Frequency of Breakdown")
                ax.set_title(f"Top 10 Equipment Breakdown Frequencies for {site_name}")

                image_stream = io.BytesIO()
                fig.savefig(image_stream, format='png')
                image_stream.seek(0)

                image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

                dispatcher.utter_message(text="Berikut adalah grafik untuk top 10 equipment breakdown:") if language == "indonesia" else dispatcher.utter_message(text="Here is the plot for top 10 equipment breakdown:")
                dispatcher.utter_message(text=f"![Top 10 Equipment Breakdown](data:image/png;base64,{image_base64})")

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text="Maaf, terjadi masalah saat mengakses data.")
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        
        return [SlotSet("site_name", None), SlotSet("breakdown_category", None)]
    
class ActionGetFMSRequestTop10Breakdown(Action):
    def name(self) -> str:
        return "action_get_fms_request_top10_breakdown"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        category_name = tracker.get_slot("category_name")
        breakdown_top10_category = tracker.get_slot("breakdown_top10_category")
        logger.info(f"Kategori: {category_name}")
        logger.info(f"Kategori Top 10: {breakdown_top10_category}")
        value = None
        if token_fms is not None :
            value = get_equipment_breakdown_fms(token_fms,"", [site_name] )

        if value is not None:
            category_map = {
                "penyebab breakdown": ("faults_name", "Penyebab Breakdown"),
                "sering breakdown": ("equipment_code", "Frekuensi Equipment Breakdown"),
                "breakdown causes": ("faults_name", "Breakdown Causes"),
                "frequently break down": ("equipment_code", "Equipment Breakdown Frequency")
            }
            try:
                key, label = category_map[breakdown_top10_category.lower()]
            except KeyError:
                dispatcher.utter_message(text="Kategori tidak ditemukan/ Unknown category")
                return [SlotSet("site_name",None), SlotSet("breakdown_top10_category",None)]
            
            count = {}
            breakdown_causes = {}
            downtime_details = {}
            downtime_logs = {}
            total_downtime = {}

            if key == "faults_name":
                for unit in value['data']:
                    for fault in unit.get('faults', []):
                        fault_name = fault['name']
                        count[fault_name] = count.get(fault_name, 0) + 1
                sorted_breakdowns = sorted(count.items(), key=lambda x: x[1], reverse=True)

                if language == "indonesia":
                    message = f"Berikut adalah 10 Penyebab Breakdown tertinggi untuk site {site_name}:\n"
                else:
                    message = f"Here are the top 10 Breakdown Causes for site {site_name}:\n"
                
                for idx, (item, freq) in enumerate(sorted_breakdowns, 1):
                    if idx > 10:
                        break
                    message += f"{idx}. {item}: {freq}\n"
                dispatcher.utter_message(text=message)

                breakdown_names = [item for item, _ in sorted_breakdowns[:10]]
                breakdown_values = [freq for _, freq in sorted_breakdowns[:10]]

                breakdown_values = [0 if value is None or np.isnan(value) else value for value in breakdown_values]

                if all(value == 0 for value in breakdown_values):
                    if language == "indonesia":
                        dispatcher.utter_message(text="Tidak ada data yang valid untuk ditampilkan.")
                    else: 
                        dispatcher.utter_message(text="There is no valid data to display.")
                    return [SlotSet("site_name", None), SlotSet("equipment_category", None)]

                logger.info(f"Breakdown Names: {breakdown_names}")
                logger.info(f"Breakdown Values: {breakdown_values}")
                
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.pie(breakdown_values, labels=breakdown_names, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
                ax.set_title(f"Top 10 Breakdown Causes for {site_name}")

                image_stream = io.BytesIO()
                fig.savefig(image_stream, format='png')
                image_stream.seek(0)

                image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

                dispatcher.utter_message(text="Berikut adalah grafik untuk top 10 breakdown causes:") if language == "indonesia" else dispatcher.utter_message(text="Here is the plot for top 10 breakdown causes:")
                dispatcher.utter_message(text=f"![Top 10 Breakdown Causes](data:image/png;base64,{image_base64})")
                return [SlotSet("site_name", None), SlotSet("breakdown_category", None)]
            
            elif key == "equipment_code":
                for unit in value['data']:
                    eq_code = unit['equipment_code']
                    count[eq_code] = count.get(eq_code, 0) + 1

                    faults = [fault['name'] for fault in unit.get('faults', [])]
                    if eq_code not in breakdown_causes:
                        breakdown_causes[eq_code] = set()  
                    breakdown_causes[eq_code].update(faults)

                    created_at_str = unit.get('created_at', None)
                    ended_at_str = unit.get('ended_at', None)
                    
                    if created_at_str and ended_at_str:
                        created_at = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                        ended_at = datetime.strptime(ended_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                        downtime = (ended_at - created_at).total_seconds() / 3600  
                        downtime_details[eq_code] = downtime_details.get(eq_code, 0) + downtime
                        total_downtime[eq_code] = total_downtime.get(eq_code, 0) + downtime  

                        if eq_code not in downtime_logs:
                            downtime_logs[eq_code] = []
                        downtime_logs[eq_code].append(f"From {created_at} to {ended_at} ({downtime:.2f} hours)")

                sorted_breakdowns = sorted(count.items(), key=lambda x: x[1], reverse=True)

                if language == "indonesia":
                    message = f"Berikut adalah 10 {label} tertinggi untuk site {site_name}:\n"
                    # downtime_header = "\n   - Detail Downtime:\n"
                else:
                    message = f"Here are the top 10 {label} for site {site_name}:\n"
                    # downtime_header = "\n   - Downtime Details:\n"
            
                doc =snakemd.Document()
                table_data = []
                for idx, (item, freq) in enumerate(sorted_breakdowns, 1):
                    if idx > 10:
                        break
                    
                    cause_text = ""
                    total_downtime_value = total_downtime.get(item, 0)

                    if key == "equipment_code":
                        all_causes = ", ".join(breakdown_causes.get(item, []))  
                        cause_text = f"Penyebab: {all_causes}" if language == "indonesia" else f" - Causes: {all_causes}"
                        # detail_downtime = downtime_header
                        # for log in downtime_logs.get(item, []):
                        #     detail_downtime += f"     * {log}\n"

                        if language == "indonesia":
                            table_data.append([f"{idx}", f"{item}", f"{freq}", f"{cause_text}", f"{total_downtime_value:.2f}"])
                        else:
                            table_data.append([f"{idx}", f"{item}", f"{freq}", f"{cause_text}", f"{total_downtime_value:.2f}"])
                
                if language == "indonesia":
                    dispatcher.utter_message(text=message)
                    doc.add_table(header=["No","Kode Equipment","Frekuensi Breakdown","Penyebab","Total Durasi Downtime (Jam)"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())
                else:
                    dispatcher.utter_message(text=message)
                    doc.add_table(header=["No","Equipment Code","Breakdown Frequency","Causes","Total Downtime Duration (Hours)"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())

                breakdown_names = [item for item, _ in sorted_breakdowns[:10]]
                breakdown_values = [freq for _, freq in sorted_breakdowns[:10]]

                breakdown_values = [0 if value is None or np.isnan(value) else value for value in breakdown_values]

                if all(value == 0 for value in breakdown_values):
                    if language == "indonesia":
                        dispatcher.utter_message(text="Tidak ada data yang valid untuk ditampilkan.")
                    else: 
                        dispatcher.utter_message(text="There is no valid data to display.")
                    return [SlotSet("site_name", None), SlotSet("equipment_category", None)]
                
                logger.info(f"Breakdown Names: {breakdown_names}")
                logger.info(f"Breakdown Values: {breakdown_values}")
                
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.pie(breakdown_values, labels=breakdown_names, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
                ax.set_xlabel("Frequency of Breakdown")
                ax.set_title(f"Top 10 Equipment Breakdown Frequencies for {site_name}")

                image_stream = io.BytesIO()
                fig.savefig(image_stream, format='png')
                image_stream.seek(0)

                image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

                dispatcher.utter_message(text="Berikut adalah grafik untuk top 10 equipment breakdown:") if language == "indonesia" else dispatcher.utter_message(text="Here is the plot for top 10 equipment breakdown:")
                dispatcher.utter_message(text=f"![Top 10 Equipment Breakdown](data:image/png;base64,{image_base64})")
  
        if language == "indonesia" and value is None:
            dispatcher.utter_message(text= "Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        
        return [SlotSet("site_name",None), SlotSet("category_name", None), SlotSet("breakdown_top10_category",None)]
    
class ActionAskEquipmentCategory(Action):
    def name(self) -> Text:
        return "action_ask_equipment_category"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(
                text="Apa kategori equipment yang ingin Anda lihat dengan nilai tertinggi?",
                buttons=[
                    {"title": "Jam Operasional", "payload": 'jam operasional'},
                    {"title": "Jarak Tempuh", "payload": 'jarak tempuh'},
                    {"title": "Kapasitas", "payload": 'kapasitas'}
                ]
            )
            json_message= {
                    "text": "Pilih kelanjutan proses "
                }
        else:
            dispatcher.utter_message(
                text="What equipment categories would you like to see with the highest scores?",
                buttons=[
                    {"title": "Operating Hours", "payload": 'operating hours'},
                    {"title": "Distance Traveled", "payload": 'distance traveled'},
                    {"title": "Capacity", "payload": 'capacity'},
                ]
            )
            json_message= {
                    "text": "Choose the next action "
                }

        return []
    
class ActionAskFleetCategory(Action):
    def name(self):
        return "action_ask_fleet_category"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(
                text="Apa kategori fleet yang ingin Anda lihat dengan nilai tertinggi?",
                buttons=[
                    {"title": "Jarak Tempuh", "payload": 'jarak tempuh'},
                    {"title": "Muatan", "payload": 'muatan'},
                    {"title": "Jam Operasional", "payload": 'jam operasional'},
                    {"title": "Sisa Bahan Bakar", "payload": 'bahan bakar'},
                    {"title": "Jumlah Produksi", "payload": 'jumlah produksi'},
                ]
            )
            json_message= {
                    "text": "Pilih kelanjutan proses "
                }
        else:
            dispatcher.utter_message(
                text="What fleet category would you like to see with the highest scores?",
                buttons=[
                    {"title": "Distance Traveled", "payload": 'distance traveled'},
                    {"title": "Payload", "payload": 'payload'},
                    {"title": "Operating Hours", "payload": 'operating hours'},
                    {"title": "Remaining Fuel", "payload": 'fuel'},
                    {"title": "Production Amount", "payload": 'production amount'},
                ]
            )
            json_message= {
                    "text": "Choose the next action "
                }
    
class ActionAskBreakdownCategory(Action):
    def name(self):
        return "action_ask_breakdown_category"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(
                text="Apa kategori breakdown yang ingin Anda lihat dengan nilai tertinggi?",
                buttons=[
                    {"title": "Penyebab Breakdown", "payload": 'penyebab breakdown'},
                    {"title": "Equipment Breakdown", "payload": 'sering breakdown'}
                ]
            )
            json_message= {
                    "text": "Pilih kelanjutan proses "
                }
        else:
            dispatcher.utter_message(
                text="What breakdown category would you like to see with the highest scores?",
                buttons=[
                    {"title": "Breakdown Cause", "payload": 'breakdown causes'},
                    {"title": "Breakdown Equipment", "payload": 'frequently break down'},
                ]
            )
            json_message= {
                    "text": "Choose the next action "
                }
        return []

class ActionAskDateProductionPerformanceControl(Action):
    def name(self):
        return "action_ask_date_production_performance_control"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        message = MessageSchema("options")


        if language == "indonesia":
            message_date_picker = MessageDatePicker("Tanggal Production Performance Control")
            message.add_date_picker(message_date_picker)
            dispatcher.utter_message(text = "Silakan masukkan tanggal. Harap gunakan format YYYY-mm-dd, contoh: 2024-12-01",json_message=message.to_dict())
        else:
            message_date_picker = MessageDatePicker("Date Production Performance Control")
            message.add_date_picker(message_date_picker)
            dispatcher.utter_message(text = "Please enter the date. Use the format YYYY-mm-dd, for example: 2024-12-01",json_message=message.to_dict())
        return []

class ActionAskDateDailyReport(Action):
    def name(self):
        return "action_ask_date_daily_report"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "masukkan tanggal")
        else:
            dispatcher.utter_message(text = "input date")
        return []
    
class ActionAskManufactureDailyReport(Action):
    def name(self):
        return "action_ask_manufacture_daily_report"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "masukkan manufacture")
        else:
            dispatcher.utter_message(text = "input manufacture")
        return []
    
class ActionAskModelDailyReport(Action):
    def name(self):
        return "action_ask_model_daily_report"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "masukkan model")
        else:
            dispatcher.utter_message(text = "input model")
        return []
    
class ActionAskCompDescDailyReport(Action):
    def name(self):
        return "action_ask_comp_desc_daily_report"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "masukkan component description")
        else:
            dispatcher.utter_message(text = "input component description")
        return []
    
class ActionAskStatusProcessDailyReport(Action):
    def name(self):
        return "action_ask_status_process_daily_report"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "masukkan status process")
        else:
            dispatcher.utter_message(text = "input status process")
        return []
    
class ActionAskSearchDailyReport(Action):
    def name(self):
        return "action_ask_search_daily_report"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "masukkan search")
        else:
            dispatcher.utter_message(text = "input search")
        return []