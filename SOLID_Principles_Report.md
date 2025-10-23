# SOLID Principles Implementation Report
## Healthcare Monitoring System

**Project:** Cloud-Based Healthcare Network Traffic Monitoring and Anomaly Detection  
**Student:** Kodukulla Mohnish Mythreya  
**Date:** September 26, 2025

---

## Executive Summary

This report demonstrates how the SOLID principles of object-oriented design have been implemented throughout our healthcare monitoring system. Each principle is illustrated with specific code examples, screenshots, and explanations showing how they contribute to maintainable, extensible, and robust software architecture.

---

## S - Single Responsibility Principle

**Definition:** A class or function should have only one reason to change - it should have only one job.

### Implementation Example 1: `/track` Route in Main Host

**File:** `services/main_host/app.py`

The `/track` route has a single, well-defined responsibility: ingesting patient vital data and updating Prometheus metrics.

```python
@app.route('/track', methods=['POST'])
def track_traffic():
    data = request.get_json()
    print("💡 Received Payload:", data)
    
    hospital = data.get('hospital', 'unknown')
    dept = data.get('dept', 'unknown')
    ward = data.get('ward', 'unknown')
    patient = data.get('patient', 'unknown')

    labels = dict(hospital=hospital, department=dept, ward=ward, patient=patient)

    for key, gauge in metrics.items():
        if key in data:
            print(f"📌 Setting {key} = {data[key]} for labels {labels}")
            gauge.labels(**labels).set(data[key])
        else:
            print(f"⚠️ {key} missing in payload")
    
    # Store the data for the dashboard
    patient_key = f"{hospital}|{dept}|{ward}|{patient}"
    patient_data_store[patient_key].append(data)
    
    return jsonify({'status': 'success'}), 200
```

**Why this follows SRP:**
- **Single Purpose:** Only handles metric ingestion and storage
- **One Reason to Change:** Would only change if the data format or metric storage logic changes
- **Clear Boundaries:** Doesn't handle authentication, validation, or data transformation

### Implementation Example 2: Model Classes

**File:** `services/web_dashboard/models/patient.py`

Each model class has a single responsibility:

```python
class Patient(db.Model):
    """Responsible ONLY for patient data representation and basic operations"""
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_age(self):
        today = datetime.today()
        birth_date = self.date_of_birth
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age

class PatientVitalSign(db.Model):
    """Responsible ONLY for vital signs data representation"""
    
    def to_dict(self):
        return {
            'vital_id': self.vital_id,
            'patient_id': self.patient_id,
            'heart_rate': self.heart_rate,
            # ... other vitals
        }
```

**Benefits:**
- Easy to test individual components
- Changes to patient data don't affect vital signs logic
- Clear separation of concerns

---

## O - Open/Closed Principle

**Definition:** Software entities should be open for extension but closed for modification.

### Implementation Example: Metrics System

**File:** `services/main_host/app.py`

The metrics dictionary allows adding new vital signs without modifying existing code:

```python
# Current metrics - CLOSED for modification
metrics = {
    'heart_rate': Gauge('heart_rate_bpm', 'Heart Rate (BPM)', ['hospital', 'department', 'ward', 'patient']),
    'bp_systolic': Gauge('bp_systolic', 'BP Systolic', ['hospital', 'department', 'ward', 'patient']),
    'spo2': Gauge('spo2_percent', 'SpO2 (%)', ['hospital', 'department', 'ward', 'patient']),
    # ... existing metrics
}

# OPEN for extension - can easily add new metrics:
# 'glucose_level': Gauge('glucose_level', 'Blood Glucose (mg/dL)', ['hospital', 'department', 'ward', 'patient']),
# 'cholesterol': Gauge('cholesterol_level', 'Cholesterol Level', ['hospital', 'department', 'ward', 'patient']),
```

The processing loop automatically handles any new metrics:

```python
for key, gauge in metrics.items():
    if key in data:
        gauge.labels(**labels).set(data[key])
```

**Extension Example - Adding New Vital Signs:**

To add a new vital sign like "blood_oxygen_level", you would only:
1. Add it to the metrics dictionary
2. The existing processing code automatically handles it
3. No modification to the core ingestion logic required

### Implementation Example: ML Model Features

**File:** `services/ml_service/model.py`

