from typing import Text, Any, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction
from rasa_sdk.interfaces import Tracker
import locale
import requests
import jwt
import snakemd
from babel.dates import format_datetime
import logging
import matplotlib.pyplot as plt
import numpy as np
import io 
import base64
import math
from datetime import datetime, timedelta, date, timezone
from actions.services.fms.api  import get_operator_kpi_fms, get_fms_token, get_nik_from_token_fms

logger = logging.getLogger(__name__)

# class ActionGetFMSKpiSelfResult(Action):
#     def name(self) -> str:
#         return "action_get_fms_kpi_self_result"
    
#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         language = tracker.get_slot("language")
#         token_fms = get_fms_token(tracker)
#         date_production_performance_control = tracker.get_slot("date_production_performance_control")
#         logger.info(f"Action: action_get_fms_kpi_self_result")
#         value = None
#         if token_fms is not None:
#             value = get_operator_kpi_fms(token_fms, "date", [date_production_performance_control], get_nik_from_token_fms(token_fms))
        
#         try:
#             formatted_date = format_datetime(datetime.strptime(date_production_performance_control, "%Y-%m-%d"), "d MMMM yyyy", locale="id" if language == "indonesia" else "en")
#         except Exception:
#             formatted_date = date_production_performance_control 

#         if value is not None:
#             doc = snakemd.Document()
#             table_data = []            
#             if language == "indonesia":
#                 message = (
#                     f"Berikut adalah laporan KPI Anda untuk tanggal {formatted_date}.\n"
#                     f"Data Operator: \n"
#                         f"  - NIK: {value['summary']['operator']['nik']}\n"
#                         f"  - Nama: {value['summary']['operator']['name']}\n"
#                         f"  - Total Workhours: {value['summary']['workhours_total']}\n"
#                 )
#                 if not value['details']:
#                     dispatcher.utter_message(text=message)
#                     return [SlotSet("date_production_performance_control", None)]

#                 message += f"\nRincian KPI: \n"                        
#                 for i, details in enumerate (value['details'], 1):
#                     message += f"\n{i}. {details['equipment']['code']}:\n"
#                     if details.get('login_at') and details['login_at'] != 'N/A':
#                         absence_status = format_datetime(datetime.strptime(details['login_at'], "%Y-%m-%dT%H:%M:%S"), "d MMMM yyyy HH:mm:ss", locale="id")
#                     else:
#                         absence_status = "Tidak ada data"

#                     if details.get('logout_at') and details['logout_at'] != 'N/A':
#                         end_activity_status = format_datetime(datetime.strptime(details['logout_at'], "%Y-%m-%dT%H:%M:%S"), "d MMMM yyyy HH:mm:ss", locale="id")
#                     else:
#                         end_activity_status = "Tidak ada data"

#                     table_data.append(["Productivity", f"{details.get('hourly_productivity_actual', 0)}/{details.get('hourly_productivity_total', 0)} BCM/Hour"])
#                     table_data.append(["Production", f"{details.get('production_actual', 0)}/{details.get('production_total', 0)} BCM"])
#                     table_data.append(["Avg. Cycle Time", f"{details.get('average_cycle_time_minutes', 0)} min"])
#                     table_data.append(["Material", f"{details.get('material', 'Tidak diketahui')}"])
#                     table_data.append(["Dumping Point", f"{details.get('dump_point_name', 'Tidak diketahui')}"])
#                     table_data.append(["Ritase", f"{details.get('cycles', 0)}"])
#                     table_data.append(["T.Distance", f"{details.get('total_distances_meters', 0)} m"])
#                     table_data.append(["HM Start", f"{details.get('hm_start', 0)}"])
#                     table_data.append(["HM Stop", f"{details.get('hm_stop', 0)}"])
#                     table_data.append(["Workhours", f"{details.get('workhour_minutes_total', 0)}"])
#                     table_data.append(["Absence Status", f"{details.get('login_status', 'Tidak ada data')} at {absence_status}"])
#                     table_data.append(["End Activity Status", f"{details.get('logout_status', 'Tidak ada data')} at {end_activity_status}"])

#                 dispatcher.utter_message(text=message)
#                 doc.add_table(header=["Deskripsi", "Nilai"], data=table_data)
#                 dispatcher.utter_message(text=doc.__str__())
            
#             else:  
#                 message = (
#                     f"Here is your KPI report for the date {formatted_date}.\n"
#                     f"Operator Data: \n"
#                     f"  - NIK: {value['summary']['operator']['nik']}\n"
#                     f"  - Name: {value['summary']['operator']['name']}\n"
#                     f"  - Total Workhours: {value['summary']['workhours_total']}\n"
#                 )
                
