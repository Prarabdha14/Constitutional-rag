import time
from urllib.parse import quote_plus
from pymongo import MongoClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import certifi

# --- 1. MongoDB Connection ---
USERNAME = "prarabdhapandey696_db_user"
PASSWORD = "Golu123Golu"
CLUSTER_URL = "constitutionbotcluster.d4pdxfq.mongodb.net"

encoded_password = quote_plus(PASSWORD)
connection_string = f"mongodb+srv://{USERNAME}:{encoded_password}@{CLUSTER_URL}/?retryWrites=true&w=majority"
ca = certifi.where()
client = MongoClient(connection_string, tlsCAFile=ca)
db = client.constitution_db
source_collection = db.articles
dest_collection = db.vectors

print("✅ Connected to MongoDB!")

# --- 2. Initialize Models ---
print("🧠 Loading embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Model loaded.")

# --- 3. Chunking and Embedding Pipeline ---
try:
    dest_collection.delete_many({})
    print("Cleared existing data from destination collection.")

    articles = list(source_collection.find())
    print(f"Found {len(articles)} articles to process.")
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    for article in articles:
        # CORRECTED PART 1: Check for 'article_desc' instead of 'Text'
        if 'article_desc' in article and article['article_desc']:
            
            # CORRECTED PART 2: Get the text from the 'article_desc' field
            chunks = text_splitter.split_text(article['article_desc'])
            embeddings = embedding_model.encode(chunks)

            docs_to_insert = []
            for i, chunk in enumerate(chunks):
                new_doc = {
                    # CORRECTED PART 3: Use 'article_id' as the source identifier
                    "source_title": f"Article {article.get('article_id')}",
                    "text_chunk": chunk,
                    "embedding": embeddings[i].tolist()
                }
                docs_to_insert.append(new_doc)

            if docs_to_insert:
                dest_collection.insert_many(docs_to_insert)

    print("\n🎉 Successfully chunked and embedded all documents!")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    client.close()
    print("Connection closed.")