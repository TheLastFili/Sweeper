from flask import Flask, render_template, request, jsonify
import datetime
from collections import defaultdict
from uuid import uuid4  # Import UUID to generate unique IDs

app = Flask(__name__)

# Using defaultdict to automatically initialize empty lists for new dates
timers_by_date = defaultdict(list)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/timers/<date>')
def get_timers(date):
    return jsonify(timers_by_date[date])

@app.route('/api/timer', methods=['POST'])
@app.route('/api/timer', methods=['POST'])
def save_timer():
    data = request.get_json()
    date = data['date']
    timer = data['timer']

    # If a timer has no ID, assign one
    if 'id' not in timer:
        timer['id'] = str(uuid4())  # Generate a unique ID

    # Check if the timer already exists (by ID) and update it
    for i, existing_timer in enumerate(timers_by_date[date]):
        if existing_timer.get('id') == timer['id']:
            timers_by_date[date][i] = timer
            return jsonify({"message": "Timer updated"})

    # Otherwise, add a new timer
    timers_by_date[date].append(timer)
    return jsonify({"message": "Timer added"})


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
            now_timestamp = datetime.datetime.now().timestamp() * 1000
            elapsed = (now_timestamp - timer['start']) / 1000
            timer['elapsed'] += max(elapsed, 0)  # Prevent negative values
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
    app.run(debug=True)