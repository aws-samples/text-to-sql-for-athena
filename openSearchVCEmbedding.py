import sys
import time
from opensearchpy.client import OpenSearch
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from typing import List, Tuple
import logging
import numpy as np
import boto3

from langchain.llms.bedrock import Bedrock
from langchain.embeddings.bedrock import BedrockEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from langchain.vectorstores import OpenSearchVectorSearch
from langchain.document_loaders import JSONLoader

logger = logging.getLogger()
logging.basicConfig(format='%(asctime)s,%(module)s,%(processName)s,%(levelname)s,%(message)s', level=logging.INFO, stream=sys.stderr)

sys.path.append("/home/ec2-user/SageMaker/llm_bedrock_v0/")
from llm_basemodel import LanguageModel
from boto_client import Clientmodules

"""

    Connecting OpenSearch in AWS done in multiple ways. here we are going to use userid and password to connect.
    Opensearch cluster can be inside VPC or Public. Recommended in inside VPC for all good reasons. Here for this demo I have mdae public.
    Opensearch is massively sclabale search engine , I have used it mostly for UI applications to render data in fraction of second. However it can also be used for Vector store.
    It provides simlarity search using KNN, Cosine or more. We will have separate document for that.
    Here we will read PDF file and store in Openserach so that we can use that in our RAG Architecture.

"""


# Here Keeping the required parameter. can be used from config store.
http_auth = ('llm**ector','@l****S1')
opensearch_domain_endpoint = 'https://search-llm-1.es.amazonaws.com'
aws_region = 'us-east-1'
index_name = 'llm_vector_db_metadata_indx1'


class EmbeddingBedrockOpenSearch:
    def __init__(self):
        self.bedrock_client = Clientmodules.createBedrockRuntimeClient()
        self.language_model = LanguageModel(self.bedrock_client)
        self.llm = self.language_model.llm
        self.embeddings = self.language_model.embeddings
        self.opensearch_domain_endpoint='https://search******puq.us-east-1.es.amazonaws.com'
        self.http_auth=('llm_vector','@l****orS1')
    
    def check_if_index_exists(self,index_name: str, region: str, host: str, http_auth: Tuple[str, str]) -> OpenSearch:
        aos_client = OpenSearch(
            hosts = [{'host': host.replace("https://", ""), 'port': 443}],
            http_auth = http_auth,
            use_ssl = True,
            verify_certs = True,
            connection_class = RequestsHttpConnection
        )
        exists = aos_client.indices.exists(index_name)
        print("exist check",exists)
        return exists
    
    def add_documnets(self,index_name: str,file_name:str):
        documents = JSONLoader(file_path=file_name, jq_schema='.', text_content=False, json_lines=False).load()
        docs = OpenSearchVectorSearch.from_documents(embedding=self.embeddings,
                                                    opensearch_url=self.opensearch_domain_endpoint,
                                                     http_auth=self.http_auth,
                                                    documents=documents,
                                                    index_name=index_name,
                                                    engine="faiss")
        index_exists = self.check_if_index_exists(index_name,
                                         aws_region,
                                         opensearch_domain_endpoint,
                                         http_auth)
        if not index_exists :
            logger.info(f'index :{index_name} is not existing ')
            sys.exit(-1)
        else:
            logger.info(f'index :{index_name} Got created')
            
    def getDocumentfromIndex(self,index_name: str):
        docsearch = OpenSearchVectorSearch(opensearch_url=self.opensearch_domain_endpoint,
                                           embedding_function=self.embeddings,
                                           http_auth=self.http_auth,
                                           index_name=index_name)
        return docsearch
    
    def getSimilaritySearch(self,user_query: str,vcindex):
        # user_query='show me the top 10 titile by maximum votes'
        docs = vcindex.similarity_search(user_query,k=200)
        # print(docs[0].page_content)
        return docs
    
    def format_metadata(self,metadata):
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