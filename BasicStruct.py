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
    
@app.route('/all_users', methods=['GET'])
def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_data")
    user_data = cursor.fetchone()
    user_dict = {
        "name": user_data[0],
        "age": user_data[1],
        "weight": user_data[2],
        "height": user_data[3],
        "goal": user_data[4],
    } if user_data else {}
    
    #Fetch workout logs
    cursor.execute("SELECT * FROM workout_logs")
    workout_logs = cursor.fetchall()
    workout_list = [
        {
            "date": workout[0],
            "exercise": workout[1],
            "sets": workout[2],
            "reps": workout[3],
            "weight": workout[4]
        } for workout in workout_logs
    ]
    
    conn.close()
    
    #Combine user data and workout logs
    response_data = {
        "user_data": user_dict,
        "workout_logs": workout_list
    }
    return jsonify(response_data)
    
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


