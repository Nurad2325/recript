from flaskr.services.confluence import get_all_confluence_pages
from flaskr.services.github import get_all_github_repo_files
from flaskr.services.llm_agent import chunk_text, embed_text
from flaskr.db import get_db
from flask import current_app
import uuid
import os

def load_database():
    reload = os.getenv("RELOAD_INDEX")
    if reload == "false":
        current_app.logger.info(f"Reload set to {reload}. Skipping reload pinecone...")
        return
    current_app.logger.info(f"Reloading docs (set reload false in .env to skip)")
    index = get_db()
    pages = get_all_confluence_pages()
    if len(pages) == 0:
        current_app.logger.error("Error retrieving confluence docs")
    try:
        for i, page in enumerate(pages):
            title = page["title"]
            current_app.logger.info(f"Uploading {title}: {i+1}/{len(pages)} confluence docs")
            content = page["content"]
            chunks = chunk_text(content)
            upserts = []
            for j, chunk in enumerate(chunks):
                embedded_chunk = embed_text(chunk)
                source = "CONFLUENCE"
                metadata = {
                    "doc": i,
                    "chunk": j,
                    "source": source,
                    "text": chunk
                }
                upserts.append({"id": str(uuid.uuid4()), "values": embedded_chunk, "metadata": metadata})
            index.upsert(vectors=upserts)
        current_app.logger.info(f"Completed uploading {len(pages)} confluence docs")
    except Exception as error:
        current_app.logger.error(f"Error uploading confluence docs: {error}")
    

    # Fetch and process GitHub repository files
    try:
        repo_name = "sshHood/sshHood"  # Replace with actual GitHub repo name
        files = get_all_github_repo_files(repo_name)
        
        if len(files) == 0:
            current_app.logger.error("Error retrieving GitHub files")
        
        # Upload GitHub files to the database
        for i, file_content in enumerate(files):
            current_app.logger.info(f"Uploading {i+1}/{len(files)} GitHub files")
            chunks = chunk_text(file_content)
            upserts = []
            for j, chunk in enumerate(chunks):
                embedded_chunk = embed_text(chunk)
                source = "GITHUB"
                metadata = {
                    "doc": i,
                    "chunk": j,
                    "source": source,
                    "text": chunk
                }
                upserts.append({"id": str(uuid.uuid4()), "values": embedded_chunk, "metadata": metadata})
            index.upsert(vectors=upserts)
        current_app.logger.info(f"Completed uploading {len(files)} GitHub files")
    
    except Exception as error:
        current_app.logger.error(f"Error uploading GitHub files: {error}")