import os
import requests
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Document
from flask import current_app
from flaskr.db import query_db

def enhance_with_llm(text):
    """
    Enhances the provided text using the OpenAI GPT-3.5 API.
    """
    # Retrieve the OpenAI API key from environment variables
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '<ERROR>')

    llm_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": f"Rephrase the following content into a brief answer of 5 lines: {text}"}
        ],
        "max_tokens": 150,
    }

    response = requests.post(llm_url, headers=headers, json=data)

    if response.status_code == 200:
        enhanced_text = response.json().get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        return enhanced_text
    else:
        return f"Error enhancing content: {response.status_code}"

def enhance_with_llm_rag(query, content):
    """
    Enhances the provided text using the OpenAI GPT-3.5 API.
    """
    # Retrieve the OpenAI API key from environment variables
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '<ERROR>')

    llm_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": f"Answer the following query in a short brief: {query} using this content: {content}"}
        ],
        "max_tokens": 150,
    }

    response = requests.post(llm_url, headers=headers, json=data)

    if response.status_code == 200:
        enhanced_text = response.json().get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        return enhanced_text
    else:
        return f"Error enhancing content: {response.status_code}"

def test_openai_api():
    """
    Tests the OpenAI API connection and prints a response.
    """
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '<ERROR>')
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello to the world"}
        ],
        "max_tokens": 50,
    }
    
    response = requests.post(url, headers=headers, json=data)

def embed_text(text):
    try: 
        OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', '<ERROR>')
        embed_model = OpenAIEmbedding(model=OPENAI_EMBEDDING_MODEL)
        embedding = embed_model.get_text_embedding(text)
        return embedding
    except Exception as error:
        current_app.logger.error(f"Error embedding doc: {error}")

def chunk_text(text):
    try:
        OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', '<ERROR>')
        embed_model = OpenAIEmbedding(model=OPENAI_EMBEDDING_MODEL)
        splitter = SemanticSplitterNodeParser(
            buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
        )
        nodes = splitter.get_nodes_from_documents([Document(text=text)])
        chunks = [node.get_content() for node in nodes]
        return chunks
    except Exception as error:
        current_app.logger.error(f"Error chunking text: {error}")
    
def process_query(text):
    # Generate the query embedding
    query_vector = embed_text(text)
    return query_vector

def query_pinecone(text):
    response = ""
    query_vector = process_query(text)
    results = query_db(query_vector)
    
    # Extract best match
    if results.matches:
        best_match = results.matches[0]  # Get the best match (most relevant)
        if best_match.metadata and 'text' in best_match.metadata:
            response = best_match.metadata['text']  # Get the relevant text from metadata
        else:
            response = "No relevant text found in metadata."
    else:
        response = "No matches found."
    return response