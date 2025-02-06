import logging
from datetime import datetime, timedelta
import requests
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


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_urls_from_newsapi(news_api_key, stock_symbol):
    logger.debug(f"Fetching URLs from NewsAPI for stock: {stock_symbol}")
    news_api_key = news_api_key.strip("'")  # Remove any surrounding quotes

    ten_days_ago = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
    
    url = (f'https://newsapi.org/v2/everything?'
           f'q={stock_symbol}&'
           f'from={ten_days_ago}&'
           f'sortBy=popularity&'
           f'apiKey={news_api_key}')
    
    response = requests.get(url)
    data = response.json()
    
    articles = []
    for article in data.get('articles', []):
        if stock_symbol.upper() in article.get('title', ''):
            articles.append({
                'source': article.get('source', {}).get('name', 'Unknown Source'),
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'publishedAt': article.get('publishedAt', '')
            })
    return articles