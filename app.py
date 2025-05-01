from flask import Flask,jsonify,request
import suger_reading

flask = Flask(__name__)

@app.route('/')
def hello():
    return "Server is running!"

@app.route('/glucose')
def glucose():
    suger_dict = suger_reading.get_glucose_reading()
    return jsonify(suger_dict)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)  # port is usually auto-handled by Render














if __name__ == '__main__':
    app = Flask(__name__)