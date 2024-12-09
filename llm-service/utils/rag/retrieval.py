import sqlite3
import os
import joblib
from sklearn.neighbors import NearestNeighbors
import torch
from functools import lru_cache
from utils.rag.initial_data import INITIAL_DATA_DETECTION
from logger_config import get_logger
from transformers import AutoModel, AutoTokenizer

logger = get_logger(__name__)

# Load the model and tokenizer from Hugging Face
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

def mean_pooling(model_output, attention_mask):
    # Mean pooling: Take the mean of the token embeddings
    token_embeddings = model_output.last_hidden_state
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return (torch.sum(token_embeddings * input_mask_expanded, 1) / 
            torch.clamp(input_mask_expanded.sum(1), min=1e-9))

def encode_texts(texts):
    # Batch encode texts
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        model_output = model(**inputs)
    embeddings = mean_pooling(model_output, inputs['attention_mask'])
    return embeddings.cpu().numpy()

nn_cache = {}

@lru_cache(maxsize=1000)
def get_embedding(smell_code):
    # Encode the smell_code string and return the embedding
    embeddings = encode_texts([smell_code])
    return embeddings[0]

def clear_embedding_cache():
    get_embedding.cache_clear()

def clear_nn_cache():
    global nn_cache
    nn_cache.clear()

# File paths for saved models
EMBEDDINGS_FILE = 'knowledge_embeddings_detections.pkl'
NN_MODEL_FILE = 'nn_model.pkl'
DB_FILE = 'knowledge_base.db'

def initialize_knowledge_base_detection():
    # Ensure the database exists
    logger.info("Initializing knowledge base for detection")
    if not os.path.exists(DB_FILE):
        logger.info("Creating knowledge base database")
        create_knowledge_base_db()

    # Load knowledge base from database
    logger.info("Loading knowledge base from database")
    knowledge_base_detection = load_detection_knowledge_base()

    # Check if embeddings and model are saved
    logger.info("Checking for saved embeddings and model")
    if os.path.exists(EMBEDDINGS_FILE) and os.path.exists(NN_MODEL_FILE):
        logger.info("Loading embeddings and model from file")
        embeddings = joblib.load(EMBEDDINGS_FILE)
        nn_model = joblib.load(NN_MODEL_FILE)
    else:
        # Create embeddings
        logger.info("Creating embeddings and model")
        knowledge_texts = [f"{doc['smell']} {doc['example']}" for doc in knowledge_base_detection]
        embeddings = encode_texts(knowledge_texts)

        # Initialize NearestNeighbors model
        logger.info("Initializing NearestNeighbors model")
        nn_model = NearestNeighbors(n_neighbors=3, algorithm='auto', metric='cosine')
        nn_model.fit(embeddings)

        # Save embeddings and model
        logger.info("Saving embeddings and model to file")
        joblib.dump(embeddings, EMBEDDINGS_FILE)
        joblib.dump(nn_model, NN_MODEL_FILE)

    return knowledge_base_detection, nn_model, embeddings

def table_exists(cursor, table_name):
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return cursor.fetchone() is not None

def create_detection_table(cursor):
    cursor.execute('''
        CREATE TABLE knowledge_base_detection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            smell TEXT NOT NULL,
            example TEXT NOT NULL
        )
    ''')

    cursor.executemany('INSERT INTO knowledge_base_detection (smell, example) VALUES (?, ?)', INITIAL_DATA_DETECTION)

def create_knowledge_base_db():
    # Connect to SQLite database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if not table_exists(cursor, 'knowledge_base_detection'):
        create_detection_table(cursor)

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
    relevant_docs = [knowledge_base_detection[idx] for idx in indices[0] if knowledge_base_detection[idx]['smell'] == smell_type]
    nn_cache[smell_code] = relevant_docs

    return relevant_docs
