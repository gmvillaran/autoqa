import logging;
from llama_index import (
    VectorStoreIndex,
    ServiceContext,
    ChromaVectorStore,
    StorageContext
)

import chromadb

class IndexManager:
    
    def __init__(self, documents, llm, embed_model):
        global index
        self.logger = logging.getLogger(__name__)

        self.documents = documents
        self.llm = llm
        self.embed_model = embed_model

        self.service_context = ServiceContext.from_defaults(
            chunk_size=500,
            chunk_overlap=20,
            llm=self.llm,
            embed_model=self.embed_model,
        )

        self.chroma_client = chromadb.PersistentClient(path="chroma")
        self.chroma_collection = self.chroma_client.get_or_create_collection("cardcom_collection")
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

        index = VectorStoreIndex.from_documents(
            self.documents, storage_context=self.storage_context, service_context=self.service_context
        )
    
    def query_model(self, query):
        query_engine = index.as_query_engine()
        response = query_engine.query(query)
        return response