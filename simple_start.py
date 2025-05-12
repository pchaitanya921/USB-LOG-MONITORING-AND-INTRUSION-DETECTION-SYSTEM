from flask import Flask, jsonify, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'usb_monitor.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "status": "running",
        "message": "Simple USB Monitoring System is running"
    })

if __name__ == '__main__':
    print("Starting simple USB Monitoring System...")
    print("Web interface available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0')
