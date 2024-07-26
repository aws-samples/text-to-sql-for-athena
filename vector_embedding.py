##from langchain.document_loaders import JSONLoader
from langchain_community.document_loaders import JSONLoader
import logging 
import json
import os,sys
import re
sys.path.append("/home/ec2-user/SageMaker/llm_bedrock_v0/")
##import schema_details.tbl_schema  as sc
from llm_basemodel import LanguageModel

from boto_client import Clientmodules
##from langchain.embeddings import BedrockEmbeddings
from langchain_community.embeddings import BedrockEmbeddings
##from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
import numpy as np
from datetime import datetime

class EmbeddingBedrock:
    def __init__(self):
        self.bedrock_client = Clientmodules.createBedrockRuntimeClient()
        self.language_model = LanguageModel(self.bedrock_client)
        self.llm = self.language_model.llm
        self.embeddings = self.language_model.embeddings
        self.embeddings_model_id='amazon.titan-embed-text-v1'
        
    def create_embeddings(self):
        documents = JSONLoader(file_path='imdb_schema.jsonl', jq_schema='.', text_content=False, json_lines=False).load()
        # EMBEDDINGS_MODEL_ID='amazon.titan-embed-text-v1'
        embeddings_model_id='amazon.titan-embed-text-v1'
        # brrkEmbeddings = BedrockEmbeddings(model_id=EMBEDDINGS_MODEL_ID,client=bedrock_client)
        try:
            vector_store = FAISS.from_documents(documents, self.embeddings)
        except Exception:
            raise Exception("Failed to create vector store")
        print("Created vector store")
        return vector_store
    
    def save_local_vector_store(self,vector_store, vector_store_path):
        time_now = datetime.now().strftime("%d%m%Y%H%M%S")
        vector_store_path=vector_store_path+'/'+time_now+'.vs'
        embeddings_model_id=self.embeddings_model_id
        try:
            if vector_store_path == "":
                vector_store_path = f"../vector_store/{time_now}.vs"
            os.makedirs(os.path.dirname(vector_store_path), exist_ok=True)
            vector_store.save_local(vector_store_path)
            with open(f"{vector_store_path}/embeddings_model_id", 'w') as f:
                f.write(embeddings_model_id)
        except Exception:
            print("Failed to save vector store, continuing without saving...")
        return vector_store_path
    
    def load_local_vector_store(self,vector_store_path):
        try:
            with open(f"{vector_store_path}/embeddings_model_id", 'r') as f:
                embeddings_model_id = f.read()
            vector_store = FAISS.load_local(vector_store_path, self.embeddings)
            print("Loaded vector store")
            return vector_store
        except Exception:
            print("Failed to load vector store, continuing creating one...")

        # print(load_local_vector_store(save_local_vector_store_path))
        
        
    def format_metadata(slef,metadata):
        docs = []
        # Remove indentation and line feed
        for elt in metadata:
            processed = elt.page_content
            for i in range(20, -1, -1):
                processed = processed.replace('\n' + ' ' * i, '')
            docs.append(processed)
        result = '\n'.join(docs)
        # Escape curly brackets
        result = result.replace('{', '{{')
        result = result.replace('}', '}}')
        return result