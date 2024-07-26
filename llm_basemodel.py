from langchain_aws import BedrockLLM

from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.chat_models import BedrockChat
from langchain_aws import ChatBedrock

class LanguageModel():
    def __init__(self,client):
        self.bedrock_client = client
        ############
        # Anthropic Claude     
        # Bedrock LLM
        inference_modifier = {
                "max_tokens_to_sample": 3000,
                "temperature": 0,
                "top_k": 20,
                "top_p": 1,
                "stop_sequences": ["\n\nHuman:"],
            }
        print("bedrockllm")
        #self.llm = BedrockLLM(
        #    model_id = "anthropic.claude-v2:1",
            #model_id = "anthropic.claude-3-sonnet-20240229-v1:0",
        #                    client = self.bedrock_client, 
        #                    model_kwargs = inference_modifier 
        #                    )
        
        self.llm = ChatBedrock(
            #model_id = "anthropic.claude-v2:1",
            model_id = "anthropic.claude-3-sonnet-20240229-v1:0",
                            client = self.bedrock_client, 
                            model_kwargs = inference_modifier 
                            )
        
        # Embeddings Modules
        self.embeddings = BedrockEmbeddings(
            client=self.bedrock_client, 
            model_id="amazon.titan-embed-text-v1"
        )