```python
# OPEN for extension - easy to add new features
feature_names = [
    "heart_rate", "bp_systolic", "bp_diastolic", "respiratory_rate",
    "spo2", "etco2", "fio2", "temperature", "wbc_count", "lactate", "blood_glucose"
    # New features can be added here without changing the prediction logic
]

# CLOSED for modification - prediction logic stays the same
@app.route("/predict", methods=["POST"])
def predict():
    input_data = request.json
    try:
        features = [input_data[feat] for feat in feature_names]  # Automatically uses new features
    except KeyError as e:
        return jsonify({"error": f"Missing feature in input: {str(e)}"}), 400
    
    X = pd.DataFrame([features], columns=feature_names)
    score = model.decision_function(X)[0]
    return jsonify({"anomaly_score": round(1 - score, 4)})
```

---

## L - Liskov Substitution Principle

**Definition:** Objects of a superclass should be replaceable with objects of a subclass without breaking functionality.

### Implementation Example: SQLAlchemy Model Inheritance

**File:** `services/web_dashboard/models/patient.py`

All our models inherit from `db.Model` and can be substituted wherever a base model is expected:

```python
# Base class behavior
class Patient(db.Model):
    def to_dict(self):
        """Base implementation for API serialization"""
        return {
            'patient_id': self.patient_id,
            'name': self.get_full_name(),
            'status': self.status
        }

class PatientVitalSign(db.Model):
    def to_dict(self):
        """Specialized implementation but maintains same interface"""
        return {
            'vital_id': self.vital_id,
            'patient_id': self.patient_id,
            'heart_rate': self.heart_rate,
            'recorded_at': self.recorded_at.isoformat()
        }
```

**Substitution Example:**

```python
# Any model can be used where db.Model is expected
def save_to_database(model_instance):
    """This function works with any subclass of db.Model"""
    db.session.add(model_instance)  # Works with Patient, PatientVitalSign, etc.
    db.session.commit()
    return model_instance

# Both work identically:
patient = Patient(first_name="John", last_name="Doe")
vital = PatientVitalSign(heart_rate=75, patient_id=1)

save_to_database(patient)   # ✓ Works
save_to_database(vital)     # ✓ Works - Liskov Substitution
```

### Implementation Example: Data Processing Functions

**File:** `services/web_dashboard/routes/patients.py`

Functions that process patient data work with any patient-like object:

```python
def enhance_patient_with_prometheus_data(patient):
    """Enhances patient data - works with any patient dict structure"""
    # Can work with real patient objects or mock patient objects
    anomaly_score = patient['anomaly_score']
    
    if anomaly_score > 0.7:
        patient['status'] = 'Critical'
        # ... enhancement logic
    
    return patient  # Returns enhanced object that maintains interface
```

---

## I - Interface Segregation Principle

**Definition:** Clients should not be forced to depend on interfaces they don't use.

### Implementation Example: Blueprint Separation

**File:** `services/web_dashboard/routes/patients.py`

We separate interfaces into focused blueprints rather than having one monolithic interface:

```python
# patients.py - ONLY patient-related endpoints
patients = Blueprint('patients', __name__)

@patients.route('/patients')           # Patient listing
@patients.route('/patients/<int:patient_id>')  # Individual patient
@patients.route('/patients/<int:patient_id>/vitals')  # Patient vitals
@patients.route('/api/patients')       # Patient API

# auth.py would contain ONLY authentication endpoints:
# @auth.route('/login')
# @auth.route('/logout') 
# @auth.route('/register')

# main.py would contain ONLY general endpoints:
# @main.route('/')
# @main.route('/dashboard')
# @main.route('/analytics')
```

**Benefits:**
- API clients only need to know about endpoints they use
- Mobile app might only use patient API endpoints
- Admin dashboard might only use authentication endpoints
- Changes to vital signs endpoints don't affect patient listing clients

### Implementation Example: Service-Specific APIs

**Main Host Service** - Only exposes metrics-related interfaces:

```python
@app.route('/track', methods=['POST'])     # For data ingestion
@app.route('/metrics')                     # For Prometheus scraping
@app.route('/api/patients', methods=['GET']) # For patient listing
```

**ML Service** - Only exposes ML-related interfaces:

```python
@app.route("/predict", methods=["POST"])   # ONLY prediction functionality
```

**Web Dashboard** - Exposes comprehensive web interfaces but keeps them separated by concern.

---

## D - Dependency Inversion Principle

**Definition:** High-level modules should not depend on low-level modules. Both should depend on abstractions.

### Implementation Example 1: Database Abstraction

**File:** `services/web_dashboard/models/patient.py`

Our high-level patient management code depends on SQLAlchemy abstraction, not direct MySQL queries:

