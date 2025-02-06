import streamlit as st
from rag_pipeline import setup_rag_pipeline, summarize_article_content
from fetch_urls_newsapi import fetch_urls_from_newsapi
from scraper_llm import extract_article_content
from streamlit_actions  import clear_previous_data, reset_article_state
from query_rewritting import queryrewriting_openai
import logging
import os
from dotenv import load_dotenv
import finnhub
load_dotenv()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Access the environment variables
news_api_key = os.environ.get('NewsAPIKEY')
openai_api_key = os.environ.get('OpenAIAPIKEY')
google_api_key = os.environ.get('GOOGLE_API_KEY')
finnhub_api_key = os.environ.get('FinnHub_API')
#finnhub_client = finnhub.Client(api_key=finnhub_api_key)
# Use the API keys in your code
print(f"FinnHub API Key: {finnhub_api_key}")
print(f"News API Key: {news_api_key}")
print(f"OpenAI API Key: {openai_api_key}")
print(f"Google API Key: {google_api_key}")

# Example usage
if finnhub_api_key:
    # Initialize your Finnhub client
    finnhub_api_key = finnhub_api_key.strip("'")  # Remove any surrounding quotes
    finnhub_client = finnhub.Client(api_key=finnhub_api_key)
else:
    print("FinnHub API key is not set")




def get_stock_symbol(company_name):
    try:
        if finnhub_api_key:
            # Initialize your Finnhub client
            finnhub_api_key = finnhub_api_key.strip("'")  # Remove any surrounding quotes
            finnhub_client = finnhub.Client(api_key=finnhub_api_key)
        else:
            print("FinnHub API key is not set")
        # Search for the company symbol using Finnhub's API
        result = finnhub_client.symbol_lookup(company_name)
        if result['count'] > 0:
            return result['result'][0]['symbol']
        else:
            return None
    except Exception as e:
        logger.error(f"Error fetching stock symbol for {company_name}: {e}")
        return None
    
