from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import re, string, unicodedata, pathlib, math
from collections import Counter, defaultdict

import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

# ========== NLTK Setup ==========
nltk_data_dir = pathlib.Path("nltk_data")
nltk_data_dir.mkdir(exist_ok=True)
nltk.data.path.append(str(nltk_data_dir))

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", download_dir=str(nltk_data_dir), quiet=True)

# ========== FastAPI App ==========
app = FastAPI(title="Chatbot API")

# ✅ Enable CORS
origins = [
    "http://localhost:4200",  # Angular dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or use ["*"] for all origins (not recommended in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== Load Dataset ==========
data = pd.read_csv("combined_faq_dataset.csv")
data = data.rename(columns={"Réponse": "Answer"})
data["Class"] = range(len(data))

# ========== Text Preprocessing ==========
stemmer = SnowballStemmer("french")
STOPWORDS_FR = set(stopwords.words("french"))

def cleanup(text: str) -> str:
    text = unicodedata.normalize("NFKC", text.lower())
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = text.translate(str.maketrans("", "", string.digits + string.punctuation))
    tokens = re.findall(r"\b\w+\b", text, flags=re.UNICODE)
    tokens = [stemmer.stem(t) for t in tokens if t not in STOPWORDS_FR]
    return " ".join(tokens)

docs_tokens = [cleanup(q).split() for q in data["Question"]]
N = len(docs_tokens)

df = defaultdict(int)
for tokens in docs_tokens:
    for tok in set(tokens):
        df[tok] += 1

idf = {tok: math.log(N / df[tok]) for tok in df}

def tf_idf(tokens):
    tf = Counter(tokens)
    tot = len(tokens)
    return {tok: (cnt / tot) * idf[tok] for tok, cnt in tf.items() if tok in idf}

question_vecs = [tf_idf(toks) for toks in docs_tokens]

def cosine(vec1: dict, vec2: dict) -> float:
    inter = set(vec1) & set(vec2)
    num = sum(vec1[t] * vec2[t] for t in inter)
    norm1 = math.sqrt(sum(v * v for v in vec1.values()))
    norm2 = math.sqrt(sum(v * v for v in vec2.values()))
    return 0.0 if norm1 == 0 or norm2 == 0 else num / (norm1 * norm2)

def _is_in(text: str, phrases) -> bool:
    txt = text.translate(str.maketrans("", "", string.punctuation)).lower()
    return txt in phrases

def get_response(user_text: str) -> str:
    if user_text.lower() == "bye":
        return "Au revoir ! 👋"

    greetings = {"hello", "hi", "salut", "bonjour", "hey"}
    thanks    = {"thanks", "merci"}
    okays     = {"ok", "d’accord", "daccord"}

    if _is_in(user_text, greetings):
        return "Bonjour ! Comment puis-je vous aider ? 😊"
    if _is_in(user_text, thanks):
        return "Avec plaisir !"
    if _is_in(user_text, okays):
        return "D’accord !"

    query_vec = tf_idf(cleanup(user_text).split())
    sims = [cosine(query_vec, qv) for qv in question_vecs]
    best_idx = max(range(len(sims)), key=sims.__getitem__)
    best_sim = sims[best_idx]

    if best_sim < 0.20:
        return "Désolé, je n’ai pas la réponse pour le moment."
    return data.iloc[best_idx]["Answer"]

# ========== API Models ==========
class Question(BaseModel):
    text: str

class Answer(BaseModel):
    answer: str

# ========== Routes ==========
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/ask", response_model=Answer)
def ask_question(q: Question):
    response = get_response(q.text)
    return {"answer": response}