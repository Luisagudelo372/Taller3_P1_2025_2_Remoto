import os
import unicodedata
from django.core.management.base import BaseCommand
from django.conf import settings
from movie.models import Movie

class Command(BaseCommand):
    help = "Assign images from media/movie/images/ folder to movies in the database"

    def handle(self, *args, **kwargs):
        images_folder = os.path.join(settings.BASE_DIR, 'media', 'movie', 'images')
        updated_count = 0
        not_found_count = 0

        if not os.path.exists(images_folder):
            self.stderr.write(f"Images folder '{images_folder}' not found.")
            return

        # ✅ Indexar todos los archivos .png disponibles (sin modificar los nombres)
        available_files = os.listdir(images_folder)
        indexed_files = {
            self.normalize_filename(f): f for f in available_files if f.lower().endswith('.png')
        }

        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies in database.")

        for movie in movies:
            expected_key = self.normalize_filename(f"m_{movie.title}.png")

            # DEBUG opcional:
            # print(f"Buscando: {expected_key}")

            if expected_key in indexed_files:
                real_filename = indexed_files[expected_key]
                relative_path = os.path.join("movie/images", real_filename)

                movie.image = relative_path
                movie.save()

                self.stdout.write(self.style.SUCCESS(f"Updated image for movie: {movie.title}"))
                updated_count += 1
            else:
                self.stderr.write(f"Image not found for movie: {movie.title}")
                not_found_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Finished. Updated images for {updated_count} movies. {not_found_count} images not found."
        ))

    def normalize_filename(self, name):
        """
        Normaliza un nombre de archivo eliminando acentos y reemplazando espacios y símbolos por guiones bajos.
        """
        name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
        name = name.lower()
        name = name.strip()
        name = ''.join(char if char.isalnum() else '_' for char in name)
        while '__' in name:
            name = name.replace('__', '_')
        return name
