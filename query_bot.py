import os
import pymongo
import certifi
from urllib.parse import quote_plus
from sentence_transformers import SentenceTransformer
import google.generativeai as genai # <-- CHANGED IMPORT

# --- 1. SETUP ---

# Configure the Google Gemini client using the environment variable
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    llm_client = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print("Error initializing Google Gemini client. Make sure your GOOGLE_API_KEY is set.")
    print(f"Error details: {e}")
    exit()

# Initialize the embedding model (this stays the same)
print("🧠 Loading embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Model loaded.")

# --- MongoDB Connection ---
USERNAME = "prarabdhapandey696_db_user"
PASSWORD = "Golu123Golu"
CLUSTER_URL = "constitutionbotcluster.d4pdxfq.mongodb.net"

encoded_password = quote_plus(PASSWORD)
connection_string = f"mongodb+srv://{USERNAME}:{encoded_password}@{CLUSTER_URL}/?retryWrites=true&w=majority"
ca = certifi.where()
db_client = pymongo.MongoClient(connection_string, tlsCAFile=ca)
db = db_client.constitution_db
collection = db.vectors

print("✅ Connected to MongoDB!")


# --- 2. THE RAG FUNCTION ---

# This is the updated, simpler function for query_bot.py

def answer_question(question, num_sources):
    """
    This function now uses a default model and accepts the number of sources.
    """
    
    # The model is now hardcoded to the fast and efficient 'flash' version.
    llm_client = genai.GenerativeModel('gemini-1.5-flash')
    
    question_embedding = embedding_model.encode(question)

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": question_embedding.tolist(),
                "numCandidates": 150,
                "limit": num_sources # Use the value from the sidebar
            }
        },
        {
            "$project": {
                "_id": 0, "text_chunk": 1, "source_title": 1, "score": { "$meta": "vectorSearchScore" }
            }
        }
    ]

    search_results = list(collection.aggregate(pipeline))

    if not search_results:
        return "I'm sorry, I couldn't find any relevant information in the constitution to answer your question.", None

    context = "\n---\n".join([result['text_chunk'] for result in search_results])
    
    prompt_template = f"""
    You are an expert bot on the Constitution of India.
    Your task is to answer the user's question based *only* on the following context retrieved from the constitutional text.
    Do not use any outside knowledge. If the context is not sufficient to answer the question, say so.

    CONTEXT:
    {context}

    USER'S QUESTION:
    {question}

    ANSWER:
    """

    print(f"\n🔍 Found context, asking the LLM to generate an answer...")
    try:
        response = llm_client.generate_content(prompt_template)
        return response.text, search_results
    except Exception as e:
        return f"An error occurred while generating the answer: {e}", None

    # --- CHANGED LLM CALL ---
    print("\n🔍 Found context, asking Google Gemini to generate an answer...")
    try:
        response = llm_client.generate_content(prompt_template)
        return response.text
    except Exception as e:
        return f"An error occurred while generating the answer with Google Gemini: {e}"
    # --- END OF CHANGES ---


# --- 3. MAIN EXECUTION LOOP (INTERACTIVE VERSION) ---
if __name__ == "__main__":
    print("\n--- AI Constitution Bot ---")
    print("Ask a question, or type 'exit' to quit.")
    while True:
        user_question = input("\nYour Question: ")
        if user_question.lower() == 'exit':
            break
        
        answer = answer_question(user_question)
        print(f"\nANSWER:\n{answer}")

    print("\nGoodbye!")
    db_client.close()