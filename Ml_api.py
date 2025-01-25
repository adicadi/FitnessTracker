from flask import Flask, request, jsonify
import pandas as pd
import xgboost as xgb
import joblib

app = Flask(__name__)

# Load the trained XGBoost model
model = joblib.load('xgboost_model.pkl')

# Load the dataset
merged_dataset = pd.read_csv('merged_dataset.csv')

# Standardize dataset columns (Goal and BodyPart)
merged_dataset['Goal'] = merged_dataset['Goal'].str.lower().str.strip()
merged_dataset['BodyPart'] = merged_dataset['BodyPart'].str.lower().str.strip()


@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Parse input JSON data
        data = request.json
        age = data['age']
        weight = data['weight']
        goal = data['goal'].strip().lower()
        body_part = data['body_part'].strip().lower()

        # Prepare input features for the model
        input_data = pd.DataFrame([{
            'Age': age,
            'Weight (kg)': weight,
            'BMI': weight / (1.75 ** 2),
            'Workout_Type': 0,
            'Level': 1,
            'Weight_BMI_Ratio': weight / (weight / (1.75 ** 2)),
            'Calories_Burned': 500
        }])
        dmatrix = xgb.DMatrix(input_data)
        predicted_class = int(model.predict(dmatrix)[0])

        # Map predicted class to Type
        type_mapping = {
            0: "Cardio",
            1: "Strength",
            2: "Flexibility",
            3: "Yoga"
        }
        mapped_class = type_mapping.get(predicted_class, None)
        print("Predicted Class (numeric):", predicted_class)
        print("Mapped Predicted Class (Type):", mapped_class)

        # Filter dataset by Goal, BodyPart, and Type
        filtered_data = merged_dataset[
            (merged_dataset['Goal'] == goal) &
            (merged_dataset['BodyPart'] == body_part) &
            (merged_dataset['Type'].str.lower() == mapped_class.lower())
        ]
        print("Filtered Data Count:", len(filtered_data))

        # Sort, remove duplicates, and pick top 5
        recommendations = (
            filtered_data.sort_values(by=['Rating', 'Calories_Burned'], ascending=[False, False])
            .drop_duplicates(subset='Title')
            .head(5)
        )

        # If no matches, provide fallback recommendations
        if filtered_data.empty:
            print("No matches found. Providing fallback recommendations.")
            fallback_data = merged_dataset[
                (merged_dataset['Goal'] == goal) &
                (merged_dataset['BodyPart'] == body_part)
            ].sort_values(by='Rating', ascending=False)

            # Provide exercises for different levels
            beginner = fallback_data[fallback_data['Level'] == 'beginner'].head(2)
            intermediate = fallback_data[fallback_data['Level'] == 'intermediate'].head(2)
            advanced = fallback_data[fallback_data['Level'] == 'advanced'].head(1)

            fallback_data = pd.concat([beginner, intermediate, advanced]).drop_duplicates(subset='Title')
            fallback_result = fallback_data[['Title', 'Desc', 'Equipment']].to_dict(orient='records')
            return jsonify({
                'recommendations': fallback_result,
                'message': 'No exact match found. Showing diverse recommendations for the selected body part.'
            })

        # Return recommendations
        result = recommendations[['Title', 'Desc', 'Equipment']].to_dict(orient='records')
        return jsonify({'recommendations': result})

    except Exception as e:
        # Handle exceptions
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