#                 if not value['details']:
#                     dispatcher.utter_message(text=message)
#                     return [SlotSet("date_production_performance_control", None)]
                
#                 message += f"\nKPI Details: \n"
#                 for i in range(len(value['details'])):
#                     details = value['details'][i]
#                     message += f"\n{details['equipment']['code']}:\n"
#                     table_data.append([f"Equipment Code", details['equipment']['code']])

#                     if details.get('login_at') and details['login_at'] != 'N/A':
#                         absence_status = format_datetime(datetime.strptime(details['login_at'], "%Y-%m-%dT%H:%M:%S"), "d MMMM yyyy HH:mm:ss", locale="en")
#                     else:
#                         absence_status = "No data"

#                     if details.get('logout_at') and details['logout_at'] != 'N/A':
#                         end_activity_status = format_datetime(datetime.strptime(details['logout_at'], "%Y-%m-%dT%H:%M:%S"), "d MMMM yyyy HH:mm:ss", locale="en")
#                     else:
#                         end_activity_status = "No data"

#                     table_data.append([f"Productivity", f"{details.get('hourly_productivity_actual', 0)}/{details.get('hourly_productivity_total', 0)} BCM/Hour"])
#                     table_data.append([f"Production", f"{details.get('production_actual', 0)}/{details.get('production_total', 0)} BCM"])
#                     table_data.append([f"Avg. Cycle Time", f"{details.get('average_cycle_time_minutes', 0)} min"])
#                     table_data.append([f"Material", f"{details.get('material', 'Unknown')}"])
#                     table_data.append([f"Dumping Point", f"{details.get('dump_point_name', 'Unknown')}"])
#                     table_data.append([f"Ritase", f"{details.get('cycles', 0)}"])
#                     table_data.append([f"T.Distance", f"{details.get('total_distances_meters', 0)} m"])
#                     table_data.append([f"HM Start", f"{details.get('hm_start', 0)}"])
#                     table_data.append([f"HM Stop", f"{details.get('hm_stop', 0)}"])
#                     table_data.append([f"Workhours", f"{details.get('workhour_minutes_total', 0)}"])
#                     table_data.append([f"Absence Status", f"{details.get('login_status', 'No data')} at {absence_status}"])
#                     table_data.append([f"End Activity Status", f"{details.get('logout_status', 'No data')} at {end_activity_status}"])

#                 dispatcher.utter_message(text=message)
#                 doc.add_table(header=["Description", "Value"], data=table_data)
#                 dispatcher.utter_message(text=doc.__str__())
        
#         if language == "indonesia" and value is None:
#             dispatcher.utter_message(text="Maaf, terjadi masalah saat mengakses data.")
            
#         elif language == "english" and value is None:
#             dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        
#         return [SlotSet("date_production_performance_control", None)]

