from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import os
from langchain_pinecone import PineconeEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain.chains import RetrievalQA
import time
from flaskr.services.confluence import fetch_confluence_page_content  # Fetching content from Confluence

# Initialize Pinecone client
def initialize_pinecone():
    api_key = os.environ.get("PINECONE_API_KEY")
    pc = Pinecone(api_key=api_key)
    index_name = "docs-rag-chatbot-eo1"
    
    # Check if the index exists
    existing_indexes = pc.list_indexes()  # Adjusted to use list_indexes()
    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=1024,  # Ensure this matches the embedding model you're using
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
    
    return pc.Index(index_name)

# Fetch documents from Confluence
def fetch_confluence_documents(page_ids):
    documents = []
    for page_id in page_ids:
        content = fetch_confluence_page_content(page_id)
        if content:
            documents.append(content)
    return documents

# Chunk the Confluence documents
def chunk_confluence_documents(documents):
    text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("##", "Header 2")], strip_headers=False)
    chunks = []
    for document in documents:
        # Wrap the document content in the necessary format and chunk it
        document_text = str(document)
        chunks += text_splitter.split_text(document_text)
    return chunks

# Embed and upsert the chunks to Pinecone
def embed_and_upsert(chunks, pinecone_index, openai_api_key):
    # Initialize OpenAI Embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

    # Create embeddings for the document chunks
    vectors = []
    for i, chunk in enumerate(chunks):
        vector = embeddings.embed_documents([chunk])[0]  # Embed the chunk
        vectors.append((str(i), vector))  # Store the vector with an ID

    # Upsert the vectors to Pinecone
    pinecone_index.upsert(vectors)
    print("Vectors upserted successfully!")

# Query the Pinecone index
def query_pinecone_index(query, pinecone_index, openai_api_key):
    # Initialize OpenAI embeddings for query
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

    # Generate the query embedding
    query_vector = embeddings.embed_query(query)

    # Query Pinecone index for the most relevant chunk
    results = pinecone_index.query(
        vector=query_vector,
        top_k=1,
        include_values=True,
        include_metadata=True
    )
    
    return results

# Main function to handle indexing and querying
def main():
    # Read API keys from environment variables
    pinecone_api_key = os.getenv('PINECONE_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')

    # Initialize Pinecone and create the index if it doesn't exist
    pinecone_index = initialize_pinecone()

    # Set default page IDs
    page_ids = [3735580, 3702785, 3833859, 98307]  # Default Confluence page IDs

    # Fetch and chunk Confluence documents
    documents = fetch_confluence_documents(page_ids)  # Fetch documents from Confluence
    chunks = chunk_confluence_documents(documents)    # Chunk the documents for better retrieval

    # Embed and upsert the document chunks into Pinecone
    embed_and_upsert(chunks, pinecone_index, openai_api_key)

    # Example query (you can modify or enhance this with a dynamic query later)
    query = "What is the app used in this project?"  # Example query to test
    response = query_pinecone_index(query, pinecone_index, openai_api_key)

    return response
