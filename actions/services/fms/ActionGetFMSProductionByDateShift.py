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
import matplotlib.pyplot as plt
import io
import base64

import logging
from datetime import datetime, timedelta, date, timezone

from actions.services.fms.api  import get_all_equipments_fms, get_fms_token, get_fms_production_performance_control, get_equipment_breakdown_fms

logger = logging.getLogger(__name__)
    
class ActionGetFMSProductionByDateShift(Action):
    def name(self) -> str:
        return "action_get_fms_production_by_date_shift"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info(f"Executing {self.name}")

        language = tracker.get_slot("language") or "indonesia"
        token_fms = get_fms_token(tracker)
        site_name = tracker.get_slot("site_name")
        date_slot = tracker.get_slot("date_production_performance_control")
        shift_name = tracker.get_slot("shift_name")
        value = None

        if token_fms is not None:
            value = get_fms_production_performance_control(token_fms, "date_shift", [site_name, shift_name, date_slot])
            breakdown_data = get_equipment_breakdown_fms(token_fms, site_name, [site_name])

        try:
            formatted_date = format_datetime(datetime.strptime(date_slot, "%Y-%m-%d"), "d MMMM yyyy", locale="id" if language == "indonesia" else "en")
        except Exception:
            formatted_date = date_slot 

        if value is not None:
            production_coal_data = [
                ["SIP", f"{value['coal_production']['shiftly']['budget']:.2f}"],
                ["Actual", f"{value['coal_production']['shiftly']['actual']:.2f}"],
                ["Budget", f"{value['coal_production']['shiftly']['ratio']:.2f}"]
            ]

            production_waste_data = [
                ["SIP", f"{value['waste_production']['shiftly']['budget']:.2f}"],
                ["Actual", f"{value['waste_production']['shiftly']['actual']:.2f}"],
                ["Budget", f"{value['waste_production']['shiftly']['ratio']:.2f}"]
            ]

            coal_actual = value['coal_production']['shiftly']['actual'] or 1000  
            coal_budget = value['coal_production']['shiftly']['budget'] or 300  

            waste_actual = value['waste_production']['shiftly']['actual'] or 1500  
            waste_budget = value['waste_production']['shiftly']['budget'] or 500  

            logger.info(f"Coal Actual: {coal_actual}, Coal Budget: {coal_budget}")
            logger.info(f"Waste Actual: {waste_actual}, Waste Budget: {waste_budget}")

            coal_percentage = min(100, max(0, (coal_actual / coal_budget) * 100)) if coal_budget > 0 else 0
            waste_percentage = min(100, max(0, (waste_actual / waste_budget) * 100)) if waste_budget > 0 else 0

            logger.info(f"Coal Percentage: {coal_percentage}%")
            logger.info(f"Waste Percentage: {waste_percentage}%")

            # Donut chart for Coal production
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.pie([coal_percentage, 100 - coal_percentage], labels=[f'{coal_percentage:.2f}%', f'{100-coal_percentage:.2f}%'], autopct='%1.1f%%', startangle=90, colors=['#28a745', '#d6d6d6'], wedgeprops={'width': 0.4, 'edgecolor': 'w'})
            ax.text(0, 0, f'{coal_percentage:.2f}%', ha='center', va='center', fontsize=20, color='white')
            ax.set_title(f"Coal Production - {formatted_date}")

            image_stream = io.BytesIO()
            fig.savefig(image_stream, format='png')
            image_stream.seek(0)
            coal_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

            # Donut chart for Waste production
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.pie([waste_percentage, 100 - waste_percentage], labels=[f'{waste_percentage:.2f}%', f'{100-waste_percentage:.2f}%'], autopct='%1.1f%%', startangle=90, colors=['#ffc107', '#d6d6d6'], wedgeprops={'width': 0.4, 'edgecolor': 'w'})
            ax.text(0, 0, f'{waste_percentage:.2f}%', ha='center', va='center', fontsize=20, color='white')
            ax.set_title(f"Waste Production - {formatted_date}")

            image_stream = io.BytesIO()
            fig.savefig(image_stream, format='png')
            image_stream.seek(0)
            waste_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

            if language == "indonesia":
                message = (f"Berikut data Production Performance Control tanggal {formatted_date} pada shift {shift_name} di site {site_name}\n") 
                
                message += "\nProduction Coal:"
                doc = snakemd.Document()
                doc.add_table(header=["Deskripsi", "Nilai"], data=production_coal_data)
                dispatcher.utter_message(text=message)
                dispatcher.utter_message(text=doc.__str__())

                message = "\nProduction Waste:"
                doc = snakemd.Document()
                doc.add_table(header=["Deskripsi", "Nilai"], data=production_waste_data)
                dispatcher.utter_message(text=message)
                dispatcher.utter_message(text=doc.__str__())

                dispatcher.utter_message(text=f"![Coal Production](data:image/png;base64,{coal_base64})")
                dispatcher.utter_message(text=f"![Waste Production](data:image/png;base64,{waste_base64})")

            else:
                message = (f"Here is the Production Performance Control data for {formatted_date} on the {shift_name} shift at the {site_name} site\n") 

                message += "\nProduction Coal:"
                doc = snakemd.Document()
                doc.add_table(header=["Description", "Value"], data=production_coal_data)
                dispatcher.utter_message(text=message)
                dispatcher.utter_message(text=doc.__str__())

                message = "\nProduction Waste:"
                doc = snakemd.Document()  
                doc.add_table(header=["Description", "Value"], data=production_waste_data)
                dispatcher.utter_message(text=message)
                dispatcher.utter_message(text=doc.__str__())

                dispatcher.utter_message(text=f"![Coal Production](data:image/png;base64,{coal_base64})")
                dispatcher.utter_message(text=f"![Waste Production](data:image/png;base64,{waste_base64})")

            if breakdown_data and "data" in breakdown_data:
                if breakdown_data["data"]:
                    message += f"\n- Equipment Breakdown Details: \n"
                    breakdown_downtime = {}  
                    breakdown_causes = {} 
                    downtime_logs = {}

                    for item in breakdown_data["data"]:
                        equipment_code = item.get("equipment_code", "Unknown Equipment")
                        
                        faults = item.get("faults", [])
                        cause_list = [fault.get('name', 'Unknown Cause') for fault in faults]
                        
                        created_at_str = item.get("created_at", "")
                        created_at = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%S.%fZ") if created_at_str else None

                        ended_at_str = item.get("ended_at", "")
                        ended_at = datetime.strptime(ended_at_str, "%Y-%m-%dT%H:%M:%S.%fZ") if ended_at_str else None

                        if created_at and ended_at and created_at.date().strftime("%Y-%m-%d") == date_slot:
                            if equipment_code not in breakdown_causes:
                                breakdown_causes[equipment_code] = {
                                    "causes": [],
                                    "count": 0,
                                    "downtime": 0.0
                                }

                            breakdown_causes[equipment_code]["causes"].extend(cause_list)
                            breakdown_causes[equipment_code]["count"] += 1

                            downtime = (ended_at - created_at).total_seconds() / 3600  
                            breakdown_downtime[equipment_code] = breakdown_downtime.get(equipment_code, 0) + downtime
                            
                            if equipment_code not in downtime_logs:
                                downtime_logs[equipment_code] = []
                            downtime_logs[equipment_code].append(f"From {created_at} to {ended_at} ({downtime:.2f} hours)")

                    sorted_breakdowns = sorted(breakdown_causes.items(), key=lambda x: x[1]["count"], reverse=True)

                    for idx, (equipment_code, details) in enumerate(sorted_breakdowns, 1):
                        total_downtime = breakdown_downtime.get(equipment_code, 0)  

                        all_faults = set(details["causes"])  
                        cause_text = ", ".join(all_faults)  

                        # downtime_detail = "\n   - Detail Downtime:\n"
                        # for downtime_log in downtime_logs[equipment_code]:
                        #     downtime_detail += f"     * {downtime_log}\n"

                        if language == "indonesia":
                            message += f"{idx}. {equipment_code} - Frekuensi Breakdown: {details['count']} - Penyebab: {cause_text} - Total Durasi Downtime: {total_downtime:.2f} jam\n"
                        else:
                            message += f"{idx}. {equipment_code} - Breakdown Frequency: {details['count']} - Causes: {cause_text} - Total Downtime Duration: {total_downtime:.2f} hours\n"

                else:
                    if language == "indonesia":
                        message += (
                            "\n- Equipment Breakdown Details:"
                            "\n  Tidak ada data breakdown yang tercatat untuk shift ini.\n"
                        )
                    else: 
                        message += (
                            "\n- Equipment Breakdown Details:"
                            "\n  There is no breakdown data recorded for this shift.\n"
                        )
            else:
                if language == "indonesia":
                    message += (
                        "\n- Equipment Breakdown Details:"
                        "\n  Tidak ada data breakdown tersedia.\n"
                    )
                else:
                    message += (
                        "\n- Equipment Breakdown Details:"
                        "\n  No breakdown data available.\n"
                    )                              
            dispatcher.utter_message(text=message)

        else:
            if language == "indonesia":
                dispatcher.utter_message(text="Maaf, terjadi masalah saat mengakses data.")
            else:
                dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        
        return [SlotSet("site_name", None), SlotSet("date_production_performance_control", None), SlotSet("shift_name", None)]