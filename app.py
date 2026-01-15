from flask import Flask, jsonify, render_template, request, send_file
import suger_reading
import json
from datetime import datetime
import io
import csv

app = Flask(__name__)

# In-memory storage for glucometer logs
glucometer_logs = []

@app.route('/')
def glucose():
    suger_dict = suger_reading.get_glucose_reading()
    return jsonify(suger_dict)

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/log')
def log_page():
    return render_template('log.html')

@app.route('/api/log', methods=['POST'])
def add_log():
    data = request.json
    
    # Get current CGM reading
    cgm_reading = suger_reading.get_glucose_reading()
    
    log_entry = {
        'id': len(glucometer_logs) + 1,
        'timestamp': data.get('timestamp', datetime.now().isoformat()),
        'glucometer_value': data['glucometer_value'],
        'cgm_value': cgm_reading['Glucose'],
        'difference': abs(data['glucometer_value'] - cgm_reading['Glucose']),
        'notes': data.get('notes', '')
    }
    
    glucometer_logs.append(log_entry)
    return jsonify(log_entry)

@app.route('/api/logs', methods=['GET'])
def get_logs():
    return jsonify(glucometer_logs)

@app.route('/api/logs/<int:log_id>', methods=['DELETE'])
def delete_log(log_id):
    global glucometer_logs
    glucometer_logs = [log for log in glucometer_logs if log['id'] != log_id]
    return jsonify({'success': True})

@app.route('/api/export')
def export_logs():
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['Timestamp', 'Glucometer Value (mg/dL)', 'CGM Value (mg/dL)', 
                     'Difference (mg/dL)', 'Notes'])
    
    # Write data
    for log in glucometer_logs:
        timestamp = datetime.fromisoformat(log['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([
            timestamp,
            log['glucometer_value'],
            log['cgm_value'],
            log['difference'],
            log['notes']
        ])
    
    # Convert to bytes
    output.seek(0)
    bytes_output = io.BytesIO()
    bytes_output.write(output.getvalue().encode('utf-8'))
    bytes_output.seek(0)
    
    return send_file(
        bytes_output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'glucose_comparison_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)