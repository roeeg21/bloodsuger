from pydexcom import Dexcom

LOW_SUGER = 60
HIGH_SUGER = 250

# Fill in your Dexcom credentials
USERNAME = "roee.dexcom"
PASSWORD = "Sdfwer234"

# Initialize Dexcom object
dexcom = Dexcom(USERNAME, PASSWORD, region="ous")

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
        return {"error": str(e)}
