from pydexcom import Dexcom
import time

LOW_SUGER = 60
HIGH_SUGER = 250
x=0
suger_dict = {}

flag = True
dexcom = Dexcom(username='roee.dexcom',password='Sdfwer234',region="ous")
glucose = dexcom.get_current_glucose_reading()




def HIGH_or_LOW(glucose_reading):
    if glucose_reading <= LOW_SUGER:
        return "low"
    elif glucose_reading >= HIGH_SUGER:
        return "high"
    else:
        return "ok"
    

def get_glucose_reading():
   while flag: 
    try:
        glucose = dexcom.get_current_glucose_reading()
    except Exception as e:
        if e == NoneType:
             glucose = dexcom.get_current_glucose_reading()
        suger_dict["Glucose"] = glucose.value
        print(f"Glucose: {glucose.value} mg/dL is {HIGH_or_LOW(glucose.value)}") 
        time.sleep(250)
        return suger_dict
   




