import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# ── constants ──────────────────────────────────────────────
MODEL_NAME   = 'all-MiniLM-L6-v2'   # small, fast, free model (22MB)
EMBEDDING_DIM = 384                  # this model always produces 384 numbers
INDEX_PATH   = 'media/faiss_index.bin'  # where we save the FAISS index on disk
MAP_PATH     = 'media/doc_id_map.npy'   # maps FAISS position → Document DB id

# ── load model once (loading is slow, do it once at startup) ─
_model = None

def get_model():
    """Load the AI model. Cached so it only loads once."""
    global _model
    if _model is None:
        print("Loading AI model... (first time only, ~5 seconds)")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


# ── index management ────────────────────────────────────────

def load_index():
    """
    Load FAISS index + doc_id map from disk.
    If no index exists yet, create an empty one.
    """
    if os.path.exists(INDEX_PATH) and os.path.exists(MAP_PATH):
        index  = faiss.read_index(INDEX_PATH)
        id_map = np.load(MAP_PATH).tolist()
    else:
        # flat L2 = exact nearest-neighbour search, fine for small datasets
        index  = faiss.IndexFlatL2(EMBEDDING_DIM)
        id_map = []   # list of Document DB ids in the same order as FAISS vectors
    return index, id_map


def save_index(index, id_map):
    """Save FAISS index + doc_id map to disk so it survives server restarts."""
    os.makedirs('media', exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    np.save(MAP_PATH, np.array(id_map))


# ── core operations ─────────────────────────────────────────

def add_document_to_index(doc_id: int, text: str):
    """
    Convert text to embedding and add it to the FAISS index.
    Call this every time a new document is uploaded.
    """
    model  = get_model()
    index, id_map = load_index()

    # encode: text → numpy array of shape (1, 384)
    embedding = model.encode([text], convert_to_numpy=True)

    # normalise so cosine similarity works properly
    faiss.normalize_L2(embedding)

    index.add(embedding)          # add vector to FAISS
    id_map.append(doc_id)         # remember which DB document this vector belongs to

    save_index(index, id_map)
    print(f"Document {doc_id} added to FAISS index. Total vectors: {index.ntotal}")


def search_documents(query: str, top_k: int = 5):
    """
    Search FAISS for documents semantically similar to the query.
    Returns a list of Document DB ids, ordered by relevance.
    """
    model  = get_model()
    index, id_map = load_index()

    if index.ntotal == 0:
        return []   # no documents indexed yet

    # encode the query the same way we encoded documents
    query_vec = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_vec)

    # search: returns distances + positions in FAISS index
    k = min(top_k, index.ntotal)   # can't return more than we have
    distances, indices = index.search(query_vec, k)

    # convert FAISS positions → Document DB ids
    result_ids = []
    for i, faiss_pos in enumerate(indices[0]):
        if faiss_pos == -1:             # -1 means no result found
            continue
        doc_id   = id_map[faiss_pos]
        distance = float(distances[0][i])
        result_ids.append({'doc_id': doc_id, 'distance': distance})

    return result_ids   # list of {doc_id, distance} sorted best first


def rebuild_index_from_db():
    """
    Rebuild the entire FAISS index from all documents in the database.
    Call this if the index file gets lost or corrupted.
    """
    from documents.models import Document
    model = get_model()

    index  = faiss.IndexFlatL2(EMBEDDING_DIM)
    id_map = []

    docs = Document.objects.all()
    if not docs.exists():
        print("No documents in DB to index.")
        save_index(index, id_map)
        return

    texts = [doc.content for doc in docs]
    ids   = [doc.id      for doc in docs]

    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    faiss.normalize_L2(embeddings)

    index.add(embeddings)
    id_map = ids

    save_index(index, id_map)
    print(f"Rebuilt index with {index.ntotal} documents.")