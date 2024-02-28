## A robust Text-to-SQL solution for Amazon Athena

This is the repo for AWS AI/ML Blog Post: https://aws.amazon.com/blogs/machine-learning/build-a-robust-text-to-sql-solution-generating-complex-queries-self-correcting-and-querying-diverse-data-sources/

### 1)	Introduction

Structured Query Language (SQL) is a complex language that needs both understanding of database, metadata and SQL language. Today, Generative AI can enable people without SQL knowledge. This task is called, Text-to-SQL, generating SQL queries from natural language processing (NLP) and converting text into a semantically correct SQL. The presented solution in this post aims to bring enterprise analytics operations to the next level by shortening the path to your data using natural language. 

However, the task of Text-to-SQL presents various challenges. At its core, the difficulty arises from the inherent differences between human language, which is ambiguous, and context-dependent, and SQL, being precise, mathematical and structured. With the emergence of Large Language Models (LLMs), the Text-to-SQL landscape has undergone a significant transformation. Demonstrating an exceptional performance, LLMs are now capable of generating accurate SQL queries from natural language descriptions. The larger adoption of centralized analytics solutions, such as data-mesh, -lakes and -warehouses, customers start to have quality metadata which provides extra input to LLMs to build better Text-to-SQL solutions. Finally, customers need to build this SQL solutions for every data-base because data is not stored in a single location. Hence, even if the customers build Text-to-SQL, they had to do it for all data-sources given the access would be different. You can learn more about the Text-to-SQL best practices and design patterns.

This post will address those challenges. First, we will include the meta-data of the data sources to increase the reliability of the generated SQL query. Secondly, we will use a final loop for evaluation and correction of SQL queries to correct the SQL query, if it is applicable. Here, we will utilize the error messages received from Amazon Athena which will make the correction prompting more coincide. Amazon Athena also allows us to utilize Athena’s supported endpoints and connectors to cover a large set of data sources. After we build the solution, we will test the Text-to-SQL capability at different realistic scenarios with varying SQL complexity levels. Finally, we will explain how a different data-source can be easily incorporated using our solution. Along with these results, you can observe our solutions architecture, workflow and the code-base snippets for you to implement this solution for your business.


### Solution Architecture
<img width="434" alt="image" src="https://github.com/aws-samples/text-to-sql-for-athena/assets/84034588/0c523340-0d7d-4da0-a409-1583a04184fe">

#### Process Walkthrough
1.	[Preparation] Create the Data Catalog on AWS Glue using AWS Glue Crawler or a different method. 
2.	[Preparation] Using Titan-Text- Embeddings model on Amazon Bedrock, convert meta-data into embeddings and store it in OpenSearch vector store, which will be our knowledge-base in our RAG framework.
At this stage, the process is ready to receive the query in natural language. Hence, it starts with;
3.	User putting their query in natural language. Here, you can use any web-application to provide the chat UI. Hence, we did not cover the UI details in our post.
4.	Apply RAG framework via the similarity search which would add the extra context from the metadata from the vector database that we formed in Step-2. This table is used for finding the correct table, database and attributes.
5.	Merging the query with the context is sent to Claude v2.1 on Amazon Bedrock.
6.	Get the generated SQL query and connect to Athena to validate the syntax. 
7.	[Correction loop, if applicable] If Athena provides an error message that mentions the syntax is incorrect, we will receive use the error text from Athena’s response.
8.	[Correction loop, if applicable] The new prompt now adds the Athena’s response. 
9.	[Correction loop, if applicable] Create the corrected SQL and continue the process. This iteration can be performed multiple times.
10.	Finally, execute SQL using Athena and generate output. Here, the output is presented to the user. For the sake of architectural simplicity, we did not show this step.

## Using the repo
Please start with [the notebook](https://github.com/aws-samples/text-to-sql-for-athena/blob/main/BedrockTextToSql_for_Athena.ipynb)

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

