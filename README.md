## A robust Text-to-SQL solution for Amazon Athena

This is the repo for AWS AI/ML Blog Post: https://aws.amazon.com/blogs/machine-learning/build-a-robust-text-to-sql-solution-generating-complex-queries-self-correcting-and-querying-diverse-data-sources/

### 1)	Introduction

Structured Query Language (SQL) is a complex language that needs both understanding of database, metadata and SQL language. Today, Generative AI can enable people without SQL knowledge. This task is called, Text-to-SQL, generating SQL queries from natural language processing (NLP) and converting text into a semantically correct SQL. The presented solution in this post aims to bring enterprise analytics operations to the next level by shortening the path to your data using natural language. 

However, the task of Text-to-SQL presents various challenges. At its core, the difficulty arises from the inherent differences between human language, which is ambiguous, and context-dependent, and SQL, being precise, mathematical and structured. With the emergence of Large Language Models (LLMs), the Text-to-SQL landscape has undergone a significant transformation. Demonstrating an exceptional performance, LLMs are now capable of generating accurate SQL queries from natural language descriptions. The larger adoption of centralized analytics solutions, such as data-mesh, -lakes and -warehouses, customers start to have quality metadata which provides extra input to LLMs to build better Text-to-SQL solutions. Finally, customers need to build this SQL solutions for every data-base because data is not stored in a single location. Hence, even if the customers build Text-to-SQL, they had to do it for all data-sources given the access would be different. You can learn more about the Text-to-SQL best practices and design patterns.

This post will address those challenges. First, we will include the meta-data of the data sources to increase the reliability of the generated SQL query. Secondly, we will use a final loop for evaluation and correction of SQL queries to correct the SQL query, if it is applicable. Here, we will utilize the error messages received from Amazon Athena which will make the correction prompting more coincide. Amazon Athena also allows us to utilize Athena’s supported endpoints and connectors to cover a large set of data sources. After we build the solution, we will test the Text-to-SQL capability at different realistic scenarios with varying SQL complexity levels. Finally, we will explain how a different data-source can be easily incorporated using our solution. Along with these results, you can observe our solutions architecture, workflow and the code-base snippets for you to implement this solution for your business.


### Solution Architecture
<img width="434" alt="image" src="https://github.com/aws-samples/text-to-sql-for-athena/assets/84034588/0c523340-0d7d-4da0-a409-1583a04184fe">

#### Process Walkthrough
1. Create a knowledge base [movie-knowledgebase](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-create.html) in Bedrock with Opensearchserverless as a vector store.
    - You can use the quick start option that can use an S3 bucket that you create. (example: knowledge-base-text-to-sql-example-<abcd1234>).
    - The process automatically creates a OpenSearch Serverless endpoint on your behalf.
2. Go to the OpenSearch Serverless console
    - Record the OpenSearch endpoint. (e.g. https://<abcdr54321>.<region>.aoss.amazonaws.com)
    - Record the index name from the Index tab. (e.g. "bedrock-knowledge-base-default-index")
    - Click the index that opens another tab showing you the vector name that you should record. (e.g. "bedrock-knowledge-base-default-vector")
    - Finally, record the Metadata field of "id". 
3.  Create a seperate S3 bucket to store your raw data (e.g. data-store-text-to-sql-<unique_ID>) 
    - Create an  folder "input"
4.  Download one or more sample files from the following links: 
     - https://developer.imdb.com/non-commercial-datasets/#titleakastsvgz
     - https://developer.imdb.com/non-commercial-datasets/#titleratingstsvgz
5.  Upload the downloaded files into the "input" folder. (e.g. data-store-text-to-sql-<unique_ID>/input)
6.  Create a glue database such as "imdb_stg". Create a glue crawler and set the database name to be "imdb_stg". While creating your Crawler, the process also allows you to create a database.
7.  Start the glue crawler to crawl the data S3 bucket (e.g. data-store-text-to-sql-<unique_ID>/input). It should create "n" number of tables in Glue catalog based on how many data files you have utilized. This step is a general Glue Crawler step that you can learn more from [the documentation](https://docs.aws.amazon.com/glue/latest/dg/define-crawler.html).
8. Query the tables created to see that the data exists. You can use Athena as explained [here](https://docs.aws.amazon.com/athena/latest/ug/querying-glue-catalog.html).
9. Now, we will use the schema extracted from your tables to be used in RAG. You can use [GetSchema API](https://docs.aws.amazon.com/glue/latest/webapi/API_GetSchema.html) or do this manually. You can also include some extra keys to explain your columns or database. For example, you can state the database is about "IMDB moviesThe best approach is to create GetSchema API into a Lambda function that can be run through EventBridge. Yet, for demostration purposes we extracted schema from the Glue Table. Please note that if you use another database name instead of "imdb_stg", you should update the file "idmb_schema.jsonl" the field of "database_name" to the exact name of the new glue database.
10. Now, you can go back to the original S3 bucket that you created for the knowledge-base (e.g. knowledge-base-text-to-sql-example-<abcd1234>). Upload the file "imdb_schema.jsonl" into this S3 bucket.
11. From the Bedrock console, sync the knowledge-base. The process will convert the schema into embeddings.
    -  You can test your embeddings. On Bedrock console, select an LLM and ask this question "Tell me about the schema for the imdb movie database?" which will give you explanations on the schema based on your explanations in the meta-data and table / column names.
    - Now it is time to go to our jupyteer notebook.
13. Run the jupyter notebook with the following edits:
    - In the file of athena_execution.py replace   'ATHENA-OUTPUT-BUCKET' with the name of the bucket where Athena has actual write permissions to. (e.g. data-store-text-to-sql-<unique_ID>)
    - In the step 2 of this process walkthru, if the values for the index name, vector field , metadata field value are different substitute the new values in the step "4.1 Update the variables" in the jupyter notebook. 
    - If you are running the jupyter notebook using  [Amazon Sagemaker - option 1](https://studiolab.sagemaker.aws/) or [Amazon Sagemaker - option 2](https://docs.aws.amazon.com/sagemaker/latest/dg/ex1-prepare.html) or VSCode , ensure the role or the user has the right set of permissions . 
13. Continue with rest of the steps till Step 6 . At this stage, the process is ready to receive the query in natural language. 
14.	User putting their query in natural language. Here, you can use any web-application to provide the chat UI. Hence, we did not cover the UI details in our post.
15.	Apply RAG framework via the similarity search which would add the extra context from the metadata from the vector database that we formed in Step-2. This table is used for finding the correct table, database and attributes.
16.	Merging the query with the context is sent to Claude v3 on Amazon Bedrock.
17.	Get the generated SQL query and connect to Athena to validate the syntax. 
18.	[Correction loop, if applicable] If Athena provides an error message that mentions the syntax is incorrect, we will receive use the error text from Athena’s response.
19.	[Correction loop, if applicable] The new prompt now adds the Athena’s response. 
20.	[Correction loop, if applicable] Create the corrected SQL and continue the process. This iteration can be performed multiple times.
21.	Finally, execute SQL using Athena and generate output. Here, the output is presented to the user. For the sake of architectural simplicity, we did not show this step.
    Since the # of records in the title file are > 10M and there is no athena partitioning , the queries can take upto 1-2 mins to execute. This can be optimized in many ways and its not described here. 

## Using the repo
Please start with [the notebook](https://github.com/aws-samples/text-to-sql-for-athena/blob/main/BedrockTextToSql_for_Athena.ipynb)

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

