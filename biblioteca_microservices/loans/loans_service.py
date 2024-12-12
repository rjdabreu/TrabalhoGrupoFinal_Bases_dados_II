from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from db_config import get_mysql_connection
from datetime import datetime, date
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)
api = Api(app)

# Configuração do MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["biblioteca_logs"]
user_logs = mongo_db["user_logs"]

class Borrow(Resource):
    def post(self):
        try:
            connection = get_mysql_connection()
            cursor = connection.cursor()

            data = request.get_json()
            user_id = data.get('user_id')
            book_id = data.get('book_id')

            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not cursor.fetchone():
                return {"error": "Utilizador não encontrado."}, 404

            cursor.execute("SELECT id FROM livros WHERE id = %s", (book_id,))
            if not cursor.fetchone():
                return {"error": "Livro não encontrado."}, 404

            cursor.execute("SELECT id FROM emprestimos WHERE id_livro = %s AND data_devolucao IS NULL", (book_id,))
            if cursor.fetchone():
                return {"error": "Livro já está emprestado."}, 400

            cursor.execute("""
                INSERT INTO emprestimos (id_users, id_livro, data_emprestimo) 
                VALUES (%s, %s, NOW())
            """, (user_id, book_id))
            connection.commit()

            user_logs.insert_one({
                "user_id": user_id,
                "action": "borrow",
                "book_id": book_id,
                "timestamp": datetime.now().isoformat()
            })

            return {"message": "Empréstimo registrado com sucesso!"}, 201
        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            cursor.close()
            connection.close()

class Return(Resource):
    def put(self):
        try:
            connection = get_mysql_connection()
            cursor = connection.cursor()

            data = request.get_json()
            user_id = data.get('user_id')
            book_id = data.get('book_id')

            cursor.execute("""
                SELECT id FROM emprestimos 
                WHERE id_users = %s AND id_livro = %s AND data_devolucao IS NULL
            """, (user_id, book_id))
            if not cursor.fetchone():
                return {"error": "Nenhum empréstimo ativo encontrado."}, 404

            cursor.execute("""
                UPDATE emprestimos 
                SET data_devolucao = NOW() 
                WHERE id_users = %s AND id_livro = %s AND data_devolucao IS NULL
            """, (user_id, book_id))
            connection.commit()

            user_logs.insert_one({
                "user_id": user_id,
                "action": "return",
                "book_id": book_id,
                "timestamp": datetime.now().isoformat()
            })

            return {"message": "Devolução registrada com sucesso!"}, 200
        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            cursor.close()
            connection.close()

api.add_resource(Borrow, '/borrow')
api.add_resource(Return, '/return')

if __name__ == "__main__":
    app.run(debug=True, port=5002)
