## A robust Text-to-SQL solution for Amazon Athena

This is the repo for AWS AI/ML Blog Post: https://aws.amazon.com/blogs/machine-learning/build-a-robust-text-to-sql-solution-generating-complex-queries-self-correcting-and-querying-diverse-data-sources/

### 1)	Introduction

Structured Query Language (SQL) is a complex language that needs both understanding of database, metadata and SQL language. Today, Generative AI can enable people without SQL knowledge. This task is called, Text-to-SQL, generating SQL queries from natural language processing (NLP) and converting text into a semantically correct SQL. The presented solution in this post aims to bring enterprise analytics operations to the next level by shortening the path to your data using natural language. 

However, the task of Text-to-SQL presents various challenges. At its core, the difficulty arises from the inherent differences between human language, which is ambiguous, and context-dependent, and SQL, being precise, mathematical and structured. With the emergence of Large Language Models (LLMs), the Text-to-SQL landscape has undergone a significant transformation. Demonstrating an exceptional performance, LLMs are now capable of generating accurate SQL queries from natural language descriptions. The larger adoption of centralized analytics solutions, such as data-mesh, -lakes and -warehouses, customers start to have quality metadata which provides extra input to LLMs to build better Text-to-SQL solutions. Finally, customers need to build this SQL solutions for every data-base because data is not stored in a single location. Hence, even if the customers build Text-to-SQL, they had to do it for all data-sources given the access would be different. You can learn more about the Text-to-SQL best practices and design patterns.

This post will address those challenges. First, we will include the meta-data of the data sources to increase the reliability of the generated SQL query. Secondly, we will use a final loop for evaluation and correction of SQL queries to correct the SQL query, if it is applicable. Here, we will utilize the error messages received from Amazon Athena which will make the correction prompting more coincide. Amazon Athena also allows us to utilize Athena’s supported endpoints and connectors to cover a large set of data sources. After we build the solution, we will test the Text-to-SQL capability at different realistic scenarios with varying SQL complexity levels. Finally, we will explain how a different data-source can be easily incorporated using our solution. Along with these results, you can observe our solutions architecture, workflow and the code-base snippets for you to implement this solution for your business.


### Solution Architecture
<img width="434" alt="image" src="https://github.com/aws-samples/text-to-sql-for-athena/assets/84034588/0c523340-0d7d-4da0-a409-1583a04184fe">

#### Process Walkthrough
1. Create a knowledge base "movie-knowledgebase" in Bedrock with Opensearchserverless as the vector store
2. In the Opensearchserverless console
    - Record the OpenSearch endpoint.   
    - From the indexes tab record the index name. It should be something similar to "bedrock-knowledge-base-default-index" 
    - Also record the vector field . It should be something like "bedrock-knowledge-base-default-vector"
    - Also record the Metadata field of "id". 
3.  Create an S3 bucket KB-<ACCOUNT_ID>
    - Create an  folder "input"
4.  Download the sample files from the following links
     - https://developer.imdb.com/non-commercial-datasets/#titleakastsvgz
     - https://developer.imdb.com/non-commercial-datasets/#titleratingstsvgz
5.  Upload the downloaded files into the "input" folder.
6.  Create a glue database "imdb_stg". Create a glue crawler and set the database name to be "imdb_stg" .  Start the glue crawler to crawl  the S3 bucket KB-<ACCOUNT_ID>/input location. It should create 2 tables in Glue catalog. 
    If you use another database name instead of "imdb_stg", update the file "idmb_schema.jsonl" the field of "database_name" to the exact name of the new glue database.
7. Query the 2 tables via Athena to see that the data exists.
8. Create another folder in the S3 bucket KB-<ACCOUNT_ID> "/metadata". 
   - Upload the file "imdb_schema.jsonl"  into the metadata folder. 
9. From the Bedrock console, 
    - Create a datasource with name = 'knowledge-base-movie-details-data-source' , type =  'Amazon S3',  pointing to the S3 foldercreated in step #8. Retain the 'Default chunking and parsing configuration'
    - Sync the 'knowledge-base-movie-details-data-source'. 
      Anytime new database changes are applied, dont forget to upload the revised "imdb_schema.jsonl" file to the S3 folder created in step #8 and do a sync . 
10. Run the jupyter notebook   with the following caveats
    - In the step 2 of this process walkthru, if the values for the index name, vector field , metadata field value are different substitute the new values  in the step "4.1 Update the variables" of the jupyter notebook. 
    - If you are running the jupyter notebook using  [Amazon Sagemaker - option 1](https://studiolab.sagemaker.aws/) or [Amazon Sagemaker - option 2](https://docs.aws.amazon.com/sagemaker/latest/dg/ex1-prepare.html) or VSCode , ensure the role or the user has the right set of permissions . 
11. Continue with rest of the steps till Step 6 . At this stage, the process is ready to receive the query in natural language. 
12.	User putting their query in natural language. Here, you can use any web-application to provide the chat UI. Hence, we did not cover the UI details in our post.
13.	Apply RAG framework via the similarity search which would add the extra context from the metadata from the vector database that we formed in Step-2. This table is used for finding the correct table, database and attributes.
14.	Merging the query with the context is sent to Claude v3 on Amazon Bedrock.
15.	Get the generated SQL query and connect to Athena to validate the syntax. 
16.	[Correction loop, if applicable] If Athena provides an error message that mentions the syntax is incorrect, we will receive use the error text from Athena’s response.
17.	[Correction loop, if applicable] The new prompt now adds the Athena’s response. 
18.	[Correction loop, if applicable] Create the corrected SQL and continue the process. This iteration can be performed multiple times.
19.	Finally, execute SQL using Athena and generate output. Here, the output is presented to the user. For the sake of architectural simplicity, we did not show this step.
    Since the # of records in the movie file are large and there is no athena partitioning , the queries can take upto 2 mins to execute. This can be optimized in many ways and its not described here. 

## Using the repo
Please start with [the notebook](https://github.com/aws-samples/text-to-sql-for-athena/blob/main/BedrockTextToSql_for_Athena.ipynb)

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

