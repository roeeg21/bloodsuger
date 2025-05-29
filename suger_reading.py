from pydexcom import Dexcom
import time
import os

LOW_SUGER = 60
HIGH_SUGER = 250
USERNAME = os.getenv('Dexcom_username')
PASSWORD = os.getenv('Dexcom_password')
suger_dict = {}

flag = True
dexcom = Dexcom(username=USERNAME,password=PASSWORD,region="ous")
glucose = dexcom.get_current_glucose_reading()




def HIGH_or_LOW(glucose_reading):
    if glucose_reading <= LOW_SUGER:
        return "low"
    elif glucose_reading >= HIGH_SUGER:
        return "high"
    else:
        return "ok"
    

def get_glucose_reading():
    try:
        glucose = dexcom.get_current_glucose_reading()
        suger_dict = {
            "Glucose": glucose.value,
            "Status": HIGH_or_LOW(glucose.value),
            "Trend": glucose.trend_description,
            "Time": glucose.datetime.strftime("%Y-%m-%d %H:%M:%S")
        }
        return suger_dict
    except Exception as e:
        glucose = dexcom.get_latest_glucose_reading()
        suger_dict = {
            "Glucose": glucose.value,
            "Status": HIGH_or_LOW(glucose.value),
            "Trend": glucose.trend_description,
            "Time": glucose.datetime.strftime("%Y-%m-%d %H:%M:%S")
        }
        return suger_dict
    

print(get_glucose_reading())