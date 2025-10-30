from django.shortcuts import render
from movie.utils.similarity_utils import recommend_movie

def recommend(request):
    prompt = (request.GET.get('q') or '').strip()
    movie, score = (None, None)

    if prompt:
        try:
            movie, score = recommend_movie(prompt)
        except Exception as e:
            print(f"❌ Error en recomendador: {e}")

    return render(request, 'recommender/recommend.html', {
        'prompt': prompt,
        'movie': movie,
        'score': score
    })
