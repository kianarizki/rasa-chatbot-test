from typing import Text, Any, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction
import locale
import requests
import jwt
import snakemd
from babel.dates import format_datetime
import logging
from datetime import datetime, timedelta, date, timezone
from actions.services.fms.api  import get_all_equipments_fms, get_fms_token, get_fms_production_performance_control, get_equipment_breakdown_fms
from babel.dates import format_datetime
import matplotlib.pyplot as plt
import io
import base64

logger = logging.getLogger(__name__)

class ActionGetFMSProductionToday(Action):
    def name(self) -> str:
        return "action_get_fms_production_today"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info(f"Executing {self.name}")

        language = tracker.get_slot("language") or "indonesia"
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        date = datetime.now().strftime('%Y-%m-%d')

        value = None
        value_night = None
        breakdown_data = None
        if token_fms is not None:
            value = get_fms_production_performance_control(token_fms, "date_shift", [site_name, "day", date])
            value_night = get_fms_production_performance_control(token_fms, "date_shift", [site_name, "night", date])
            breakdown_data = get_equipment_breakdown_fms(token_fms, site_name, [site_name])

        try:
            formatted_date = format_datetime(datetime.strptime(date, "%Y-%m-%d"), "d MMMM yyyy", locale="id" if language == "indonesia" else "en")
        except Exception:
            formatted_date = date 

        if value is not None:
            if language == "indonesia":
                message = f"Berikut data Production Performance Control pada site {site_name} tanggal {formatted_date}\n"
                message += f"\nProduction Coal:"    
                doc = snakemd.Document()     
                header = ["Deskripsi", "Budget", "Actual", "Ratio"] 

                coal_categories = [
                    ("Coal (DS)", float(value['coal_production']['shiftly']['budget']), float(value['coal_production']['shiftly']['actual']), float(value['coal_production']['shiftly']['ratio'])),
                    ("Coal (NS)", float(value_night['coal_production']['shiftly']['budget']), float(value_night['coal_production']['shiftly']['actual']), float(value_night['coal_production']['shiftly']['ratio'])),
                    ("Coal (Daily)", float(value['coal_production']['daily']['budget']), float(value['coal_production']['daily']['actual']), float(value['coal_production']['daily']['ratio'])),
                    ("Coal (MTD)", float(value['coal_production']['month_to_date']['budget']), float(value['coal_production']['month_to_date']['actual']), float(value['coal_production']['month_to_date']['ratio'])),
                    ("Coal (YTD)", float(value['coal_production']['year_to_date']['budget']), float(value['coal_production']['year_to_date']['actual']), float(value['coal_production']['year_to_date']['ratio']))
                ]

                dispatcher.utter_message(text=message)
                doc.add_table(header=header, data=[(category, f"{budget:.2f}", f"{actual:.2f}", f"{ratio:.2f}") for category, budget, actual, ratio in coal_categories])
                dispatcher.utter_message(text=doc.__str__())

                for category, budget, actual, ratio in coal_categories:
                    coal_percentage = min(100, max(0, (actual / budget) * 100)) if budget > 0 else 0
                    logger.info(f"Coal Category: {category} | Budget: {budget:.2f} | Actual: {actual:.2f} | Coal Percentage: {coal_percentage:.2f}%")

                    fig, ax = plt.subplots(figsize=(6, 6))
                    ax.pie([coal_percentage, 100 - coal_percentage], labels=[f'{coal_percentage:.2f}%', f'{100-coal_percentage:.2f}%'], autopct='%1.1f%%', startangle=90, colors=['#28a745', '#d6d6d6'], wedgeprops={'width': 0.4, 'edgecolor': 'w'})
                    ax.text(0, 0, f'{coal_percentage:.2f}%', ha='center', va='center', fontsize=20, color='white')
                    ax.set_title(f"{category} - {formatted_date}")

                    image_stream = io.BytesIO()
                    fig.savefig(image_stream, format='png')
                    image_stream.seek(0)
                    coal_base64 = base64.b64encode(image_stream.read()).decode('utf-8')
                    dispatcher.utter_message(text=f"![{category}](data:image/png;base64,{coal_base64})")

                message = "\nProduction Waste:"
                doc = snakemd.Document()
                waste_categories = [
                    ("Waste (DS)", float(value['waste_production']['shiftly']['budget']), float(value['waste_production']['shiftly']['actual']), float(value['waste_production']['shiftly']['ratio'])),
                    ("Waste (NS)", float(value_night['waste_production']['shiftly']['budget']), float(value_night['waste_production']['shiftly']['actual']), float(value_night['waste_production']['shiftly']['ratio'])),
                    ("Waste (Daily)", float(value['waste_production']['daily']['budget']), float(value['waste_production']['daily']['actual']), float(value['waste_production']['daily']['ratio'])),
                    ("Waste (MTD)", float(value['waste_production']['month_to_date']['budget']), float(value['waste_production']['month_to_date']['actual']), float(value['waste_production']['month_to_date']['ratio'])),
                    ("Waste (YTD)", float(value['waste_production']['year_to_date']['budget']), float(value['waste_production']['year_to_date']['actual']), float(value['waste_production']['year_to_date']['ratio']))
                ]
                dispatcher.utter_message(text=message)
                doc.add_table(header=header, data=[(category, f"{budget:.2f}", f"{actual:.2f}", f"{ratio:.2f}") for category, budget, actual, ratio in waste_categories])
                dispatcher.utter_message(text=doc.__str__())

                for category, budget, actual, ratio in waste_categories:
                    waste_percentage = min(100, max(0, (actual / budget) * 100)) if budget > 0 else 0
                    logger.info(f"Waste Category: {category} | Budget: {budget:.2f} | Actual: {actual:.2f} | Waste Percentage: {waste_percentage:.2f}%")

                    fig, ax = plt.subplots(figsize=(6, 6))
                    ax.pie([waste_percentage, 100 - waste_percentage], labels=[f'{waste_percentage:.2f}%', f'{100-waste_percentage:.2f}%'], autopct='%1.1f%%', startangle=90, colors=['#ffc107', '#d6d6d6'], wedgeprops={'width': 0.4, 'edgecolor': 'w'})
                    ax.text(0, 0, f'{waste_percentage:.2f}%', ha='center', va='center', fontsize=20, color='white')
                    ax.set_title(f"{category} - {formatted_date}")

                    image_stream = io.BytesIO()
                    fig.savefig(image_stream, format='png')
                    image_stream.seek(0)
                    waste_base64 = base64.b64encode(image_stream.read()).decode('utf-8')
                    dispatcher.utter_message(text=f"![{category}](data:image/png;base64,{waste_base64})")

                message = "\nEquipment Breakdown Details:"
                doc = snakemd.Document()
                if breakdown_data and "data" in breakdown_data and breakdown_data["data"]:
                    equipment_breakdown_data = {}

                    for idx, item in enumerate(breakdown_data["data"], 1):
                        equipment_code = item.get("equipment_code", "Unknown Equipment")
                        faults = item.get("faults", [])
                        cause_list = [fault.get('name', 'Unknown Cause') for fault in faults]
                        downtime = item.get("downtime", 0)

                        if equipment_code not in equipment_breakdown_data:
                            equipment_breakdown_data[equipment_code] = {
                                "count": 0,
                                "cause_list": set(),
                                "downtime": 0.0
                            }

                        equipment_breakdown_data[equipment_code]["count"] += 1
                        equipment_breakdown_data[equipment_code]["cause_list"].update(cause_list)
                        equipment_breakdown_data[equipment_code]["downtime"] += downtime

                    equipment_breakdown_table_data = []
                    for idx, (equipment_code, data) in enumerate(equipment_breakdown_data.items(), 1):
                        causes = ", ".join(sorted(data["cause_list"]))  
                        equipment_breakdown_table_data.append([f"{idx}", f"{equipment_code}", f"{data['count']}", f"{causes}", f"{data['downtime']:.2f}"])
                    dispatcher.utter_message(text=message)
                    doc.add_table(header=["No", "Kode Equipment", "Frekuensi Kerusakan", "Penyebab", "Total Durasi Waktu Henti (Jam)"], data=equipment_breakdown_table_data)
                    dispatcher.utter_message(text=doc.__str__())
                else:
                    message += "Tidak ada data breakdown yang tercatat untuk hari ini.\n"
                    dispatcher.utter_message(text=message)

            else:  
                message = f"Here is the Production Performance Control data for site {site_name} on {formatted_date}\n"
                message += "\nProduction Coal:"
                doc = snakemd.Document()
                header = ["Description", "Budget", "Actual", "Ratio"]

                coal_categories = [
                    ("Coal (DS)", float(value['coal_production']['shiftly']['budget']), float(value['coal_production']['shiftly']['actual']), float(value['coal_production']['shiftly']['ratio'])),
                    ("Coal (NS)", float(value_night['coal_production']['shiftly']['budget']), float(value_night['coal_production']['shiftly']['actual']), float(value_night['coal_production']['shiftly']['ratio'])),
                    ("Coal (Daily)", float(value['coal_production']['daily']['budget']), float(value['coal_production']['daily']['actual']), float(value['coal_production']['daily']['ratio'])),
                    ("Coal (MTD)", float(value['coal_production']['month_to_date']['budget']), float(value['coal_production']['month_to_date']['actual']), float(value['coal_production']['month_to_date']['ratio'])),
                    ("Coal (YTD)", float(value['coal_production']['year_to_date']['budget']), float(value['coal_production']['year_to_date']['actual']), float(value['coal_production']['year_to_date']['ratio']))
                ]

                dispatcher.utter_message(text=message)
                doc.add_table(header=header, data=[(category, f"{budget:.2f}", f"{actual:.2f}", f"{ratio:.2f}") for category, budget, actual, ratio in coal_categories])
                dispatcher.utter_message(text=doc.__str__())

                for category, budget, actual, ratio in coal_categories:
                    coal_percentage = min(100, max(0, (actual / budget) * 100)) if budget > 0 else 0
                    logger.info(f"Coal Category: {category} | Budget: {budget:.2f} | Actual: {actual:.2f} | Coal Percentage: {coal_percentage:.2f}%")

                    fig, ax = plt.subplots(figsize=(6, 6))
                    ax.pie([coal_percentage, 100 - coal_percentage], labels=[f'{coal_percentage:.2f}%', f'{100-coal_percentage:.2f}%'], autopct='%1.1f%%', startangle=90, colors=['#28a745', '#d6d6d6'], wedgeprops={'width': 0.4, 'edgecolor': 'w'})
                    ax.text(0, 0, f'{coal_percentage:.2f}%', ha='center', va='center', fontsize=20, color='white')
                    ax.set_title(f"{category} - {formatted_date}")

                    image_stream = io.BytesIO()
                    fig.savefig(image_stream, format='png')
                    image_stream.seek(0)
                    coal_base64 = base64.b64encode(image_stream.read()).decode('utf-8')
                    dispatcher.utter_message(text=f"![{category}](data:image/png;base64,{coal_base64})")

                message = "\nProduction Waste:"
                doc = snakemd.Document()
                waste_categories = [
                    ("Waste (DS)", float(value['waste_production']['shiftly']['budget']), float(value['waste_production']['shiftly']['actual']), float(value['waste_production']['shiftly']['ratio'])),
                    ("Waste (NS)", float(value_night['waste_production']['shiftly']['budget']), float(value_night['waste_production']['shiftly']['actual']), float(value_night['waste_production']['shiftly']['ratio'])),
                    ("Waste (Daily)", float(value['waste_production']['daily']['budget']), float(value['waste_production']['daily']['actual']), float(value['waste_production']['daily']['ratio'])),
                    ("Waste (MTD)", float(value['waste_production']['month_to_date']['budget']), float(value['waste_production']['month_to_date']['actual']), float(value['waste_production']['month_to_date']['ratio'])),
                    ("Waste (YTD)", float(value['waste_production']['year_to_date']['budget']), float(value['waste_production']['year_to_date']['actual']), float(value['waste_production']['year_to_date']['ratio']))
                ]
                dispatcher.utter_message(text=message)
                doc.add_table(header=header, data=[(category, f"{budget:.2f}", f"{actual:.2f}", f"{ratio:.2f}") for category, budget, actual, ratio in waste_categories])
                dispatcher.utter_message(text=doc.__str__())

                for category, budget, actual, ratio in waste_categories:
                    waste_percentage = min(100, max(0, (actual / budget) * 100)) if budget > 0 else 0
                    logger.info(f"Waste Category: {category} | Budget: {budget:.2f} | Actual: {actual:.2f} | Waste Percentage: {waste_percentage:.2f}%")

                    fig, ax = plt.subplots(figsize=(6, 6))
                    ax.pie([waste_percentage, 100 - waste_percentage], labels=[f'{waste_percentage:.2f}%', f'{100-waste_percentage:.2f}%'], autopct='%1.1f%%', startangle=90, colors=['#ffc107', '#d6d6d6'], wedgeprops={'width': 0.4, 'edgecolor': 'w'})
                    ax.text(0, 0, f'{waste_percentage:.2f}%', ha='center', va='center', fontsize=20, color='white')
                    ax.set_title(f"{category} - {formatted_date}")

                    image_stream = io.BytesIO()
                    fig.savefig(image_stream, format='png')
                    image_stream.seek(0)
                    waste_base64 = base64.b64encode(image_stream.read()).decode('utf-8')
                    dispatcher.utter_message(text=f"![{category}](data:image/png;base64,{waste_base64})")

                message = "\nEquipment Breakdown Details:"
                doc = snakemd.Document()
                if breakdown_data and "data" in breakdown_data and breakdown_data["data"]:
                    equipment_breakdown_data = {}

                    for idx, item in enumerate(breakdown_data["data"], 1):
                        equipment_code = item.get("equipment_code", "Unknown Equipment")
                        faults = item.get("faults", [])
                        cause_list = [fault.get('name', 'Unknown Cause') for fault in faults]
                        downtime = item.get("downtime", 0)

                        if equipment_code not in equipment_breakdown_data:
                            equipment_breakdown_data[equipment_code] = {
                                "count": 0,
                                "cause_list": set(),
                                "downtime": 0.0
                            }

                        equipment_breakdown_data[equipment_code]["count"] += 1
                        equipment_breakdown_data[equipment_code]["cause_list"].update(cause_list)
                        equipment_breakdown_data[equipment_code]["downtime"] += downtime

                    equipment_breakdown_table_data = []
                    for idx, (equipment_code, data) in enumerate(equipment_breakdown_data.items(), 1):
                        causes = ", ".join(sorted(data["cause_list"]))  
                        equipment_breakdown_table_data.append([f"{idx}", f"{equipment_code}", f"{data['count']}", f"{causes}", f"{data['downtime']:.2f}"])
                    dispatcher.utter_message(text=message)
                    doc.add_table(header=["No", "Equipment Code", "Breakdown Frequency", "Causes", "Total Downtime Duration (Hours)"], data=equipment_breakdown_table_data)
                    dispatcher.utter_message(text=doc.__str__())
                else:
                    message += "No breakdown data recorded for today.\n"
                    dispatcher.utter_message(text=message)
        
        else:
            if language == "indonesia":
                dispatcher.utter_message(text="Maaf, terjadi masalah saat mengakses data.")
            else:
                dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        
        return [SlotSet("site_name", None), SlotSet("date", None)]
                