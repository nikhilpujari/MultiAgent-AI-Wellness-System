import faiss, os, json, numpy as np
from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)
INDEX_PATH = "data/embeddings.index"
META_PATH = "data/meta.json"

def embed_texts(texts):
    r = client.embeddings.create(model=settings.EMBEDDING_MODEL, input=texts)
    vecs = [d.embedding for d in r.data]
    return np.array(vecs).astype("float32")

def build_index():
    docs, metas = [], []
    for f in os.listdir("data/seed_docs"):
        path = os.path.join("data/seed_docs", f)
        txt = open(path, "r", encoding="utf-8").read()
        for i, chunk in enumerate(txt.split("\n\n")):
            docs.append(chunk)
            metas.append({"file": f, "chunk": i})
    vecs = embed_texts(docs)
    faiss.normalize_L2(vecs)
    index = faiss.IndexFlatIP(vecs.shape[1])
    index.add(vecs)
    faiss.write_index(index, INDEX_PATH)
    json.dump({"docs": docs, "metas": metas}, open(META_PATH, "w"))
    print("FAISS index built.")

def search(query, k=3):
    index = faiss.read_index(INDEX_PATH)
    meta = json.load(open(META_PATH))
    qv = embed_texts([query])
    faiss.normalize_L2(qv)
    D, I = index.search(qv, k)
    return [meta["docs"][i] for i in I[0] if i != -1]
