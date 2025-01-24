import pandas as pd

df = pd.read_csv("./gym_exercise_data/megaGymDataset.csv")
#print the all columns of the dataset
#print(data.columns)
df = df.drop(columns=['Unnamed: 0'], errors='ignore')

print("Missing values:\n", df.isnull().sum())

df = df.dropna()

df['Type'] = df['Type'].str.lower()
df['BodyPart'] = df['BodyPart'].str.lower()
df['Equipment'] = df['Equipment'].str.lower()
df['Level'] = df['Level'].str.lower()

print(df.head())

#Group by Bodypart