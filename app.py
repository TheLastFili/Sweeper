from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import datetime
from collections import defaultdict

app = Flask(__name__)
socketio = SocketIO(app)

# Using defaultdict to automatically initialize empty lists for new dates
timers_by_date = defaultdict(list)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/timers/<date>')
def get_timers(date):
    # Return empty list if no timers exist for the date
    return jsonify(timers_by_date[date])

@app.route('/api/timer', methods=['POST'])
def save_timer():
    data = request.get_json()
    date = data['date']
    timer = data['timer']

    # If timer has an index, update existing timer
    if 'index' in data:
        index = data['index']
        if 0 <= index < len(timers_by_date[date]):
            timers_by_date[date][index] = timer
    else:
        # Otherwise append new timer
        timers_by_date[date].append(timer)

    return jsonify({"message": "Timer saved"})

@app.route('/api/timer', methods=['DELETE'])
def delete_timer():
    data = request.get_json()
    date = data['date']
    index = data['index']

    if 0 <= index < len(timers_by_date[date]):
        timers_by_date[date].pop(index)
        return jsonify({"message": "Timer deleted"})
    return jsonify({"error": "Timer not found"}), 404

@app.route('/api/timer/start', methods=['POST'])
def start_timer():
    data = request.get_json()
    date = data['date']
    index = data['index']

    if 0 <= index < len(timers_by_date[date]):
        timers_by_date[date][index]['start'] = datetime.datetime.now().timestamp() * 1000
        timers_by_date[date][index]['lastStarted'] = datetime.datetime.now().timestamp() * 1000
        return jsonify({"message": "Timer started"})
    return jsonify({"error": "Timer not found"}), 404

@app.route('/api/timer/stop', methods=['POST'])
def stop_timer():
    data = request.get_json()
    date = data['date']
    index = data['index']

    if 0 <= index < len(timers_by_date[date]):
        timer = timers_by_date[date][index]
        if timer['start']:
            elapsed = (datetime.datetime.now().timestamp() * 1000 - timer['start']) / 1000
            timer['elapsed'] += elapsed
            timer['start'] = None
            return jsonify({"elapsed": timer['elapsed']})
    return jsonify({"error": "Timer not found"}), 404

@app.route('/api/timer/copy', methods=['POST'])
def copy_timer():
    data = request.get_json()
    target_date = data['targetDate']
    timer = data['timer']

    timers_by_date[target_date].append(timer)
    return jsonify({"message": "Timer copied"})

@app.route('/api/report')
def get_report():
    return jsonify(timers_by_date)

if __name__ == '__main__':
    socketio.run(app, debug=True)
