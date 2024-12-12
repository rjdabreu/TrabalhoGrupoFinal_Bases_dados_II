from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from db_config import get_mysql_connection

app = Flask(__name__)
CORS(app)
api = Api(app)

class Books(Resource):
    def get(self):
        """Listar todos os livros ou realizar pesquisas avançadas."""
        try:
            connection = get_mysql_connection()
            cursor = connection.cursor()

            search = request.args.get('search', '')
            sort_by = request.args.get('sort_by', 'titulo')  # Ordenação padrão: título

            query = "SELECT id, titulo, autor FROM livros WHERE 1=1"
            params = []

            if search:
                query += " AND (titulo LIKE %s OR autor LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%"])

            if sort_by in ['titulo', 'autor']:
                query += f" ORDER BY {sort_by}"

            cursor.execute(query, params)
            books = cursor.fetchall()

            return books if books else {"message": "Nenhum livro encontrado."}, 200
        except Exception as e:
            return {"error": f"Erro ao pesquisar livros: {str(e)}"}, 500
        finally:
            cursor.close()
            connection.close()

    def post(self):
        """Adicionar um novo livro."""
        try:
            connection = get_mysql_connection()
            cursor = connection.cursor()

            data = request.get_json()
            titulo = data.get("titulo")
            autor = data.get("autor")
            if not titulo or not autor:
                return {"error": "Título e autor são obrigatórios."}, 400

            cursor.execute("INSERT INTO livros (titulo, autor) VALUES (%s, %s)", (titulo, autor))
            connection.commit()

            return {"message": "Livro adicionado com sucesso!"}, 201
        except Exception as e:
            return {"error": f"Erro ao adicionar livro: {str(e)}"}, 500
        finally:
            cursor.close()
            connection.close()

api.add_resource(Books, '/books')

if __name__ == "__main__":
    app.run(debug=True, port=5001)
