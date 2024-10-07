from flaskr.services.confluence import get_all_confluence_pages
from flaskr.services.llm_agent import chunk_text, embed_chunk
from flaskr.db import get_db
from flask import current_app
import uuid

def load_database():
    index = get_db()
    pages = get_all_confluence_pages()
    if len(pages) == 0:
        current_app.logger.error("Error retrieving confluence docs")
    try:
        for i, page in enumerate(pages):
            current_app.logger.info(f"Uploading {i+1}/{len(pages)} confluence docs")
            chunks = chunk_text(page)
            upserts = []
            for j, chunk in enumerate(chunks):
                embedded_chunk = embed_chunk(chunk)
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
    