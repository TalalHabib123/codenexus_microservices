from utils.rag.retrieval import retrieve_relevant_info_detection
from logger_config import get_logger

logger = get_logger(__name__)

def retrieve_relevant_docs_for_(task_type, processed_data, knowledge_base_detection, nn_model):
    relevant_docs = []
    return relevant_docs
    for file_path, codes in processed_data.items():
        for code in codes:
            try:
                relevant_docs.extend(retrieve_relevant_info_detection(task_type, code, knowledge_base_detection, nn_model))
            except Exception as e:
                logger.error(f"Error retrieving relevant documents for file: {file_path} for Job: {task_type}")
                logger.error(e)
                
    return relevant_docs