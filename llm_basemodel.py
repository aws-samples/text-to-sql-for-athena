from langchain.llms.bedrock import Bedrock
from langchain.embeddings import BedrockEmbeddings


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
        self.llm = Bedrock(model_id = "anthropic.claude-v2:1",
                            client = self.bedrock_client, 
                            model_kwargs = inference_modifier 
                            )
        
        # Embeddings Modules
        self.embeddings = BedrockEmbeddings(
            client=self.bedrock_client, 
            model_id="amazon.titan-embed-text-v1"
        )