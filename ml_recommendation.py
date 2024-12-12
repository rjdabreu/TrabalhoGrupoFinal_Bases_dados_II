import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

def generate_recommendations(user_id, historical_data):
    """
    Gera recomendações de livros com base no histórico de empréstimos.

    Args:
        user_id (int): ID do utilizador.
        historical_data (pd.DataFrame): Dados históricos contendo 'user_id', 'book_id', 'title', 'genre'.

    Returns:
        list: Lista de recomendações.
    """
    # Filtrar histórico do usuário
    user_history = historical_data[historical_data['user_id'] == user_id]

    if user_history.empty:
        return ["Nenhum histórico encontrado para este usuário."]

    # Combinar todos os livros no histórico do usuário
    user_books = user_history['title'] + " " + user_history['genre']

    # Criar matriz TF-IDF
    tfidf_vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf_vectorizer.fit_transform(user_books)

    # Calcular similaridade entre os livros
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Escolher os livros mais similares
    similar_books = similarity_matrix.mean(axis=0).argsort()[-5:][::-1]
    recommendations = historical_data.iloc[similar_books]['title'].tolist()

    return recommendations
