import os
import requests
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Document
from llama_index.llms import openai
from flask import current_app
from flaskr.db import query_db

def enhance_with_llm(text):
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
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '<ERROR>')
    llm_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        "model": "gpt-4o-mini", #"gpt-3.5-turbo"
        "messages": [
            {"role": "user", "content": f"Answer the following query in a short brief: {query} using this content: {content}. Mention the source behind each part of the answer like From Confluence and From Github"}
        ],
        "max_tokens": 150,
    }

    llm = OpenAI(model="gpt-4o-mini")  # Change to desired model, e.g., gpt-3.5-turbo
    llm_predictor = LLMPredictor(llm=llm)

    # Build the input prompt for the LLM
    prompt = (
        f"Answer the following query in a short brief: {query} using this content: {content}. "
        "Mention the source behind each part of the answer like 'From Confluence' and 'From Github'."
    )

    # Query the model using LlamaIndex's LLMPredictor
    enhanced_text = llm_predictor.predict(prompt, max_tokens=150)

    return enhanced_text

    response = requests.post(llm_url, headers=headers, json=data)

    if response.status_code == 200:
        enhanced_text = response.json().get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        return enhanced_text
    else:
        return f"Error enhancing content: {response.status_code}"

def test_openai_api():
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

def query_pinecone_non_agent(text):
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

def query_pinecone(text):
    response = ""
    score_threshold = 0.3
    query_vector = process_query(text)
    confluence_results = query_db(query_vector, "CONFLUENCE")
    github_results = query_db(query_vector, "GITHUB")

    # Combine and filter results above the score threshold
    combined_results = []
    
    # Check for results in Confluence
    if confluence_results.matches:
        for match in confluence_results.matches:
            if match.score >= score_threshold:
                combined_results.append(match)
    
    print("dj 1 ", len(combined_results), len(confluence_results.matches))
    # Check for results in GitHub
    if github_results.matches:
        for match in github_results.matches:
            if match.score >= score_threshold:
                combined_results.append(match)

    print("dj 2 ", len(combined_results), len(github_results.matches))
    if combined_results:
        combined_results = sorted(combined_results, key=lambda x: x.score, reverse=True)
        response = "Here are the top results:\n"
        for i, result in enumerate(combined_results[:3]):  # Limit to top 3 results
            response += f"\nResult {i + 1} from {result.metadata['source']}:\n{result.metadata['text'][:500]}..."  # Limit to 500 characters per result
        
    # If combined results don't meet the threshold, fallback to the best result from either source
    else:
        best_confluence = confluence_results.matches[0] if confluence_results.matches else None
        best_github = github_results.matches[0] if github_results.matches else None
        
        # Select the top result from the source with the highest score
        if best_confluence and (not best_github or best_confluence.score > best_github.score):
            response = f"Best result from Confluence:\n{best_confluence.metadata['text']}"
        elif best_github:
            response = f"Best result from GitHub:\n{best_github.metadata['text']}"
        else:
            response = "No matches found."
        print("dj 3 ", response)
    return response