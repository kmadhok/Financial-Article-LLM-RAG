from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Access the environment variables
news_api_key = os.environ.get('NewsAPIKEY')
openai_api_key = os.environ.get('OpenAIAPIKEY')
google_api_key = os.environ.get('GOOGLE_API_KEY')
finnhub_api_key = os.environ.get('FinnHub_API')

# Use the API keys in your code
print(f"FinnHub API Key: {finnhub_api_key}")
print(f"News API Key: {news_api_key}")
print(f"OpenAI API Key: {openai_api_key}")
print(f"Google API Key: {google_api_key}")

def queryrewriting_openai(query):
    query_rewriting_content = """You are an AI assistant tasked with reformulating user queries to improve retrieval in a stock news analysis system. 
    Given the original query, rewrite it to be more specific, detailed, and likely to retrieve relevant information about stock market news and analysis. 
    Keep the message of the original query, however improve it so a Large Language Model can understand it better.
    Original query: {query}

    Rewritten query:
    """.format(query=query)
    print("Original query is: ", query)
    messages = [
        ChatMessage(
            role="system", content=query_rewriting_content
        ),
        ChatMessage(role="user", content=query),
    ]
    
    resp = OpenAI().chat(messages)

    print("Updated query is: ", resp)
    response=resp.message.content
    
    return response