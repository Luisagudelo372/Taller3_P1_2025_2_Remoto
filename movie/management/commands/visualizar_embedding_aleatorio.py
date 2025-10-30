import os
import numpy as np
import random
from django.core.management.base import BaseCommand
from movie.models import Movie  # Asegúrate de que 'movie' sea el nombre correcto de tu app
from openai import OpenAI
from dotenv import load_dotenv

class Command(BaseCommand):
    help = "Visualiza los embeddings de una película seleccionada aleatoriamente"

    def handle(self, *args, **kwargs):
        # ✅ Cargar la clave de API de OpenAI
        load_dotenv(dotenv_path='openAI.env')
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # ✅ Obtener todas las películas de la base de datos
        movies = Movie.objects.all()

        # Si no hay películas en la base de datos, devolver un error
        if not movies:
            self.stdout.write("No hay películas en la base de datos.")
            return

        # ✅ Seleccionar una película al azar
        movie = random.choice(movies)

        self.stdout.write(f"Película seleccionada aleatoriamente: {movie.title}")

        # ✅ Obtener el embedding de la descripción de la película
        def get_embedding(text):
            response = client.embeddings.create(
                input=[text],
                model="text-embedding-3-small"
            )
            return np.array(response.data[0].embedding, dtype=np.float32)

        # ✅ Generar el embedding para la descripción de la película seleccionada
        emb = get_embedding(movie.description)

        # ✅ Mostrar el embedding en la consola
        self.stdout.write(f"\nEmbeding de la película '{movie.title}':\n")
        self.stdout.write(f"{emb}")

        # ✅ Mostrar la longitud del embedding
        self.stdout.write(f"\nLongitud del embedding: {len(emb)} dimensiones")
