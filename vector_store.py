import os
import shutil
import logging
import streamlit as st

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def manage_vector_store_path(vector_store_path):
    """
    Manages the vector store path by deleting it if it exists and then recreating it.

    Parameters:
    vector_store_path (str): The path to the vector store directory.
    """
    if os.path.exists(vector_store_path):
        try:
            shutil.rmtree(vector_store_path)
            logger.debug(f"Vector store path {vector_store_path} deleted successfully.")
        except OSError as e:
            st.write(f"Error: {vector_store_path} : {e.strerror}")
            logger.debug(f"Error deleting vector store path {vector_store_path}: {e.strerror}")

    try:
        os.makedirs(vector_store_path)
        logger.debug(f"Vector store path {vector_store_path} created successfully.")
    except OSError as e:
        st.write(f"Error: {vector_store_path} : {e.strerror}")
        logger.error(f"Error creating vector store path {vector_store_path}: {e.strerror}")
