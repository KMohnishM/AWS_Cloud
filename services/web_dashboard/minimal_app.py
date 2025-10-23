from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Minimal Flask App Working"

@app.route('/api/patients')
def get_test_patients():
    """Return test patient data"""
    # Generate 15 test patients
    test_data = []
    for i in range(1, 16):
        test_data.append({
            "patient_id": f"patient-{i}",
            "status": "Normal" if i < 10 else ("Warning" if i < 13 else "Critical")
        })
    
    return jsonify({
        "status": "success", 
        "data": {"patients": test_data}
    })

if __name__ == '__main__':
    print("Starting minimal Flask app on port 5000")
    app.run(host='0.0.0.0', port=5000)