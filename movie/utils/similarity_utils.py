# movie/utils/similarity_utils.py
import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from movie.models import Movie

# === Carga la API key solo si se necesita generar embeddings nuevos ===
if os.path.exists("openAI.env"):
    load_dotenv(dotenv_path='openAI.env')
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str) -> np.ndarray:
    """Genera el embedding de un texto usando OpenAI."""
    if not client:
        raise ValueError("No se encontró la clave OPENAI_API_KEY.")
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

def bytes_to_array(b: bytes) -> np.ndarray | None:
    """Convierte un BinaryField (bytes) en un vector numpy."""
    if not b:
        return None
    # Intentar float32, fallback float64
    try:
        arr = np.frombuffer(b, dtype=np.float32)
        if arr.size > 0:
            return arr
    except Exception:
        pass
    return np.frombuffer(b, dtype=np.float64).astype(np.float32)

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calcula la similitud coseno entre dos embeddings."""
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)

def recommend_movie(prompt: str):
    """
    Devuelve (película más similar, score de similitud).
    Usa los embeddings locales guardados en Movie.emb.
    Si alguna película no tiene emb, puede generarlo en tiempo real.
    """
    if not prompt:
        return None, None

    # Embedding del prompt (1 llamada a OpenAI)
    prompt_emb = get_embedding(prompt)

    best_movie = None
    best_score = -1.0

    for movie in Movie.objects.all():
        # Si no tiene descripción, saltar
        if not movie.description:
            continue

        # Recuperar embedding desde BD
        mvec = bytes_to_array(movie.emb)
        if mvec is None or mvec.size == 0:
            # Si no tiene embedding guardado, generarlo (solo si quieres permitirlo)
            try:
                mvec = get_embedding(movie.description)
            except Exception as e:
                print(f"❌ Error generando embedding de '{movie.title}': {e}")
                continue

        # Calcular similitud
        score = cosine_similarity(prompt_emb, mvec)
        if score > best_score:
            best_score = score
            best_movie = movie

    return best_movie, best_score
