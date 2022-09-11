import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from bigse import model
import os

from bigse.database import manager

INDEX = os.environ['INDEX']

def vector_search(query, num_results=10):
    """Tranforms query to vector using a pretrained, sentence-level
    DistilBERT model and finds similar vectors using FAISS.
    
    Args:
        query (str): User query that should be more than a sentence long.
        model (sentence_transformers.SentenceTransformer.SentenceTransformer)
        index (`numpy.ndarray`): FAISS index that needs to be deserialized.
        num_results (int): Number of results to return.
    
    Returns:
        D (:obj:`numpy.array` of `float`): Distance between results and query.
        I (:obj:`numpy.array` of `int`): Paper ID of the results.
    
    """
    vector = model.encode(list(query))
    index = faiss.read_index(INDEX)
    D, I = index.search(np.array(vector).astype("float32"), k=num_results)
    return D, I

def id2details(I):
    """Returns the paper titles based on the paper index."""
    dbm = manager.DatabaseInteractionManager()
    list = [dbm.get_doc_entry(int(idx)) for idx in I[0]]
    dbm.close_connection()
    return list
