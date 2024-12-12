from flask import Flask, request
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
        """Registrar um novo empréstimo."""
        try:
            connection = get_mysql_connection()
            cursor = connection.cursor()

            data = request.get_json()
            user_id = data.get('user_id')
            book_id = data.get('book_id')

            # Validação do utilizador
            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not cursor.fetchone():
                return {"error": "Utilizador não encontrado."}, 404

            # Validação do livro
            cursor.execute("SELECT id FROM livros WHERE id = %s", (book_id,))
            if not cursor.fetchone():
                return {"error": "Livro não encontrado."}, 404

            # Verificar disponibilidade
            cursor.execute("SELECT id FROM emprestimos WHERE id_livro = %s AND data_devolucao IS NULL", (book_id,))
            if cursor.fetchone():
                return {"error": "Livro já está emprestado."}, 400

            # Registrar o empréstimo
            cursor.execute("""
                INSERT INTO emprestimos (id_users, id_livro, data_emprestimo) 
                VALUES (%s, %s, NOW())
            """, (user_id, book_id))
            connection.commit()

            # Registrar log no MongoDB
            user_logs.insert_one({
                "user_id": user_id,
                "action": "borrow",
                "book_id": book_id,
                "timestamp": datetime.now().isoformat()
            })

            return {"message": "Empréstimo registrado com sucesso!"}, 201
        except Exception as e:
            return {"error": f"Erro ao registrar empréstimo: {str(e)}"}, 500
        finally:
            cursor.close()
            connection.close()

class Return(Resource):
    def put(self):
        """Registrar a devolução de um livro."""
        try:
            connection = get_mysql_connection()
            cursor = connection.cursor()

            data = request.get_json()
            user_id = data.get('user_id')
            book_id = data.get('book_id')

            # Verificar se existe um empréstimo ativo
            cursor.execute("""
                SELECT id FROM emprestimos 
                WHERE id_users = %s AND id_livro = %s AND data_devolucao IS NULL
            """, (user_id, book_id))
            if not cursor.fetchone():
                return {"error": "Nenhum empréstimo ativo encontrado para este utilizador e livro."}, 404

            # Registrar a devolução
            cursor.execute("""
                UPDATE emprestimos 
                SET data_devolucao = NOW() 
                WHERE id_users = %s AND id_livro = %s AND data_devolucao IS NULL
            """, (user_id, book_id))
            connection.commit()

            # Registrar log no MongoDB
            user_logs.insert_one({
                "user_id": user_id,
                "action": "return",
                "book_id": book_id,
                "timestamp": datetime.now().isoformat()
            })

            return {"message": "Devolução registrada com sucesso!"}, 200
        except Exception as e:
            return {"error": f"Erro ao registrar devolução: {str(e)}"}, 500
        finally:
            cursor.close()
            connection.close()

class Loans(Resource):
    def get(self):
        """Listar todos os empréstimos."""
        try:
            connection = get_mysql_connection()
            cursor = connection.cursor()

            user_id = request.args.get('user_id')
            query = """
                SELECT emprestimos.id, emprestimos.data_emprestimo, emprestimos.data_devolucao,
                       users.nome AS utilizador, livros.titulo AS livro
                FROM emprestimos
                JOIN users ON emprestimos.id_users = users.id
                JOIN livros ON emprestimos.id_livro = livros.id
            """
            params = []

            if user_id:
                query += " WHERE emprestimos.id_users = %s"
                params.append(user_id)

            cursor.execute(query, params)
            loans = cursor.fetchall()

            # Formatar datas para strings
            for loan in loans:
                if isinstance(loan["data_emprestimo"], (datetime, date)):
                    loan["data_emprestimo"] = loan["data_emprestimo"].strftime("%Y-%m-%d %H:%M:%S")
                if loan["data_devolucao"] and isinstance(loan["data_devolucao"], (datetime, date)):
                    loan["data_devolucao"] = loan["data_devolucao"].strftime("%Y-%m-%d")

            return loans, 200
        except Exception as e:
            return {"error": f"Erro ao pesquisar empréstimos: {str(e)}"}, 500
        finally:
            cursor.close()
            connection.close()

# Registrar os endpoints
api.add_resource(Borrow, '/borrow')
api.add_resource(Return, '/return')
api.add_resource(Loans, '/loans')

if __name__ == "__main__":
    app.run(debug=True, port=5002)
