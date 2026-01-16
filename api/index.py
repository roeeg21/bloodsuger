import os
from flask import Flask, jsonify, render_template
from pydexcom import Dexcom

app = Flask(__name__)

# --- SUGER_READING LOGIC (Combined) ---
def get_glucose_reading():
    # Pulling from Vercel Environment Variables
    USERNAME_tmp = os.environ.get("Dexcom_username")
    PASSWORD_tmp = os.environ.get("Dexcom_password")
    
    if not USERNAME or not PASSWORD:
        return {"error": "Missing credentials in Vercel settings"}

    try:
        # Using region="ous" for outside US as per your requirement
        dexcom = Dexcom(username=USERNAME_tmp, password=PASSWORD_tmp, region="ous")
        glucose_reading = dexcom.get_current_glucose_reading()
    
    
        
        
        if glucose_reading:
            return {
                "value": glucose_reading.value,
                "trend": glucose_reading.trend_description,
                "time": str(glucose_reading.datetime),
                "trend_arrow": glucose_reading.trend_arrow,
                
            }
        return {"error": "No recent glucose reading found"}
    except Exception as e:
        return {"error": str(e)}

# --- FLASK ROUTES ---
@app.route('/')
def glucose():
    # Calling the function directly now that it's in the same file
    suger_dict = get_glucose_reading()
    return jsonify(suger_dict)

'''@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/log")
def log_page():
    return render_template("log.html")

# No app.run() needed for Vercel
'''