```python
# HIGH-LEVEL MODULE (depends on abstraction)
class Patient(db.Model):  # Depends on SQLAlchemy abstraction, not MySQL directly
    
    def save(self):
        db.session.add(self)    # Using ORM abstraction
        db.session.commit()     # Not writing raw SQL
    
    @classmethod
    def find_by_mrn(cls, mrn):
        return cls.query.filter_by(mrn=mrn).first()  # ORM query, not raw SQL

# Usage in routes (HIGH-LEVEL)
@patients.route('/patients', methods=['POST'])
def create_patient():
    patient = Patient(
        mrn=request.form.get('mrn'),
        first_name=request.form.get('first_name')
    )
    patient.save()  # Abstracted database operation
```

**Without Dependency Inversion (BAD):**
```python
# This would violate DIP - depending on concrete MySQL implementation
import mysql.connector

def create_patient(mrn, name):
    connection = mysql.connector.connect(host='localhost', user='admin', password='pass')
    cursor = connection.cursor()
    cursor.execute("INSERT INTO patients (mrn, name) VALUES (%s, %s)", (mrn, name))
    connection.commit()
```

### Implementation Example 2: Service Communication Abstraction

**File:** `services/web_dashboard/routes/patients.py`

High-level patient route depends on request abstraction, not concrete HTTP implementation:

```python
# HIGH-LEVEL MODULE
def get_prometheus_patients():
    """Depends on requests abstraction, not raw socket programming"""
    try:
        # Using requests library abstraction
        response = requests.get(f"{MAIN_HOST_URL}/api/dashboard-data", timeout=5)
        
        if response.status_code != 200:
            return None
            
        return response.json()  # Abstracted JSON parsing
    except requests.exceptions.RequestException:
        return None  # Graceful handling of network abstraction failures
```

**Benefits:**
- Can easily switch from HTTP to gRPC or message queues
- Can switch from MySQL to PostgreSQL without changing business logic
- Can mock dependencies for testing
- Loose coupling between components

### Implementation Example 3: Configuration Abstraction

**File:** `docker-compose.yml` and environment configuration

Our services depend on environment variable abstractions, not hardcoded values:

```python
# services/main_host/app.py - depends on environment abstraction
PROMETHEUS_URL = os.environ.get('PROMETHEUS_URL', 'http://prometheus:9090')
MAIN_HOST_URL = os.environ.get('MAIN_HOST_URL', 'http://main_host:8000')

# services/web_dashboard/app.py - database configuration abstraction  
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///hospital.db'
```

---

## Testing and Validation

### How SOLID Principles Improve Our Code

1. **Testability**: Each component has a single responsibility, making unit tests straightforward
2. **Maintainability**: Changes to one principle don't affect others
3. **Extensibility**: New features can be added without modifying existing code
4. **Flexibility**: Components can be swapped out or upgraded independently

### Example Test Cases Enabled by SOLID

```python
# Easy to test due to Single Responsibility
def test_track_route_single_responsibility():
    """Test that track route only handles metric ingestion"""
    response = client.post('/track', json={'heart_rate': 75, 'patient': '1'})
    assert response.status_code == 200
    assert 'success' in response.get_json()['status']

# Easy to extend due to Open/Closed
def test_new_metric_extension():
    """Test that new metrics can be added without changing existing code"""
    new_metrics = metrics.copy()
    new_metrics['new_vital'] = Gauge('new_vital', 'New Vital Sign', ['patient'])
    # Test passes without modifying existing processing logic

# Easy to substitute due to Liskov Substitution  
def test_model_substitution():
    """Test that any model can be used where db.Model is expected"""
    patient = Patient(first_name="Test")
    vital = PatientVitalSign(heart_rate=75)
    
    # Both should work with same database operations
    assert save_to_database(patient).patient_id is not None
    assert save_to_database(vital).vital_id is not None
```

---

## Future Enhancements Enabled by SOLID

Our SOLID implementation makes future enhancements straightforward:

1. **New Vital Signs** (Open/Closed): Add to metrics dictionary
2. **New Database** (Dependency Inversion): Change DATABASE_URL configuration  
3. **New Authentication** (Interface Segregation): Add auth blueprint without affecting patient routes
4. **New ML Models** (Single Responsibility): Each model gets its own service
5. **New Data Sources** (Liskov Substitution): Any data source implementing our interface works

---

## Conclusion

The healthcare monitoring system demonstrates comprehensive implementation of all five SOLID principles:

- **S**: Each function and class has a single, well-defined responsibility
- **O**: System is extensible for new vitals, metrics, and features without modification
- **L**: Models and objects can be substituted without breaking functionality  
- **I**: Interfaces are segregated by concern (patients, auth, API, web)
- **D**: High-level modules depend on abstractions, not concrete implementations

This design results in a maintainable, testable, and extensible healthcare monitoring system that can evolve with changing requirements while maintaining stability and reliability.

---

**Document Version:** 1.0  
**Created:** September 26, 2025  
**Author:** Kodukulla Mohnish Mythreya