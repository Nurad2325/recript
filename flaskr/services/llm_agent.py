import os
import requests
from bs4 import BeautifulSoup
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Document
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from flask import current_app
from flaskr.db import query_db
from datetime import datetime
import pytz

def enhance_with_llm_rag(query, content):
    OPENAI_CHAT_MODEL = os.getenv('OPENAI_CHAT_MODEL', '<ERROR>')
    llm = OpenAI(model=OPENAI_CHAT_MODEL)
    messages = [
        ChatMessage(
            role="system",
            content=f"""Given this content {content} answer this question, mention the source behind each part of the answer like 'Source: GitHub' or 'Source: Confluence'.  
         If the content only contains 'No matches found', mention that the current knowledge base does not explicitly answer this question, but providing the best possible answer. 
        Add this message at the end: "This query has been updated in the Knowledge Gap Tracker page in Confluence - https://engineeringonboarding.atlassian.net/wiki/spaces/SD/pages/9240675/Knowledge+Gap+Tracker" """
        ),
        ChatMessage(role="user", content=query),
    ]
    response = llm.chat(messages)
    return response.message.content

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

    combined_results = []
    
    if confluence_results.matches:
        for match in confluence_results.matches:
            if match.score >= score_threshold:
                combined_results.append(match)
    
    if github_results.matches:
        for match in github_results.matches:
            if match.score >= score_threshold:
                combined_results.append(match)

    if combined_results:
        combined_results = sorted(combined_results, key=lambda x: x.score, reverse=True)
        response = "Here are the top results:\n"
        for i, result in enumerate(combined_results[:3]):  # Limit to top 3 results
            response += f"\nResult {i + 1} from {result.metadata['source']}:\n{result.metadata['text'][:500]}..."  # Limit to 500 characters per result
        
    else:
        best_confluence = (
            confluence_results.matches[0] if confluence_results.matches and confluence_results.matches[0].score > score_threshold else None
        )
        best_github = (
            github_results.matches[0] if github_results.matches and github_results.matches[0].score > score_threshold else None
        )
        
        if best_confluence and (not best_github or best_confluence.score > best_github.score):
            response = f"Best result from Confluence:\n{best_confluence.metadata['text']}"
        elif best_github:
            response = f"Best result from GitHub:\n{best_github.metadata['text']}"
        else:
            response = "No matches found."
            post_query_to_confluence(text) 

    return response

def post_query_to_confluence(question):
    CONFLUENCE_BASE_URL = os.getenv('CONFLUENCE_BASE_URL', '<ERROR>')
    CONFLUENCE_USERNAME = os.getenv('CONFLUENCE_USERNAME', '<ERROR>')
    CONFLUENCE_API_TOKEN = os.getenv('CONFLUENCE_API_TOKEN', '<ERROR>')

    PAGE_ID = '9240675'
    page_url = f'{CONFLUENCE_BASE_URL}/rest/api/content/{PAGE_ID}?expand=body.storage,version'

    response = requests.get(page_url, auth=(CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN))

    if response.status_code != 200:
        current_app.logger.error(f"Failed to retrieve page data. Status code: {response.status_code}")
        return

    page_data = response.json()
    current_body = page_data['body']['storage']['value']

    # Extract current questions and number them
    soup = BeautifulSoup(current_body, 'html.parser')

    # Find all existing questions (assuming they're inside <p> tags)
    question_paragraphs = soup.find_all('p')
    numbered_questions = []

    # Renumber the questions and build the new content
    for idx, para in enumerate(question_paragraphs, start=1):
        text = para.get_text(strip=True)
        if text.lower().startswith('question'):
            numbered_questions.append(f"<p>Question {idx}: {text.split(':', 1)[-1]}</p>")
    
    # Add the new question at the end with current PDT time
    pdt_tz = pytz.timezone('America/Los_Angeles')
    current_pdt_time = datetime.now(pdt_tz).strftime("%Y-%m-%d %I:%M:%S %p")
    new_question = f"<p>Question {len(numbered_questions) + 1}: {question} (added on {current_pdt_time})</p>"
    numbered_questions.append(new_question)

    # Combine all questions back into the body
    new_body = ''.join(numbered_questions)

    updated_content = {
        "version": {
            "number": page_data['version']['number'] + 1
        },
        "title": page_data['title'],
        "type": "page",
        "body": {
            "storage": {
                "value": new_body,
                "representation": "storage"
            }
        }
    }

    update_response = requests.put(
        page_url,
        auth=(CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN),
        json=updated_content,
        headers={"Content-Type": "application/json"}
    )

    if update_response.status_code == 200:
        current_app.logger.info("Question posted successfully to Confluence")
    else:
        current_app.logger.error(f"Error posting to Confluence: {update_response.status_code}")
        current_app.logger.error(f"Response content: {update_response.content}")
