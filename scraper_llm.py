
import logging
from dotenv import load_dotenv
import os
from scrapegraphai.graphs import SmartScraperGraph

load_dotenv()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

openai_api_key = os.getenv('OpenAIAPIKEY')
os.environ["OPENAI_API_KEY"] = openai_api_key


def extract_article_content(_url, _openai_api_key):
    logger.debug(f"Extracting content from URL: {_url}")
    graph_config = {
        "llm": {
            "api_key": _openai_api_key,
            "model": "gpt-4o-mini",
        },
        "verbose": True,
        "headless": True,
    }
    
    smart_scraper_graph = SmartScraperGraph(
        prompt="Find the content of the article. Please return the whole content of the article.",
        source=_url,
        config=graph_config
    )
    
    try:
        result = smart_scraper_graph.run()
        logger.debug(f"Extracted result is: {result}")
        content = result.get('article_content', '')
        logger.debug(f"Extracted content (first 100 chars): {content[:100]}")
        return content
    except Exception as e:
        logger.error(f"Error extracting article content: {e}")
        return None