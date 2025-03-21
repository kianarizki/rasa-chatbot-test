from typing import Text, Any, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction
import locale
import requests
import jwt
from babel.dates import format_datetime
import logging
import snakemd
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta, date, timezone
from actions.services.fms.api  import get_all_equipments_fms, get_fms_token, get_fms_production_performance_control

logger = logging.getLogger(__name__)

class ActionGetFMSProductionWasteByDateShift(Action):
    def name(self) -> str:
        return "action_get_fms_production_waste_by_date_shift"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info(f"Executing {self.name} ")
        
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        date_slot = tracker.get_slot("date_production_performance_control")
        shift_name = tracker.get_slot("shift_name")
        value = None
        
        if token_fms is not None:
            value = get_fms_production_performance_control(token_fms, "date_shift", [site_name, shift_name, date_slot])
        
        try:
            formatted_date = format_datetime(datetime.strptime(date_slot, "%Y-%m-%d"), "d MMMM yyyy", locale="id" if language == "indonesia" else "en")
        except Exception:
            formatted_date = date_slot 

        if value is not None:
            doc = snakemd.Document()
            table_data = []

            waste_actual = value['waste_production']['shiftly']['actual'] or 1500  
            waste_budget = value['waste_production']['shiftly']['budget'] or 500  

            waste_percentage = min(100, max(0, (waste_actual / waste_budget) * 100)) if waste_budget > 0 else 0

            logger.info(f"Waste Actual: {waste_actual}, Waste Budget: {waste_budget}")
            logger.info(f"Waste Percentage: {waste_percentage}%")

            # Donut chart for waste production
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.pie([waste_percentage, 100 - waste_percentage], labels=[f'{waste_percentage:.2f}%', f'{100-waste_percentage:.2f}%'], autopct='%1.1f%%', startangle=90, colors=['#ffc107', '#d6d6d6'], wedgeprops={'width': 0.4, 'edgecolor': 'w'})
            ax.text(0, 0, f'{waste_percentage:.2f}%', ha='center', va='center', fontsize=20, color='white')
            ax.set_title(f"Waste Production - {formatted_date}")

            image_stream = io.BytesIO()
            fig.savefig(image_stream, format='png')
            image_stream.seek(0)
            waste_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

            if language == "indonesia":
                message = (
                    f"Berikut adalah data Waste Production Performance Control tanggal {formatted_date} pada {shift_name} shift di site {site_name}\n"                        
                )
                message += "\nProduction Waste:"
                table_data.append(["SIP", f"{value['waste_production']['shiftly']['budget']:.2f}"])
                table_data.append(["Actual", f"{value['waste_production']['shiftly']['actual']:.2f}"])
                table_data.append(["Budget", f"{value['waste_production']['shiftly']['ratio']:.2f}"])
                doc.add_table(header=["Deskripsi", "Nilai"], data=table_data)

            else:
                message = (
                    f"Here is the Waste Production Performance Control data for {formatted_date} on the {shift_name} shift at the {site_name} site\n"                        
                )
                message += "\nProduction Waste:"
                table_data.append(["SIP", f"{value['waste_production']['shiftly']['budget']:.2f}"])
                table_data.append(["Actual", f"{value['waste_production']['shiftly']['actual']:.2f}"])
                table_data.append(["Budget", f"{value['waste_production']['shiftly']['ratio']:.2f}"])
                doc.add_table(header=["Description", "Value"], data=table_data)

            dispatcher.utter_message(text=message)
            dispatcher.utter_message(text=doc.__str__())
            dispatcher.utter_message(text=f"![Waste Production](data:image/png;base64,{waste_base64})")

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text="Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")

        return [SlotSet("site_name", None), SlotSet("date_production_performance_control", None), SlotSet("shift_name", None)]
