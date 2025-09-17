import pandas as pd
from pymongo import MongoClient

# 1. Your MongoDB Atlas Connection String
# IMPORTANT: Replace the placeholders with your actual username and password
connection_string = "mongodb+srv://prarabdhapandey696_db_user:Golu123Golu@constitutionbotcluster.d4pdxfq.mongodb.net/?retryWrites=true&w=majority&appName=ConstitutionBotCluster"

# 2. Your existing code to load the data from the URL
url = "https://huggingface.co/datasets/Sharathhebbar24/Indian-Constitution/raw/main/Final_IC.csv"
df = pd.read_csv(url)

# 3. Connect to MongoDB Atlas
client = MongoClient(connection_string)

# 4. Access the database and collection
# MongoDB will automatically create these if they don't exist
db = client.constitution_db
collection = db.articles

# 5. Convert the DataFrame to a list of dictionaries and insert
records = df.to_dict('records')
collection.insert_many(records)

print("Data successfully ingested into MongoDB!") 