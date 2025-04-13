from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin
import pandas as pd
import pickle
import mysql.connector

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Load trained model and expected column structure
model = pickle.load(open('model.pkl', 'rb'))
expected_columns = pickle.load(open('columns.pkl', 'rb'))

# MySQL connection config
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="electric_buses"
)
cursor = db.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS efficient_batteries (
        id INT AUTO_INCREMENT PRIMARY KEY,
        company_name VARCHAR(100),
        battery_model VARCHAR(100),
        manufacture_year INT,
        predicted_range FLOAT,
        efficiency_percent FLOAT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
db.commit()

# Preprocess form data
def preprocess_input(data):
    df = pd.DataFrame([{
        "Avg Speed (km/h)": data["avg_speed"],
        "Distance (km)": data["distance"],
        "Battery (kWh)": data["battery"],
        "Top Speed (km/h)": data["top_speed"],
        "Passenger Capacity": data["passenger"],
        "Road Type": data["road_type"],
        "Bus Type": data["bus_type"],
        "Charger Type": data["charger_type"],
    }])
    return df

# Match model input
def preprocess(df):
    df = pd.get_dummies(df, columns=["Road Type", "Bus Type", "Charger Type"])
    for col in expected_columns:
        if col not in df.columns:
            df[col] = 0
    return df[expected_columns]

@app.route("/")
def home():
    return "Backend running!"

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        raw_df = preprocess_input(data)
        df = preprocess(raw_df)

        prediction = model.predict(df)[0]
        max_range = 400
        efficiency_percent = round((prediction / max_range) * 100, 2)

        if prediction >= 250:
            efficiency = "Efficient"
        elif prediction >= 150:
            efficiency = "Moderate"
        else:
            efficiency = "Inefficient"

        return jsonify({
            "efficiency": efficiency,
            "predicted_range": round(prediction, 2),
            "efficiency_percent": efficiency_percent
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Updated /upload route using 'battery_model' instead of 'model_id'
@app.route("/upload", methods=["POST", "OPTIONS"])
@cross_origin(origin='http://localhost:8000', methods=['POST'], supports_credentials=True)
def upload():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    try:
        data = request.get_json()
        cursor.execute("""
            INSERT INTO efficient_batteries (company_name, battery_model, manufacture_year, efficiency_percent, predicted_range)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data["company"],             # Manufacturer company name
            data["battery_model"],       # Battery model ID (note: key changed from model_id to battery_model)
            data["year"],
            data["efficiency_percent"],
            data["predicted_range"]
        ))
        db.commit()
        return jsonify({"message": "Saved successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Updated /view route using 'battery_model'
@app.route("/view")
def view():
    cursor.execute("SELECT company_name, battery_model, manufacture_year, efficiency_percent, predicted_range FROM efficient_batteries")
    rows = cursor.fetchall()
    data = [{
        "company": row[0],
        "battery_model": row[1],
        "year": row[2],
        "efficiency_percent": row[3],
        "predicted_range": row[4]
    } for row in rows]
    return jsonify(data)

if __name__ == '__main__':
    app.run(port=5000)
