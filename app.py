from flask import Flask, jsonify, render_template, request, send_file, abort
import suger_reading
from datetime import datetime
import io
import csv

app = Flask(__name__)

# In-memory storage (NOTE: resets on restart)
glucometer_logs: list[dict] = []


@app.route('/')
def glucose():
    """
    Returns current CGM glucose reading
    """
    try:
        sugar_dict = suger_reading.get_glucose_reading()
        return jsonify(sugar_dict)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/log')
def log_page():
    return render_template('log.html')


@app.route('/api/log', methods=['POST'])
def add_log():
    """
    Add a glucometer reading and compare to CGM
    """
    if not request.is_json:
        abort(400, description="Request must be JSON")

    data = request.get_json()

    if 'glucometer_value' not in data:
        abort(400, description="Missing glucometer_value")

    try:
        glucometer_value = float(data['glucometer_value'])
    except (ValueError, TypeError):
        abort(400, description="glucometer_value must be a number")

    try:
        cgm_reading = suger_reading.get_glucose_reading()
        cgm_value = float(cgm_reading.get('Glucose'))
    except Exception as e:
        abort(500, description=f"Failed to read CGM: {e}")

    timestamp = data.get('timestamp')
    if timestamp:
        try:
            datetime.fromisoformat(timestamp)
        except ValueError:
            abort(400, description="timestamp must be ISO format")
    else:
        timestamp = datetime.now().isoformat()

    log_entry = {
        'id': len(glucometer_logs) + 1,
        'timestamp': timestamp,
        'glucometer_value': glucometer_value,
        'cgm_value': cgm_value,
        'difference': abs(glucometer_value - cgm_value),
        'notes': data.get('notes', '')
    }

    glucometer_logs.append(log_entry)
    return jsonify(log_entry), 201


@app.route('/api/logs', methods=['GET'])
def get_logs():
    return jsonify(glucometer_logs)


@app.route('/api/logs/<int:log_id>', methods=['DELETE'])
def delete_log(log_id):
    """
    Delete a log entry by ID
    """
    global glucometer_logs
    original_len = len(glucometer_logs)
    glucometer_logs = [log for log in glucometer_logs if log['id'] != log_id]

    if len(glucometer_logs) == original_len:
        abort(404, description="Log not found")

    return jsonify({'success': True})


@app.route('/api/export', methods=['GET'])
def export_logs():
    """
    Export logs as CSV
    """
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Timestamp',
        'Glucometer Value (mg/dL)',
        'CGM Value (mg/dL)',
        'Difference (mg/dL)',
        'Notes'
    ])

    for log in glucometer_logs:
        try:
            timestamp = datetime.fromisoformat(log['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            timestamp = log['timestamp']

        writer.writerow([
            timestamp,
            log['glucometer_value'],
            log['cgm_value'],
            log['difference'],
            log['notes']
        ])

    bytes_output = io.BytesIO(output.getvalue().encode('utf-8'))
    bytes_output.seek(0)

    return send_file(
        bytes_output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'glucose_comparison_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )


if __name__ == '__main__':
     app.run(debug=True)