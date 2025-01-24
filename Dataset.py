from kaggle.api.kaggle_api_extended import KaggleApi
import zipfile

#Download the dataset
api = KaggleApi()
api.authenticate()
dataset_name = "niharika41298/gym-exercise-data"
download_path = "gym-exercise-data.zip"

# Download and extract
api.dataset_download_files(dataset_name, path=".", unzip=False)
print(f"Dataset downloaded to {download_path}")

with zipfile.ZipFile(download_path, "r") as zip_ref:
    zip_ref.extractall("./gym_exercise_data")

print("Dataset downloaded and extracted!")