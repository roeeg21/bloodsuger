from flask import Flask, jsonify, request, render_template
import suger_reading

app = Flask(__name__)  

@app.route('/')
def glucose():
    suger_dict = suger_reading.get_glucose_reading()

    return jsonify(suger_dict)

@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/log")
def log_page():
    return render_template("log.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)