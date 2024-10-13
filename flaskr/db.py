import os
from flask import current_app
from pinecone import Pinecone, ServerlessSpec

EMBEDDING_DIMENSION = 1536

def init_db():
    reload = os.getenv("RELOAD_INDEX")
    if reload == "false":
<<<<<<< HEAD
        current_app.logger.info(f"Reload set to {reload}. Skipping init pinecone...")
=======
        current_app.logger.info(f"Reload set to {reload}. Skipping reload pinecone...")
>>>>>>> main
        return
    DB_KEY = os.getenv('PINECONE_API_KEY', '<ERROR>')
    pc = Pinecone(api_key=DB_KEY)
    INDEX = os.getenv('INDEX_NAME', '<ERROR>')
    if pc.has_index(INDEX):
        pc.delete_index(INDEX)
    pc.create_index(
        name=INDEX,
        dimension=EMBEDDING_DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(
            cloud='aws', 
            region='us-east-1'
        ) 
    ) 
    index = pc.Index(INDEX)
    return index

def get_db():
    DB_KEY = os.getenv('PINECONE_API_KEY', '<ERROR>')
    pc = Pinecone(api_key=DB_KEY)
    INDEX = os.getenv('INDEX_NAME', '<ERROR>')
    if not pc.has_index(INDEX):
        current_app.logger.error("DB connection not established")
        raise Exception("DB connection not established")
    else:
        index = pc.Index(INDEX)
        return index

def query_db(query_vector, source = "CONFLUENCE"):
    pinecone_index = get_db()
    results = pinecone_index.query(
        vector=query_vector,
        top_k=3,
        filter={
            "source":source
        },
        include_values=True,
        include_metadata=True,
        timeout = 30
    )
    return results