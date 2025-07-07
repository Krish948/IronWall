from flask import Flask, request, jsonify
from threading import Thread, Event
import time

app = Flask(__name__)

scan_state = {
    'total_files': 100,
    'files_scanned': 0,
    'threats_found': 0,
    'current_file': '',
    'status': 'idle',
    'results': [],
    'paused': False,
    'stopped': False
}
scan_thread = None
scan_event = Event()

# Demo scan logic (fake scan)
def scan_job():
    scan_state['status'] = 'scanning'
    scan_state['files_scanned'] = 0
    scan_state['threats_found'] = 0
    scan_state['results'] = []
    scan_state['stopped'] = False
    for i in range(scan_state['total_files']):
        if scan_state['stopped']:
            scan_state['status'] = 'stopped'
            break
        while scan_state['paused']:
            scan_state['status'] = 'paused'
            time.sleep(0.2)
        scan_state['status'] = 'scanning'
        scan_state['files_scanned'] = i + 1
        scan_state['current_file'] = f"file_{i+1}.txt"
        if (i+1) % 17 == 0:
            scan_state['threats_found'] += 1
            scan_state['results'].append({
                'file_name': f"file_{i+1}.txt",
                'full_path': f"/fake/path/file_{i+1}.txt",
                'file_size': f"{round(0.5 + i*0.01, 2)} MB",
                'file_type': 'Text',
                'threat_type': 'Demo Threat',
                'status': 'Threat Found'
            })
        else:
            scan_state['results'].append({
                'file_name': f"file_{i+1}.txt",
                'full_path': f"/fake/path/file_{i+1}.txt",
                'file_size': f"{round(0.5 + i*0.01, 2)} MB",
                'file_type': 'Text',
                'threat_type': 'Clean',
                'status': 'Scanned'
            })
        time.sleep(0.07)
    scan_state['status'] = 'finished'
    scan_state['current_file'] = ''

@app.route('/start_scan', methods=['POST'])
def start_scan():
    global scan_thread
    if scan_state['status'] == 'scanning':
        return jsonify({'message': 'Scan already running'}), 400
    scan_state['paused'] = False
    scan_state['stopped'] = False
    scan_thread = Thread(target=scan_job, daemon=True)
    scan_thread.start()
    return jsonify({'message': 'Scan started'})

@app.route('/stop_scan', methods=['POST'])
def stop_scan():
    scan_state['stopped'] = True
    scan_state['status'] = 'stopped'
    return jsonify({'message': 'Scan stopped'})

@app.route('/pause_scan', methods=['POST'])
def pause_scan():
    scan_state['paused'] = True
    scan_state['status'] = 'paused'
    return jsonify({'message': 'Scan paused'})

@app.route('/resume_scan', methods=['POST'])
def resume_scan():
    scan_state['paused'] = False
    scan_state['status'] = 'scanning'
    return jsonify({'message': 'Scan resumed'})

@app.route('/progress', methods=['GET'])
def progress():
    # Return a summary and the last 20 results for demo
    return jsonify({
        'total_files': scan_state['total_files'],
        'files_scanned': scan_state['files_scanned'],
        'threats_found': scan_state['threats_found'],
        'current_file': scan_state['current_file'],
        'status': scan_state['status'],
        'results': scan_state['results'][-20:]
    })

if __name__ == '__main__':
    app.run(debug=True) 