def main():
    st.set_page_config(page_title="Stock News Analysis Assistant", page_icon="📈", layout="wide")
    st.title("Stock News Analysis Assistant")

    if "stock_symbol" not in st.session_state:
        st.session_state.stock_symbol = ""
    if "articles" not in st.session_state:
        st.session_state.articles = []
    if "selected_article" not in st.session_state:
        st.session_state.selected_article = None
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = []  # List to store portfolio of stocks

    # Sidebar for stock symbol input and article selection
    with st.sidebar:
        st.header("Stock Portfolio")
        new_stock_symbol = st.text_input("Add a stock symbol to your portfolio (e.g., AAPL, GOOGL)", value="")
        
        if st.button("Add Stock to Portfolio"):
            if new_stock_symbol and new_stock_symbol not in st.session_state.portfolio:
                st.session_state.portfolio.append(new_stock_symbol)
            elif new_stock_symbol in st.session_state.portfolio:
                st.warning("Stock already in portfolio.")

        st.subheader("Your Portfolio")
        # if st.session_state.portfolio:
        #     for stock in st.session_state.portfolio:
        #         if st.button(stock):
        #             st.session_state.stock_symbol = stock
        #             st.session_state.articles = []  # Reset articles when stock symbol changes
        #             reset_article_state()  # Reset article-related state
        #             st.success(f"Selected {stock} from your portfolio.")
        # Display the portfolio stocks in a single row
        if st.session_state.portfolio:
            st.subheader("Your Portfolio")
            num_columns = len(st.session_state.portfolio)
            cols = st.columns(num_columns)

            for idx, stock in enumerate(st.session_state.portfolio):
                with cols[idx]:
                    if st.button(stock):
                        st.session_state.stock_symbol = stock
                        st.session_state.articles = []  # Reset articles when stock symbol changes
                        reset_article_state()  # Reset article-related state
                        st.success(f"Selected {stock} from your portfolio.")
        else:
            st.info("No stocks in your portfolio. Add stocks to see them here.")

        if st.session_state.stock_symbol:
            if st.button("Fetch News Articles"):
                logger.debug(f"Fetching news for stock symbol: {st.session_state.stock_symbol}")
                with st.spinner("Fetching news articles..."):
                    st.session_state.articles = fetch_urls_from_newsapi(news_api_key, st.session_state.stock_symbol)
                if st.session_state.articles:
                    st.success(f"Found {len(st.session_state.articles)} articles for {st.session_state.stock_symbol}")
                else:
                    st.warning(f"No articles found for {st.session_state.stock_symbol}. Try a different stock symbol.")
        # Fetch and display stock price and basic financials
                # with st.spinner("Fetching stock data..."):
                #     try:
                #         quote = finnhub_client.quote(st.session_state.stock_symbol)
                #         financials = finnhub_client.company_basic_financials(st.session_state.stock_symbol, 'all')
                        
                #         st.subheader(f"Stock Price for {st.session_state.stock_symbol}")
                #         st.write(f"Current Price: ${quote['c']}")
                #         st.write(f"Open: ${quote['o']}")
                #         st.write(f"High: ${quote['h']}")
                #         st.write(f"Low: ${quote['l']}")
                #         st.write(f"Previous Close: ${quote['pc']}")

                #         st.subheader("Basic Financials")
                #         if 'metric' in financials:
                #             for key, value in financials['metric'].items():
                #                 st.write(f"{key}: {value}")
                #         else:
                #             st.write("No financial data available.")
                #     except Exception as e:
                #         st.error(f"Failed to fetch stock data: {e}")
                # Fetch and display stock price and basic financials, and store them in session_state
                with st.spinner("Fetching stock data..."):
                    try:
                        quote = finnhub_client.quote(st.session_state.stock_symbol)
                        financials = finnhub_client.company_basic_financials(st.session_state.stock_symbol, 'all')
                        
                        st.session_state.stock_data = {
                            'current_price': quote['c'],
                            'open': quote['o'],
                            'high': quote['h'],
                            'low': quote['l'],
                            'previous_close': quote['pc'],
                            'financials': financials['metric'] if 'metric' in financials else {}
                        }
                        st.session_state.stock_data_fetched = True
                    except Exception as e:
                        st.error(f"Failed to fetch stock data: {e}")
        if st.session_state.get('stock_data_fetched', False):
            st.subheader(f"Stock Price for {st.session_state.stock_symbol}")
            st.write(f"Current Price: ${st.session_state.stock_data['current_price']}")
            st.write(f"Open: ${st.session_state.stock_data['open']}")
            st.write(f"High: ${st.session_state.stock_data['high']}")
            st.write(f"Low: ${st.session_state.stock_data['low']}")
            st.write(f"Previous Close: ${st.session_state.stock_data['previous_close']}")

            st.subheader("Basic Financials")
            if st.session_state.stock_data['financials']:
                for key, value in st.session_state.stock_data['financials'].items():
                    st.write(f"{key}: {value}")
            else:
                st.write("No financial data available.")

        if st.session_state.get('article_summary', False):
            st.sidebar.subheader("Article Summary")
            st.sidebar.markdown(st.session_state.article_summary)
        if st.session_state.articles:
            st.header("Article Selection")
            article_titles = [article['title'] for article in st.session_state.articles] + ["Custom URL"]
            selected_title = st.selectbox("Choose an article", options=article_titles)
            
            if selected_title == "Custom URL":
                selected_url = st.text_input("Paste your custom URL here")
                if selected_url:
                    st.session_state.selected_article = {'url': selected_url, 'title': "Custom Article"}
                    print("Selected custom URL:", selected_url)
            else:
                selected_article = next((article for article in st.session_state.articles if article['title'] == selected_title), None)
                if selected_article:
                    st.session_state.selected_article = selected_article
                    print("Selected article:", selected_article)
                    st.markdown(f"**Source:** {selected_article['source']}")
                    st.markdown(f"**Description:** {selected_article['description']}")
                    st.markdown(f"**URL:** {selected_article['url']}")
                    st.markdown(f"**Published At:** {selected_article['publishedAt']}")

    if st.button("Analyze Article"):
        if st.session_state.selected_article:
            logger.debug("Analyze Article button clicked")
            clear_previous_data()  # Clear previous article data
            with st.spinner("Extracting and analyzing article content..."):
                article_content = extract_article_content(st.session_state.selected_article['url'], openai_api_key)
                if article_content:
                    logger.debug(f"Article content extracted successfully. Length: {len(article_content)}")
                    query_engine, temp_dir = setup_rag_pipeline(article_content)
                    response=summarize_article_content(article_content)
                    st.sidebar.subheader("Article Summary")
                    st.sidebar.markdown(response)
                    st.session_state.article_content = article_content
                    st.session_state.query_engine = query_engine
                    st.session_state.temp_dir = temp_dir
                    logger.debug("RAG pipeline setup completed")
                    # Generate the summary with Gemini LLM
                    #with st.spinner("Generating summary with Gemini LLM..."):
                    #    summary = generate_summary_with_gemini(article_content)
                    #    st.session_state.article_summary = summary
                
                    st.success("Article analyzed successfully!")

                    # Display the summary in the sidebar
                    #with st.sidebar:
                    #    st.header("Article Summary")
                    #    st.write(st.session_state.article_summary)
                else:
                    st.error("Failed to extract article content. Please try another article.")
        else:
            st.warning("Please select an article before analyzing.")

    # Main area for displaying article content and Q&A
    if 'article_content' in st.session_state and 'query_engine' in st.session_state:
        st.header(f"Analysis for {st.session_state.stock_symbol}")
        
        st.subheader(st.session_state.selected_article['title'])
        st.markdown(f"**Source:** {st.session_state.selected_article['source']}")
        st.markdown(f"**URL:** {st.session_state.selected_article['url']}")
        
        st.subheader("Article Content")
        with st.expander("Click to expand/collapse full article content", expanded=False):
            st.markdown(st.session_state.article_content)
        
        st.subheader("Ask Questions About the Article")
        if 'messages' not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask a question about the article"):
            logger.debug(f"User input received: {prompt}")

            revised_prompt = queryrewriting_openai(prompt)
            logger.debug(f"Revised user input is: {revised_prompt}")
            
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        logger.debug("Input for query engine is {revised_prompt}")
                        streaming_response = st.session_state.query_engine.query(revised_prompt)
                        full_response = ""
                        response_placeholder = st.empty()
                        for text in streaming_response.response_gen:
                            full_response += text
                            response_placeholder.markdown(full_response + "")
                        logger.debug(f"Full response generated: {full_response}")
                        
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                    except Exception as e:
                        logger.error(f"Error during query processing: {e}")
                        st.error(f"An error occurred: {e}")

    elif st.session_state.stock_symbol:
        st.info("Select an article from the sidebar and click 'Analyze Article' to start the analysis.")
    else:
        st.info("Enter a stock symbol in the sidebar to begin.")



if __name__ == "__main__":
    main()
