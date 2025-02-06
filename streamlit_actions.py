from vector_store import manage_vector_store_path
import streamlit as st
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def clear_previous_data():
    if 'temp_dir' in st.session_state and st.session_state.temp_dir:
        logger.debug(f"Clearing previous vector store: {st.session_state.temp_dir}")
        manage_vector_store_path(st.session_state.temp_dir)
        st.session_state.temp_dir = None
    st.session_state.article_content = None
    st.session_state.query_engine = None
    st.session_state.messages = []

def reset_article_state():
    if 'article_content' in st.session_state:
        del st.session_state.article_content
    if 'query_engine' in st.session_state:
        del st.session_state.query_engine
    if 'messages' in st.session_state:
        del st.session_state.messages