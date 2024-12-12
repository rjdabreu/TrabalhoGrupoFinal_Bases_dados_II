from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from db_config import get_mysql_connection

app = Flask(__name__)
CORS(app)
api = Api(app)

class Recommendations(Resource):
    def get(self):
        try:
            connection = get_mysql_connection()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT livros.id, livros.titulo, COUNT(emprestimos.id) AS total_emprestimos
                FROM livros
                JOIN emprestimos ON livros.id = emprestimos.id_livro
                GROUP BY livros.id, livros.titulo
                ORDER BY total_emprestimos DESC
                LIMIT 5
            """)
            recommendations = cursor.fetchall()

            return recommendations if recommendations else {"message": "Nenhuma recomendação encontrada."}, 200
        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            cursor.close()
            connection.close()

api.add_resource(Recommendations, '/recommendations')

if __name__ == "__main__":
    app.run(debug=True, port=5004)
