from bigse.celery import app
import numpy as np
import faiss
import os

from bigse.database import manager


@app.task(ignore_result=True, name="update_index")
def update_index():

    dbm = manager.DatabaseInteractionManager()

    ids, embeddings = dbm.get_ids_embeddings_not_added()
    embeddings = np.array([embedding for embedding in embeddings]).astype("float32")
    converted_ids = np.array([id for id in ids]).astype("int64")



    print(f'id: {converted_ids.shape}, emb: {embeddings.shape}')

    try:
        index = faiss.read_index(os.environ['INDEX'])
    except:
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index = faiss.IndexIDMap(index)

    if converted_ids.size > 0:
        index.add_with_ids(embeddings, converted_ids)

        for id in ids:
            print(f'added the id {id}')
            dbm.set_doc_as_added(id)

        faiss.write_index(index, 'walid.index')

    dbm.close_connection()