class ActionGetFMSKpiSelfResult(Action):
    def name(self) -> str:
        return "action_get_fms_kpi_self_result"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        date_production_performance_control = tracker.get_slot("date_production_performance_control")
        logger.info(f"Action: action_get_fms_kpi_self_result")
        
        value = None
        if token_fms is not None:
            value = get_operator_kpi_fms(token_fms, "date", [date_production_performance_control], get_nik_from_token_fms(token_fms))
        
        try:
            formatted_date = format_datetime(datetime.strptime(date_production_performance_control, "%Y-%m-%d"), "d MMMM yyyy", locale="id" if language == "indonesia" else "en")
        except Exception:
            formatted_date = date_production_performance_control 

        if value is not None:
            doc = snakemd.Document()
            table_data = []            
            if language == "indonesia":
                message = (
                    f"Berikut adalah laporan KPI Anda untuk tanggal {formatted_date}.\n"
                    f"Data Operator: \n"
                        f"  - NIK: {value['summary']['operator']['nik']}\n"
                        f"  - Nama: {value['summary']['operator']['name']}\n"
                        f"  - Total Workhours: {value['summary']['workhours_total']}\n"
                )
                
                if not value['details']:
                    dispatcher.utter_message(text=message)
                    return [SlotSet("date_production_performance_control", None)]

                message += f"\nRincian KPI: \n"                        
                for i, details in enumerate(value['details'], 1):
                    message += f"\n{i}. {details['equipment']['code']}:\n"
                    
                    # Handling login and logout times
                    if details.get('login_at') and details['login_at'] != 'N/A':
                        absence_status = format_datetime(datetime.strptime(details['login_at'], "%Y-%m-%dT%H:%M:%S"), "d MMMM yyyy HH:mm:ss", locale="id")
                    else:
                        absence_status = "Tidak ada data"

                    if details.get('logout_at') and details['logout_at'] != 'N/A':
                        end_activity_status = format_datetime(datetime.strptime(details['logout_at'], "%Y-%m-%dT%H:%M:%S"), "d MMMM yyyy HH:mm:ss", locale="id")
                    else:
                        end_activity_status = "Tidak ada data"
                    
                    # Extracting productivity data
                    productive_hours = details.get('productive_hours', 0)
                    non_productive_hours = details.get('non_productive_hours', 0)

                    # Avoiding division by zero
                    total_time = productive_hours + non_productive_hours
                    if total_time > 0:
                        productive_percentage = (productive_hours / total_time) * 100
                        non_productive_percentage = (non_productive_hours / total_time) * 100
                    else:
                        productive_percentage = 0
                        non_productive_percentage = 0

                    # Logging productivity for debugging
                    logger.info(f"Productivity for {details['equipment']['code']}: Productive: {productive_percentage:.2f}% | Non-Productive: {non_productive_percentage:.2f}%")

                    # Ensure that values are not NaN before plotting
                    if math.isnan(productive_percentage) or math.isnan(non_productive_percentage):
                        productive_percentage = 0
                        non_productive_percentage = 0

                    # Create the donut chart for productivity
                    fig, ax = plt.subplots(figsize=(6, 6))
                    ax.pie([productive_percentage, non_productive_percentage], 
                           labels=[f'{productive_percentage:.2f}%', f'{non_productive_percentage:.2f}%'], 
                           autopct='%1.1f%%', startangle=90, 
                           colors=['#28a745', '#d6d6d6'], 
                           wedgeprops={'width': 0.4, 'edgecolor': 'w'})
                    ax.text(0, 0, f'{productive_percentage:.2f}%', ha='center', va='center', fontsize=20, color='white')
                    ax.set_title(f"Productivity - {details['equipment']['code']} - {formatted_date}")

                    # Save to BytesIO and convert to base64
                    image_stream = io.BytesIO()
                    fig.savefig(image_stream, format='png')
                    image_stream.seek(0)
                    productivity_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

                    # Send the chart as a response
                    dispatcher.utter_message(text=f"![Productivity for {details['equipment']['code']}](data:image/png;base64,{productivity_base64})")

                # Continue with table data for other KPIs
                for i, details in enumerate(value['details'], 1):
                    table_data.append(["Productivity", f"{details.get('hourly_productivity_actual', 0)}/{details.get('hourly_productivity_total', 0)} BCM/Hour"])
                    table_data.append(["Production", f"{details.get('production_actual', 0)}/{details.get('production_total', 0)} BCM"])
                    table_data.append(["Avg. Cycle Time", f"{details.get('average_cycle_time_minutes', 0)} min"])
                    table_data.append(["Material", f"{details.get('material', 'Tidak diketahui')}"])
                    table_data.append(["Dumping Point", f"{details.get('dump_point_name', 'Tidak diketahui')}"])
                    table_data.append(["Ritase", f"{details.get('cycles', 0)}"])
                    table_data.append(["T.Distance", f"{details.get('total_distances_meters', 0)} m"])
                    table_data.append(["HM Start", f"{details.get('hm_start', 0)}"])
                    table_data.append(["HM Stop", f"{details.get('hm_stop', 0)}"])
                    table_data.append(["Workhours", f"{details.get('workhour_minutes_total', 0)}"])
                    table_data.append(["Absence Status", f"{details.get('login_status', 'Tidak ada data')} at {absence_status}"])
                    table_data.append(["End Activity Status", f"{details.get('logout_status', 'Tidak ada data')} at {end_activity_status}"])

                dispatcher.utter_message(text=message)
                doc.add_table(header=["Deskripsi", "Nilai"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())
            
            else:  
                # Similar for English messages here...
                pass
        
        if language == "indonesia" and value is None:
            dispatcher.utter_message(text="Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        
        return [SlotSet("date_production_performance_control", None)]

# class ActionGetFMSKpiSelfResultToday(Action):
#     def name(self) -> str:
#         return "action_get_fms_kpi_self_result_today"
    
#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         language = tracker.get_slot("language")
#         token_fms = get_fms_token(tracker)
#         today = datetime.now().date().strftime('%Y-%m-%d')
#         logger.info(f"Action: action_get_fms_kpi_self_result_today")

#         value = None
#         if token_fms is not None:
#             value = get_operator_kpi_fms(token_fms, "date", [today], get_nik_from_token_fms(token_fms))

#         try:
#             formatted_date = format_datetime(datetime.strptime(today, "%Y-%m-%d"), "d MMMM yyyy", locale="id" if language == "indonesia" else "en")
#         except Exception:
#             formatted_date = today 

#         if value is not None:
#             doc = snakemd.Document()
#             table_data = []
#             if language == "indonesia":
#                 message = (
#                     f"Berikut adalah laporan KPI Anda untuk hari ini {formatted_date}.\n"
#                     f"Data Operator: \n"
#                         f"  - NIK: {value['summary']['operator']['nik']}\n"
#                         f"  - Nama: {value['summary']['operator']['name']}\n"
#                         f"  - Total Workhours: {value['summary']['workhours_total']}\n"
#                 )
#                 if not value['details']:
#                     dispatcher.utter_message(text=message)
#                     return [SlotSet("date_production_performance_control", None)]
                
#                 message += f"\nRincian KPI: \n"
#                 for i in range(len(value['details'])):
#                     details = value['details'][i]
#                     message += (f"{i+1}. {details['equipment']['code']} :\n")
                    
#                     absence_status = "Tidak ada data"
#                     if details.get('login_at') and details['login_at'] != 'N/A':
#                         absence_status = format_datetime(datetime.strptime(details['login_at'], "%Y-%m-%dT%H:%M:%S"), "d MMMM yyyy HH:mm:ss", locale="id")
                    
#                     end_activity_status = "Tidak ada data"
#                     if details.get('logout_at') and details['logout_at'] != 'N/A':
#                         end_activity_status = format_datetime(datetime.strptime(details['logout_at'], "%Y-%m-%dT%H:%M:%S"), "d MMMM yyyy HH:mm:ss", locale="id")

#                     table_data.append(["Productivity", f"{details.get('hourly_productivity_actual', 0)}/{details.get('hourly_productivity_total', 0)} BCM/Hour"])
#                     table_data.append(["Production", f"{details.get('production_actual', 0)}/{details.get('production_total', 0)} BCM"])
#                     table_data.append(["Avg. Cycle Time", f"{details.get('average_cycle_time_minutes', 0)} min"])
#                     table_data.append(["Material", f"{details.get('material', 'Tidak diketahui')}"])
#                     table_data.append(["Dumping Point", f"{details.get('dump_point_name', 'Tidak diketahui')}"])
#                     table_data.append(["Ritase", f"{details.get('cycles', 0)}"])
#                     table_data.append(["T.Distance", f"{details.get('total_distances_meters', 0)} m"])
#                     table_data.append(["HM Start", f"{details.get('hm_start', 0)}"])
#                     table_data.append(["HM Stop", f"{details.get('hm_stop', 0)}"])
#                     table_data.append(["Workhours", f"{details.get('workhour_minutes_total', 0)}"])
#                     table_data.append(["Absence Status", f"{details.get('login_status', 'Tidak ada data')} at {absence_status}"])
#                     table_data.append(["End Activity Status", f"{details.get('logout_status', 'Tidak ada data')} at {end_activity_status}"])
#                 dispatcher.utter_message(text=message)
#                 doc.add_table(header=["Deskripsi", "Nilai"], data=table_data)
#                 dispatcher.utter_message(text=doc.__str__()) 
            
#             else:
#                 message = (
#                     f"Here is your KPI report for today {formatted_date}.\n"
#                     f"Operator Data: \n"
#                     f"  - NIK: {value['summary']['operator']['nik']}\n"
#                     f"  - Name: {value['summary']['operator']['name']}\n"
#                     f"  - Total Workhours: {value['summary']['workhours_total']}\n"
#                 )
#                 if not value['details']:
#                     dispatcher.utter_message(text=message)
#                     return [SlotSet("date_production_performance_control", None)]
    
#                 message += f"\nKPI Details: \n"
#                 for i in range(len(value['details'])):
#                     details = value['details'][i]
#                     message += (f"{i+1}. {details['equipment']['code']} :\n")
                    
#                     absence_status = "No data"
#                     if details.get('login_at') and details['login_at'] != 'N/A':
#                         absence_status = format_datetime(datetime.strptime(details['login_at'], "%Y-%m-%dT%H:%M:%S"), "d MMMM yyyy HH:mm:ss", locale="en")
                    
#                     end_activity_status = "No data"
#                     if details.get('logout_at') and details['logout_at'] != 'N/A':
#                         end_activity_status = format_datetime(datetime.strptime(details['logout_at'], "%Y-%m-%dT%H:%M:%S"), "d MMMM yyyy HH:mm:ss", locale="en")

#                     table_data.append(["Productivity", f"{details.get('hourly_productivity_actual', 0)}/{details.get('hourly_productivity_total', 0)} BCM/Hour"])
#                     table_data.append(["Production", f"{details.get('production_actual', 0)}/{details.get('production_total', 0)} BCM"])
#                     table_data.append(["Avg. Cycle Time", f"{details.get('average_cycle_time_minutes', 0)} min"])
#                     table_data.append(["Material", f"{details.get('material', 'Unknown')}"])
#                     table_data.append(["Dumping Point", f"{details.get('dump_point_name', 'Unknown')}"])
#                     table_data.append(["Ritase", f"{details.get('cycles', 0)}"])
#                     table_data.append(["T.Distance", f"{details.get('total_distances_meters', 0)} m"])
#                     table_data.append(["HM Start", f"{details.get('hm_start', 0)}"])
#                     table_data.append(["HM Stop", f"{details.get('hm_stop', 0)}"])
#                     table_data.append(["Workhours", f"{details.get('workhour_minutes_total', 0)}"])
#                     table_data.append(["Absence Status", f"{details.get('login_status', 'No data')} at {absence_status}"])
#                     table_data.append(["End Activity Status", f"{details.get('logout_status', 'No data')} at {end_activity_status}"])
#                 dispatcher.utter_message(text=message)
#                 doc.add_table(header=["Description", "Value"], data=table_data)
#                 dispatcher.utter_message(text=doc.__str__())
        
#         if language == "indonesia" and value is None:
#             dispatcher.utter_message(text="Maaf, terjadi masalah saat mengakses data.")
            
#         elif language == "english" and value is None:
#             dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        
#         return [SlotSet("date_production_performance_control", None)]

class ActionGetFMSKpiSelfResultToday(Action):
    def name(self) -> str:
        return "action_get_fms_kpi_self_result_today"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        today = datetime.now().date().strftime('%Y-%m-%d')
        logger.info(f"Action: action_get_fms_kpi_self_result_today")

        value = None
        if token_fms is not None:
            value = get_operator_kpi_fms(token_fms, "date", [today], get_nik_from_token_fms(token_fms))

        try:
            formatted_date = format_datetime(datetime.strptime(today, "%Y-%m-%d"), "d MMMM yyyy", locale="id" if language == "indonesia" else "en")
        except Exception:
            formatted_date = today 

        if value is not None:
            doc = snakemd.Document()
            table_data = []
            
            # Collect data for Productivity pie chart (Productive vs Non-Productive)
            productive_data = []
            non_productive_data = []

            # Message for KPI details (Operator, Workhours, etc.)
            if language == "indonesia":
                message = (
                    f"Berikut adalah laporan KPI Anda untuk hari ini {formatted_date}.\n"
                    f"Data Operator: \n"
                        f"  - NIK: {value['summary']['operator']['nik']}\n"
                        f"  - Nama: {value['summary']['operator']['name']}\n"
                        f"  - Total Workhours: {value['summary']['workhours_total']}\n"
                )
                
                if not value['details']:
                    dispatcher.utter_message(text=message)
                    return [SlotSet("date_production_performance_control", None)]
                
                message += f"\nRincian KPI: \n"
                for i in range(len(value['details'])):
                    details = value['details'][i]
                    message += (f"{i+1}. {details['equipment']['code']} :\n")
                    
                    absence_status = "Tidak ada data"
                    if details.get('login_at') and details['login_at'] != 'N/A':
                        absence_status = format_datetime(datetime.strptime(details['login_at'], "%Y-%m-%dT%H:%M:%S"), "d MMMM yyyy HH:mm:ss", locale="id")
                    
                    end_activity_status = "Tidak ada data"
                    if details.get('logout_at') and details['logout_at'] != 'N/A':
                        end_activity_status = format_datetime(datetime.strptime(details['logout_at'], "%Y-%m-%dT%H:%M:%S"), "d MMMM yyyy HH:mm:ss", locale="id")

                    # Data for the table
                    table_data.append(["Productivity", f"{details.get('hourly_productivity_actual', 0)}/{details.get('hourly_productivity_total', 0)} BCM/Hour"])
                    table_data.append(["Production", f"{details.get('production_actual', 0)}/{details.get('production_total', 0)} BCM"])
                    table_data.append(["Avg. Cycle Time", f"{details.get('average_cycle_time_minutes', 0)} min"])
                    table_data.append(["Workhours", f"{details.get('workhour_minutes_total', 0)}"])

                    # Collect data for the pie chart (Productive vs Non-Productive)
                    hourly_productivity_actual = details.get('hourly_productivity_actual', 0)
                    if hourly_productivity_actual > 0:
                        productive_data.append(hourly_productivity_actual)
                        non_productive_data.append(0)
                    else:
                        productive_data.append(0)
                        non_productive_data.append(hourly_productivity_actual)

                # Generate the pie chart for productivity (Productive vs Non-Productive)
                labels = ['Productive', 'Non-Productive']
                sizes = [sum(productive_data), sum(non_productive_data)]
                colors = ['#1f77b4', '#ff7f0e']  # Blue for Productive, Orange for Non-Productive

                # Handle zero data scenario
                if sum(sizes) == 0:  # If both values are zero
                    sizes = [100, 0]  # Show 100% for Productive and 0% for Non-Productive
                    labels = ['Productive (0%)', 'Non-Productive (0%)']

                # Sanitize data: replace NaN with 0
                sizes = np.nan_to_num(sizes, nan=0)

                # Plot the pie chart
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)

                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                ax.set_title('Work Hours Productivity Distribution')

                # Save the pie chart to a BytesIO object
                image_stream = io.BytesIO()
                fig.savefig(image_stream, format='png')
                image_stream.seek(0)

                # Convert the pie chart to base64 for embedding
                image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

                # Send the pie chart as an embedded image
                dispatcher.utter_message(text="Berikut adalah diagram Workhours Productivity:") if language == "indonesia" else dispatcher.utter_message(text="Here is the Workhours Productivity diagram:")
                dispatcher.utter_message(text=f"![Workhours Productivity](data:image/png;base64,{image_base64})")

                dispatcher.utter_message(text=message)
                doc.add_table(header=["Deskripsi", "Nilai"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())
            
            else:  
                message = (
                    f"Here is your KPI report for today {formatted_date}.\n"
                    f"Operator Data: \n"
                    f"  - NIK: {value['summary']['operator']['nik']}\n"
                    f"  - Name: {value['summary']['operator']['name']}\n"
                    f"  - Total Workhours: {value['summary']['workhours_total']}\n"
                )
                if not value['details']:
                    dispatcher.utter_message(text=message)
                    return [SlotSet("date_production_performance_control", None)]
    
                message += f"\nKPI Details: \n"
                for i in range(len(value['details'])):
                    details = value['details'][i]
                    message += (f"{i+1}. {details['equipment']['code']} :\n")
                    
                    absence_status = "No data"
                    if details.get('login_at') and details['login_at'] != 'N/A':
                        absence_status = format_datetime(datetime.strptime(details['login_at'], "%Y-%m-%dT%H:%M:%S"), "d MMMM yyyy HH:mm:ss", locale="en")
                    
                    end_activity_status = "No data"
                    if details.get('logout_at') and details['logout_at'] != 'N/A':
                        end_activity_status = format_datetime(datetime.strptime(details['logout_at'], "%Y-%m-%dT%H:%M:%S"), "d MMMM yyyy HH:mm:ss", locale="en")

                    # Data for the table
                    table_data.append([f"Productivity", f"{details.get('hourly_productivity_actual', 0)}/{details.get('hourly_productivity_total', 0)} BCM/Hour"])
                    table_data.append([f"Production", f"{details.get('production_actual', 0)}/{details.get('production_total', 0)} BCM"])
                    table_data.append([f"Avg. Cycle Time", f"{details.get('average_cycle_time_minutes', 0)} min"])
                    table_data.append([f"Workhours", f"{details.get('workhour_minutes_total', 0)}"])

                    # Collect data for the pie chart (Productive vs Non-Productive)
                    hourly_productivity_actual = details.get('hourly_productivity_actual', 0)
                    if hourly_productivity_actual > 0:
                        productive_data.append(hourly_productivity_actual)
                        non_productive_data.append(0)
                    else:
                        productive_data.append(0)
                        non_productive_data.append(hourly_productivity_actual)

                # Generate the pie chart for productivity (Productive vs Non-Productive)
                labels = ['Productive', 'Non-Productive']
                sizes = [sum(productive_data), sum(non_productive_data)]
                colors = ['#1f77b4', '#ff7f0e']  # Blue for Productive, Orange for Non-Productive

                # Handle zero data scenario
                if sum(sizes) == 0:  # If both values are zero
                    sizes = [100, 0]  # Show 100% for Productive and 0% for Non-Productive
                    labels = ['Productive (0%)', 'Non-Productive (0%)']

                # Sanitize data: replace NaN with 0
                sizes = np.nan_to_num(sizes, nan=0)

                # Plot the pie chart
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)

                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                ax.set_title('Work Hours Productivity Distribution')

                # Save the pie chart to a BytesIO object
                image_stream = io.BytesIO()
                fig.savefig(image_stream, format='png')
                image_stream.seek(0)

                # Convert the pie chart to base64 for embedding
                image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

                # Send the pie chart as an embedded image
                dispatcher.utter_message(text="Here is the Workhours Productivity diagram:")
                dispatcher.utter_message(text=f"![Workhours Productivity](data:image/png;base64,{image_base64})")

                dispatcher.utter_message(text=message)
                doc.add_table(header=["Description", "Value"], data=table_data)
                dispatcher.utter_message(text=doc.__str__())

        if language == "indonesia" and value is None:
            dispatcher.utter_message(text="Maaf, terjadi masalah saat mengakses data.")
            
        elif language == "english" and value is None:
            dispatcher.utter_message(text="Sorry, there was a problem accessing data.")
        
        return [SlotSet("date_production_performance_control", None)]
    
class ActionGetFMSKpiOtherOperatorResult(Action): 
    def name(self) -> str:
        return "action_get_fms_kpi_other_operator_result"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")
        token_fms = get_fms_token(tracker)
        input_nik_operator = tracker.get_slot("input_nik_operator")
        date_production_performance_control = tracker.get_slot("date_production_performance_control")
        logger.info(f"Action: action_get_fms_kpi_other_operator_result")
        logger.info(f"NIK Operator: {input_nik_operator}")

        value = None
        if token_fms is not None:
            value = get_operator_kpi_fms(token_fms, "date", [date_production_performance_control], input_nik_operator)
        
        try:
            formatted_date = format_datetime(datetime.strptime(date_production_performance_control, "%Y-%m-%d"), "d MMMM yyyy", locale="id" if language == "indonesia" else "en")
        except Exception:
            formatted_date = date_production_performance_control

        if value is not None:
            logger.info(f"Detail KPI: {value['details']}")
        else:
            logger.info("No value found for KPI details")

        if value is not None:
            doc = snakemd.Document()
            table_data = []
            
            if language == "indonesia":
                message = (
                    f"Berikut adalah laporan KPI Operator {input_nik_operator} untuk tanggal {formatted_date}.\n"
                    f"Data Operator: \n"
                    f" - NIK: {value['summary']['operator']['nik']}\n"
                    f" - Nama: {value['summary']['operator']['name']}\n"
                    f" - Total Workhours: {value['summary']['workhours_total']:.2f}\n"
                )
                message += "\nRincian KPI: \n"
                dispatcher.utter_message(text=message)

                # Process details and generate table for each equipment
                for i, details in enumerate(value['details']):
                    equipment_code = details['equipment']['code']
                    message += f"\n{i + 1}. {equipment_code}:\n"
                    doc = snakemd.Document()

                    table_data = []
                    absence_status = "Tidak ada data" if language == "indonesia" else "No data"
                    if details.get('login_at') and details['login_at'] != 'N/A':
                        absence_status = format_datetime(datetime.strptime(details['login_at'], "%Y-%m-%dT%H:%M:%S"), "d MMMM yyyy HH:mm:ss", locale="id" if language == "indonesia" else "en")
                    
                    end_activity_status = "Tidak ada data" if language == "indonesia" else "No data"
                    if details.get('logout_at') and details['logout_at'] != 'N/A':
                        end_activity_status = format_datetime(datetime.strptime(details['logout_at'], "%Y-%m-%dT%H:%M:%S"), "d MMMM yyyy HH:mm:ss", locale="id" if language == "indonesia" else "en")

                    # Prepare the table data
                    table_data.append(["Productivity", f"{details.get('hourly_productivity_actual', 0)}/{details.get('hourly_productivity_total', 0)} BCM/Hour"])
                    table_data.append(["Production", f"{details.get('production_actual', 0)}/{details.get('production_total', 0)} BCM"])
                    table_data.append(["Avg. Cycle Time", f"{details.get('average_cycle_time_minutes', 0)} min"])
                    table_data.append(["Material", f"{details.get('material', 'Tidak diketahui')}"])
                    table_data.append(["Dumping Point", f"{details.get('dump_point_name', 'Tidak diketahui')}"])
                    table_data.append(["Ritase", f"{details.get('cycles', 0)}"])
                    table_data.append(["T.Distance", f"{details.get('total_distances_meters', 0)} m"])
                    table_data.append(["HM Start", f"{details.get('hm_start', 0)}"])
                    table_data.append(["HM Stop", f"{details.get('hm_stop', 0)}"])
                    table_data.append(["Workhours", f"{details.get('workhour_minutes_total', 0)}"])
                    table_data.append(["Absence Status", f"{details.get('login_status', 'Tidak ada data')} at {absence_status}"])
                    table_data.append(["End Activity Status", f"{details.get('logout_status', 'Tidak ada data')} at {end_activity_status}"])

                    doc.add_table(header=["Deskripsi", "Nilai"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())

            else:  # English
                message = (
                    f"Here is the KPI report for Operator {input_nik_operator} on {formatted_date}.\n"
                    f"Operator Data: \n"
                    f" - NIK: {value['summary']['operator']['nik']}\n"
                    f" - Name: {value['summary']['operator']['name']}\n"
                    f" - Total Workhours: {value['summary']['workhours_total']:.2f}\n"
                )
                message += "\nKPI Details: \n"
                dispatcher.utter_message(text=message)

                # Process details and generate table for each equipment
                for i, details in enumerate(value['details']):
                    equipment_code = details['equipment']['code']
                    message += f"\n{i + 1}. {equipment_code}:\n"

                    table_data = []
                    absence_status = "No data" if language == "english" else "Tidak ada data"
                    if details.get('login_at') and details['login_at'] != 'N/A':
                        absence_status = format_datetime(datetime.strptime(details['login_at'], "%Y-%m-%dT%H:%M:%S"), "d MMMM yyyy HH:mm:ss", locale="en")
                    
                    end_activity_status = "No data" if language == "english" else "Tidak ada data"
                    if details.get('logout_at') and details['logout_at'] != 'N/A':
                        end_activity_status = format_datetime(datetime.strptime(details['logout_at'], "%Y-%m-%dT%H:%M:%S"), "d MMMM yyyy HH:mm:ss", locale="en")

                    # Prepare the table data
                    table_data.append(["Productivity", f"{details.get('hourly_productivity_actual', 0)}/{details.get('hourly_productivity_total', 0)} BCM/Hour"])
                    table_data.append(["Production", f"{details.get('production_actual', 0)}/{details.get('production_total', 0)} BCM"])
                    table_data.append(["Avg. Cycle Time", f"{details.get('average_cycle_time_minutes', 0)} min"])
                    table_data.append(["Material", f"{details.get('material', 'Unknown')}"])
                    table_data.append(["Dumping Point", f"{details.get('dump_point_name', 'Unknown')}"])
                    table_data.append(["Ritase", f"{details.get('cycles', 0)}"])
                    table_data.append(["T.Distance", f"{details.get('total_distances_meters', 0)} m"])
                    table_data.append(["HM Start", f"{details.get('hm_start', 0)}"])
                    table_data.append(["HM Stop", f"{details.get('hm_stop', 0)}"])
                    table_data.append(["Workhours", f"{details.get('workhour_minutes_total', 0)}"])
                    table_data.append(["Absence Status", f"{details.get('login_status', 'No data')} at {absence_status}"])
                    table_data.append(["End Activity Status", f"{details.get('logout_status', 'No data')} at {end_activity_status}"])

                    doc.add_table(header=["Description", "Value"], data=table_data)
                    dispatcher.utter_message(text=doc.__str__())

            dispatcher.utter_message(text=message)

        else:
            dispatcher.utter_message(text="Maaf, terjadi masalah saat mengakses data." if language == "indonesia" else "Sorry, there was a problem accessing the data.")

        return [SlotSet("date_production_performance_control", None)]


class ActionAskInputNIKOperator(Action):
    def name(self):
        return "action_ask_input_nik_operator"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language")

        if language == "indonesia":
            dispatcher.utter_message(text = "Tolong masukkan NIK operator yang ingin anda cari")
        else:
            dispatcher.utter_message(text = "Please state the operator NIK you want to search for")
        return []
    
