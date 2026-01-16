from pydexcom import Dexcom


import os

LOW_SUGER = 60
HIGH_SUGER = 250
USERNAME_tmp = os.getenv('Dexcom_username')
PASSWORD_tmp = os.getenv('Dexcom_password')

suger_dict = {}

flag = True


dexcom = Dexcom(username=USERNAME_tmp,password=PASSWORD_tmp,ous=flag)






def HIGH_or_LOW(glucose_reading):
    if glucose_reading <= LOW_SUGER:
        return "low"
    elif glucose_reading >= HIGH_SUGER:
        return "high"
    else:
        return "ok"
    

def get_glucose_reading():
    glucose = dexcom.get_latest_glucose_reading()
    suger_dict = {
        "Glucose": glucose.value,
        "Status": HIGH_or_LOW(glucose.value),
        "Trend": glucose.trend_description,
        "Time": glucose.datetime.strftime("%Y-%m-%d %H:%M:%S")}
    return suger_dict
    
         

print(get_glucose_reading())
