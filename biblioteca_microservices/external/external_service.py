from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)
api = Api(app)

class ExternalBooks(Resource):
    def get(self):
        """Pesquisar livros de uma API externa."""
        query = request.args.get('query')
        if not query:
            return {"error": "O parâmetro 'query' é obrigatório."}, 400

        try:
            response = requests.get(f"https://openlibrary.org/search.json?q={query}")
            response.raise_for_status()
            data = response.json()

            books = [
                {
                    "title": doc.get("title"),
                    "author": doc.get("author_name", ["Autor desconhecido"])[0],
                }
                for doc in data.get("docs", [])[:10]
            ]
            return books, 200
        except requests.RequestException as e:
            return {"error": "Erro ao consultar API externa."}, 500

api.add_resource(ExternalBooks, '/external-books')

if __name__ == "__main__":
    app.run(debug=True, port=5003)
