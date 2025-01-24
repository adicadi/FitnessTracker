import datetime
import sqlite3
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify


app = Flask(__name__)
@app.route('/')
def home():
    return "<h1>Fitness Tracker API</h1><p>Welcome to the Fitness Tracker API. Use the available endpoints to interact with the system.</p>"

#Database Connection
def get_db_connection():
    conn = sqlite3.connect("fitness_tracker.db")
    conn.row_factory = sqlite3.Row
    return conn

#Register User
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    name = data['name']
    age = data['age']
    weight = data['weight']
    height = data['height']
    goal = data['goal']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                    INSERT INTO user_data(name, age, weight, height, goal)
                    VALUES (?, ?, ?, ?, ?)
                    """, (name, age, weight, height, goal))
    conn.commit()
    conn.close()
    return jsonify({"message": f"User{name} registered successfully."}), 201

@app.route('/register_from_query', methods=['GET'])
def register_from_query():
    name = request.args.get('name')
    age = request.args.get('age')
    weight = request.args.get('weight')
    height = request.args.get('height')
    goal = request.args.get('goal')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                    INSERT INTO user_data(name, age, weight, height, goal)
                    VALUES (?, ?, ?, ?, ?)
                    """, (name, age, weight, height, goal))
    conn.commit()
    conn.close()
    return jsonify({"message": f"User {name} registered successfully.",
                    "user":{
                        "name": name,
                        "age": age,
                        "weight": weight,
                        "height": height,
                        "goal": goal
                        }}), 201

@app.route('/log_workout', methods=['POST'])
def log_workout():
    data = request.json
    exercise = data['exercise']
    sets = data['sets']
    reps = data['reps']
    weight = data['weight']
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                    INSERT INTO workout_logs(date, exercise, sets, reps, weight)
                    VALUES (?, ?, ?, ?, ?)
                    """, (date, exercise, sets, str(reps), str(weight)))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Workout logged: {exercise}, {sets} sets of {reps} reps at {weight} kg"}), 201

#Fetch Progress
@app.route('/progress', methods=['GET'])
def fetch_progress():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workout_logs")
    workouts = cursor.fetchall()
    conn.close()
    return jsonify([dict(workout) for workout in workouts]), 200


#Setup Database
@app.before_request
def setup_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_data(
                        name TEXT,
                        age INTEGER,
                        weight REAL,
                        height REAL,
                        goal TEXT
                        )""")
    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS workout_logs(
                        date TEXT,
                        exercise TEXT,
                        sets INTEGER,
                        reps TEXT,
                        weight TEXT
                        )""")
    conn.commit()
    conn.close()
    
@app.route('/debug', methods=['GET'])
def debug():
    data = {
        "message": "User name registered successfully.",
                    "user":{
                        "name": "name",
                        "age": "age",
                        "weight": "weight",
                        "height": "height",
                        "goal": "goal"
    }}
    return jsonify(data)

    
if __name__ == "__main__":
    app.run(debug=True)


