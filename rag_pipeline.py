from llama_index.core import Document, Settings, StorageContext
import logging
from helper_functions import chunking, manage_vector_store_path, gemini_load_model, load_gemini_embed_model, chunking_sentance
import tempfile
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.core.prompts import PromptTemplate
from llama_index.core.llms import ChatMessage
from llama_index.llms.gemini import Gemini
import shutil
from vector_store import manage_vector_store_path
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
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
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')


def setup_rag_pipeline(article_content):
    logger.debug("Setting up RAG pipeline")
    Settings.llm = gemini_load_model()
    Settings.embed_model = load_gemini_embed_model()
    #CHUNK_SIZE = 1
    CHUNK_SIZE = 512
    Settings.chunk_size = CHUNK_SIZE

    document = Document(text=article_content)
    nodes = chunking([document])
    #nodes = chunking_sentance([document])


    # Create a temporary directory for the vector store
    temp_dir = tempfile.mkdtemp()
    logger.debug(f"Created temporary directory for vector store: {temp_dir}")

    try:
        # Manage the vector store path
        manage_vector_store_path(temp_dir)

        # Set up Chroma vector store
        db = chromadb.PersistentClient(path=temp_dir)
        chroma_collection = db.create_collection("article_collection")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Create index
        index = VectorStoreIndex(
            nodes,
            storage_context=storage_context,
            show_progress=True
        )

        # query_engine = index.as_query_engine(
        #     similarity_top_k=5,
        #     streaming=True,
        #     verbose=True
        # )

        # Define the new prompt template
        qa_prompt_tmpl_str = """\
        Context information is below.
        ---------------------
        {context_str}
        ---------------------
        You are a subject matter expert in understanding articles. You are tasked with providing a response to the client given the query which explains the question in the article they are facing.
        Given the following article, provide a detailed summary that includes the main points, key arguments, and any significant insights or conclusions. 
        Additionally, identify any implicit assumptions, the tone of the article, and how the article's conclusions might impact its target audience. 
        If applicable, suggest any potential questions that readers might have after reading this article.
        The user does not see the context in the response
        Query: {query_str}
        Answer: \
        """

        # Create the prompt template
        prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)

        # Create the query engine with the new prompt template
        query_engine = index.as_query_engine(
            similarity_top_k=5,
            streaming=True,
            verbose=True,
            text_qa_template=prompt_tmpl
        )

        return query_engine, temp_dir
    
    except Exception as e:
        logger.error(f"Error in setup_rag_pipeline: {e}")
        shutil.rmtree(temp_dir)  # Clean up in case of an error
        raise



def summarize_article_content(article_content):
    logger.debug("Summarizing article content using Gemini")
    
    # Load the Gemini model
    llm = gemini_load_model()

    # Create a prompt to summarize the article content
    prompt = f"Please summarize the following article:\n\n{article_content}\n\nSummary:"
    
    # Send the request to Gemini
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant tasked with summarizing articles."),
        ChatMessage(role="user", content=prompt)
    ]
    
    try:
        response = llm.chat(messages)
        logger.debug("Response is, {response}")
        response_message_content=response.message.content
        logger.debug("response message context is {response_message_content}")
        print('response message context is: ', response_message_content)
        return response_message_content
        #return response
    except Exception as e:
        logger.error(f"Error summarizing article content: {e}")
        return "Failed to generate a summary."