from sentence_transformers import SentenceTransformer

def embed_sentences(sentences: str, model):
    # Model di-load setiap kali fungsi dipanggil
    
    embeddings = model.encode(
        sentences,
        convert_to_numpy=True, 
        normalize_embeddings=True # Bagus! Mempermudah perhitungan Cosine Similarity via Dot Product
    )
    
    # Konversi dari numpy array ke list biasa sebelum disimpan ke DB
    return embeddings.tolist()