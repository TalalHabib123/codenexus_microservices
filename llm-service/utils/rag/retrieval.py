import sqlite3
import os
import joblib
from sklearn.neighbors import NearestNeighbors
from sentence_transformers import SentenceTransformer
from functools import lru_cache

# Initialize the retrieval model
retrieval_model = SentenceTransformer('all-MiniLM-L6-v2')

nn_cache = {}

@lru_cache(maxsize=10000)
def get_embedding(smell_code):
    # Encode the smell_code string and return the embedding
    embedding = retrieval_model.encode([smell_code])[0]
    return embedding

def clear_embedding_cache():
    get_embedding.cache_clear()

def clear_nn_cache():
    global nn_cache
    nn_cache.clear()


# File paths for saved models
EMBEDDINGS_FILE = 'knowledge_embeddings.pkl'
NN_MODEL_FILE = 'nn_model.pkl'
DB_FILE = 'knowledge_base.db'

def initialize_knowledge_base_detection():
    # Ensure the database exists
    if not os.path.exists(DB_FILE):
        create_detection_knowledge_base_db()

    # Load knowledge base from database
    knowledge_base_detection = load_detection_knowledge_base()

    # Check if embeddings and model are saved
    if os.path.exists(EMBEDDINGS_FILE) and os.path.exists(NN_MODEL_FILE):
        embeddings = joblib.load(EMBEDDINGS_FILE)
        nn_model = joblib.load(NN_MODEL_FILE)
    else:
        # Create embeddings
        knowledge_texts = [f"{doc['smell']} {doc['example']}" for doc in knowledge_base_detection]
        embeddings = retrieval_model.encode(knowledge_texts)

        # Initialize NearestNeighbors model
        nn_model = NearestNeighbors(n_neighbors=3, algorithm='auto', metric='cosine')
        nn_model.fit(embeddings)

        # Save embeddings and model
        joblib.dump(embeddings, EMBEDDINGS_FILE)
        joblib.dump(nn_model, NN_MODEL_FILE)

    return knowledge_base_detection, nn_model, embeddings

def create_detection_knowledge_base_db():
    # Connect to SQLite database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE knowledge_base_detection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            smell TEXT NOT NULL,
            example TEXT NOT NULL
        )
    ''')

    # Insert initial data
    initial_data = [
        ('Long Function', 'def long_function():\n    # Imagine a very long function here\n    pass'),
        ('God Object', 'class GodObject:\n    # Too many responsibilities\n    pass'),
        # Add other code smells here
    ]

    cursor.executemany('INSERT INTO knowledge_base_detection (smell, example) VALUES (?, ?)', initial_data)
    conn.commit()
    conn.close()

def load_detection_knowledge_base():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('SELECT smell, example FROM knowledge_base_detection')
    rows = cursor.fetchall()
    conn.close()

    knowledge_base = [{'smell': row[0], 'example': row[1]} for row in rows]
    return knowledge_base

def add_detection_knowledge_base_entry(entry):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        'INSERT INTO knowledge_base_detection (smell, example) VALUES (?, ?)',
        (entry['smell'], entry['example'])
    )
    conn.commit()
    conn.close()

    # Remove old embeddings and model so they can be rebuilt
    if os.path.exists(EMBEDDINGS_FILE):
        os.remove(EMBEDDINGS_FILE)
    if os.path.exists(NN_MODEL_FILE):
        os.remove(NN_MODEL_FILE)
        
    clear_embedding_cache()
    clear_nn_cache()

def retrieve_relevant_info_detection(smell_type, code_snippet, knowledge_base_detection, nn_model, top_k=3):
    # Combine smell_type and code_snippet into a single string
    smell_code = f"{smell_type} {code_snippet}"

    # Check if the nearest neighbor result is cached
    if smell_code in nn_cache:
        return nn_cache[smell_code]

    code_embedding = get_embedding(smell_code)

    code_embedding = code_embedding.reshape(1, -1)

    distances, indices = nn_model.kneighbors(code_embedding, n_neighbors=top_k)
    relevant_docs = [knowledge_base_detection[idx] for idx in indices[0]]
    nn_cache[smell_code] = relevant_docs

    return relevant_docs

