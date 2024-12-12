from flask import Flask, request, jsonify, redirect, session, url_for
from flask_restful import Api, Resource
from flask_cors import CORS
from datetime import datetime, date
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from biblioteca_backend.shared.db_config import get_mysql_connection
from authlib.integrations.flask_client import OAuth
from functools import wraps
from flask_mail import Mail, Message
import os
import random
from prometheus_client import generate_latest, REGISTRY, Counter, Histogram
from flask import Response, g
import time
import logging
from ml_recommendation import generate_recommendations
import pandas as pd

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

app = Flask(__name__)
app.secret_key = '84544a37be4c6948b4fee7f011dd49d9e92c8454' # Chave OAuth
CORS(app)  # Ativa o CORS para todas as rotas
api = Api(app)

# Configuração do MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["biblioteca_logs"]
user_logs = mongo_db["user_logs"]

# Configurações do GitHub OAuth
GITHUB_CLIENT_ID = "Ov23liymgS8RRnY5Uxv8"  # Client ID do GitHub
GITHUB_CLIENT_SECRET = "84544a37be4c6948b4fee7f011dd49d9e92c8454"  # Client Secret do GitHub
GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_URL = "https://api.github.com/user"

# Configuração do Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "rjdabreu@gmail.com"
app.config['MAIL_PASSWORD'] = "xicw lmjd rrpp hyvs"
app.config['MAIL_DEFAULT_SENDER'] = "MFACODE@gmail.com"
mail = Mail(app)

# Métricas Prometheus
REQUEST_COUNT = Counter('request_count', 'Total de requisições', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Latência de requisições', ['endpoint'])

@app.before_request
def before_request():
    """Antes de cada requisição, registra o início do tempo."""
    g.start_time = time.time()

@app.after_request
def after_request(response):
    """Após cada requisição, registra a latência e conta as requisições."""
    latency = time.time() - g.start_time
    REQUEST_COUNT.labels(request.method, request.path).inc()  # Incrementa a contagem
    REQUEST_LATENCY.labels(request.path).observe(latency)  # Registra a latência
    return response

@app.route('/metrics')
def metrics():
    """Endpoint para expor métricas no formato Prometheus"""
    return Response(generate_latest(REGISTRY), mimetype="text/plain")

# Função para registrar logs de ações
def log_action(user_id, action, details=""):
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO audit_logs (user_id, action, details)
            VALUES (%s, %s, %s)
        """, (user_id, action, details))
        connection.commit()
    except Exception as e:
        print(f"Erro ao registrar log de auditoria: {e}")
    finally:
        cursor.close()
        connection.close()

# Verificar funções protegidas por login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function
    
# Funções protegidas por função (role)
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = session.get('user')
            if not user or user.get('role') != role:
                return jsonify({"error": "Acesso negado."}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Rota para gerar código MFA
@app.route('/mfa/generate', methods=['POST'])
def generate_mfa_code():
    try:
        data = request.get_json()
        username = data.get("username")
        connection = get_mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT users.email 
            FROM logins 
            JOIN users ON logins.user_id = users.id 
            WHERE logins.username = %s
        """, (username,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "Utilizador não encontrado."}), 404

        email = user['email']
        mfa_code = f"{random.randint(100000, 999999)}"

        cursor.execute("UPDATE logins SET mfa_code = %s WHERE username = %s", (mfa_code, username))
        connection.commit()

        msg = Message(
            "O seu código de autenticação",
            sender=app.config['MAIL_DEFAULT_SENDER'],  # Utiliza o remetente configurado
            recipients=[email]
        )
        msg.body = f"O seu código de autenticação é: {mfa_code}"
        mail.send(msg)

        return jsonify({"message": "Código enviado por e-mail."}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao criar MFA: {str(e)}"}), 500
    finally:
        cursor.close()
        connection.close()

# Rota para validar código MFA
@app.route('/mfa/validate', methods=['POST'])
def validate_mfa_code():
    try:
        data = request.get_json()
        username = data.get("username")
        mfa_code = data.get("mfa_code")

        connection = get_mysql_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT mfa_code FROM logins WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user or user['mfa_code'] != mfa_code:
            return jsonify({"error": "Código inválido."}), 401

        cursor.execute("UPDATE logins SET mfa_code = NULL WHERE username = %s", (username,))
        connection.commit()

        return jsonify({"message": "Autenticação MFA validada com sucesso."}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao validar MFA: {str(e)}"}), 500
    finally:
        cursor.close()
        connection.close()

# Rota para iniciar o fluxo de login com OAuth
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Redireciona para o OAuth ou trata login baseado em formulário."""
    if request.method == 'POST':
        # Login baseado em formulário
        connection = get_mysql_connection()
        cursor = connection.cursor()

        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            mfa_code = data.get("mfa_code")  # Para verificar o MFA

            if not username or not password:
                return {"error": "Username e password são obrigatórios."}, 400

            cursor.execute("SELECT id, password_hash, mfa_code FROM logins WHERE username = %s", (username,))
            user = cursor.fetchone()

            if not user or not check_password_hash(user["password_hash"], password):
                return {"error": "Login ou password inválidos."}, 401

            # Verificar o MFA
            if user['mfa_code']:
                if not mfa_code:
                    return {"error": "Código MFA é obrigatório."}, 403
                if mfa_code != user['mfa_code']:
                    return {"error": "Código MFA inválido."}, 403

                # Limpar o código MFA após validação
                cursor.execute("UPDATE logins SET mfa_code = NULL WHERE username = %s", (username,))
                connection.commit()

            token = f"TOKEN-{user['id']}-{datetime.now().timestamp()}"
            return {"message": "Login realizado com sucesso.", "token": token}, 200
        except Exception as e:
            return {"error": f"Erro ao realizar login: {e}"}, 500
        finally:
            cursor.close()
            connection.close()
    else:
        # Iniciar fluxo OAuth
        github_redirect_url = f"{GITHUB_AUTH_URL}?client_id={GITHUB_CLIENT_ID}&scope=user"
        return redirect(github_redirect_url)

@app.route('/login/callback')
def login_callback():
    """Recebe o callback do GitHub com o código de autenticação."""
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "Código de autenticação ausente"}), 400

    # Troca o código por um token de acesso
    response = requests.post(
        GITHUB_TOKEN_URL,
        headers={"Accept": "application/json"},
        data={
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code
        }
    )
    token_data = response.json()

    if "access_token" not in token_data:
        return jsonify({"error": "Falha ao obter token de acesso"}), 400

    access_token = token_data["access_token"]

    # Obtém informações do utilizador autenticado
    user_response = requests.get(
        GITHUB_API_URL,
        headers={"Authorization": f"token {access_token}"}
    )
    user_data = user_response.json()

    username = user_data.get("login")
    user_id = user_data.get("id")

    if not username or not user_id:
        return jsonify({"error": "Erro ao obter informações do utilizador"}), 400

    # Verifica se o utilizador já está registrado
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM logins WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if not existing_user:
            # Registra o utilizador no sistema local
            cursor.execute(
                "INSERT INTO logins (username, password_hash) VALUES (%s, %s)",
                (username, "")  # Utilizador registrado via OAuth tem password_hash como string vazia
            )
            connection.commit()

    except Exception as e:
        return jsonify({"error": f"Erro ao registrar utilizador no sistema: {e}"}), 500
    finally:
        cursor.close()
        connection.close()

    # Guarda o utilizador na sessão
    session['user'] = {
        "username": username,
        "id": user_id,
        "avatar": user_data.get("avatar_url"),
        "profile_url": user_data.get("html_url")
    }
    print(f"Sessão configurada para o usuário: {session['user']}")
    return redirect('/github-success')
    
@app.route('/github-success')
def github_success():
    """Endpoint para notificar sucesso do login via GitHub."""
    user = session.get('user') # Verifica se há um utilizador na sessão
    if not user:
        return jsonify({"error": "Utilizador não autenticado."}), 401
    return jsonify({"message": "Login via GitHub concluído!", "user": user})

@app.route('/dashboard')
@login_required
def dashboard():
    """Página do painel do utilizador"""
    user = session.get('user')
    if not user:
        return jsonify({"error": "Utilizador não autenticado."}), 401
    return jsonify({
        "message": "Bem-vindo ao painel!",
        "user": user
    }), 200

@app.route('/logout')
def logout():
    """Encerra a sessão do utilizador."""
    session.pop('user', None)
    return redirect(url_for('login'))
    
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")
        role = data.get("role", "user")  # Define a função, padrão como "user"
        
        if not all([username, password, email]):
            return jsonify({"error": "Todos os campos são obrigatórios."}), 400

        password_hash = generate_password_hash(password)
        connection = get_mysql_connection()
        cursor = connection.cursor()

        # Verificar duplicidade de username
        cursor.execute("SELECT id FROM logins WHERE username = %s", (username,))
        result = cursor.fetchone()
        print(f"Verificando username: {username}, resultado: {result}") 
        if result is not None:
            return jsonify({"error": "Username já está registrado."}), 400

        # Verificar duplicidade de email
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        print(f"Verificando email: {email}, resultado: {result}")  
        if result is not None:
            return jsonify({"error": "Email já está registrado."}), 400
            
        # Registrar informações no banco
        cursor.execute("INSERT INTO users (email) VALUES (%s)", (email,))
        user_id = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO logins (username, password_hash, user_id, role)
            VALUES (%s, %s, %s, %s)
        """, (username, password_hash, user_id, role))
        connection.commit()

        # Cria MFA para o utilizador e envia por e-mail
        mfa_code = f"{random.randint(100000, 999999)}"  # Gera um código MFA de 6 dígitos
        cursor.execute("UPDATE logins SET mfa_code = %s WHERE username = %s", (mfa_code, username))
        connection.commit()

        # Enviar o MFA para o e-mail do utilizador
        msg = Message(
            subject="O seu código de autenticação MFA",
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )
        msg.body = f"O eu código de autenticação é: {mfa_code}"
        mail.send(msg)

        return jsonify({"message": f"Utilizador registrado com sucesso como {role}!"}), 201
    except Exception as e:
        return jsonify({"error": f"Erro ao registrar utilizador: {str(e)}"}), 500
    finally:
        cursor.close()
        connection.close()
   

# Classe para listar livros
class Books(Resource):
    def get(self):
        try:
            connection = get_mysql_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT id, titulo, autor FROM livros")
            books = cursor.fetchall()
            return books if books else {"message": "Nenhum livro encontrado."}, 200
        except Exception as e:
            return {"error": f"Erro ao procurar livros: {e}"}, 500
        finally:
            cursor.close()
            connection.close()
    def post(self):
        try:
            data = request.get_json()
            titulo = data.get("titulo")
            autor = data.get("autor")

            if not titulo or not autor:
                return {"error": "Título e autor são obrigatórios."}, 400

            connection = get_mysql_connection()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO livros (titulo, autor) VALUES (%s, %s)", (titulo, autor))
            connection.commit()

            return {"message": "Livro adicionado com sucesso!"}, 201
        except Exception as e:
            return {"error": f"Erro ao adicionar livro: {e}"}, 500
        finally:
            cursor.close()
            connection.close()

# Classe para registrar empréstimos
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

            cursor.execute("""
                SELECT id FROM emprestimos 
                WHERE id_livro = %s AND data_devolucao IS NULL
            """, (book_id,))
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
            return {"error": f"Erro ao registrar empréstimo: {e}"}, 500
        finally:
            cursor.close()
            connection.close()

# Classe para listar empréstimos
class Loans(Resource):
    def get(self):
        try:
            connection = get_mysql_connection()
            cursor = connection.cursor()
            cursor.execute("""
                SELECT emprestimos.id AS emprestimo_id, 
                       emprestimos.data_emprestimo, 
                       emprestimos.data_devolucao,
                       users.nome AS utilizador, 
                       livros.titulo AS livro
                FROM emprestimos
                JOIN users ON emprestimos.id_users = users.id
                JOIN livros ON emprestimos.id_livro = livros.id
            """)
            loans = cursor.fetchall()

            for loan in loans:
                if isinstance(loan["data_emprestimo"], (datetime, date)):
                    loan["data_emprestimo"] = loan["data_emprestimo"].strftime("%Y-%m-%d %H:%M:%S")
                if loan["data_devolucao"] and isinstance(loan["data_devolucao"], (datetime, date)):
                    loan["data_devolucao"] = loan["data_devolucao"].strftime("%Y-%m-%d")

            return loans, 200
        except Exception as e:
            return {"error": f"Erro ao procurar empréstimos: {e}"}, 500
        finally:
            cursor.close()
            connection.close()

# Classe para registrar devoluções
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
                return {"error": "Nenhum empréstimo ativo encontrado para este utilizador e livro."}, 404

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
            return {"error": f"Erro ao registrar devolução: {e}"}, 500
        finally:
            cursor.close()
            connection.close()

# Classe para listar e registrar utilizadores e logins
class Users(Resource):
    def get(self):
        try:
            connection = get_mysql_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT id, nome, email FROM users")
            users = cursor.fetchall()
            return users if users else {"message": "Nenhum utilizador encontrado."}, 200
        except Exception as e:
            return {"error": f"Erro ao procurar utilizadores: {e}"}, 500
        finally:
            cursor.close()
            connection.close()

    def post(self):
        try:
            connection = get_mysql_connection()
            cursor = connection.cursor()

            data = request.get_json()
            nome = data.get("nome")
            email = data.get("email")
            username = data.get("username")
            password = data.get("password")

            if not all([nome, email, username, password]):
                return {"error": "Todos os campos são obrigatórios."}, 400

            # Verificar se o email já está registrado
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return {"error": "Email já está registrado."}, 400

            # Verificar se o username já está registrado
            cursor.execute("SELECT id FROM logins WHERE username = %s", (username,))
            if cursor.fetchone():
                return {"error": "Username já está registrado."}, 400

            # Criar hash da password
            password_hash = generate_password_hash(password)

            # Inserir informações na tabela `users`
            cursor.execute("INSERT INTO users (nome, email) VALUES (%s, %s)", (nome, email))
            user_id = cursor.lastrowid

            # Inserir informações na tabela `logins`
            cursor.execute("INSERT INTO logins (username, password_hash, user_id) VALUES (%s, %s, %s)",
                           (username, password_hash, user_id))
            connection.commit()

            return {"message": "Utilizador e login registrados com sucesso!"}, 201
        except Exception as e:
            return {"error": f"Erro ao registrar utilizador e login: {e}"}, 500
        finally:
            cursor.close()
            connection.close()
    def delete(self):
        try:
            data = request.get_json()
            user_id = data.get("id")

            if not user_id:
                return {"error": "ID do utilizador é obrigatório."}, 400

            connection = get_mysql_connection()
            cursor = connection.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            cursor.execute("DELETE FROM logins WHERE user_id = %s", (user_id,))
            connection.commit()

            return {"message": "Utilizador apagado com sucesso!"}, 200
        except Exception as e:
            return {"error": f"Erro ao apagar utilizador: {e}"}, 500
        finally:
            cursor.close()
            connection.close()

# Classe para pesquisar livros externos do Open Library
class ExternalBooks(Resource):
    def get(self):
        query = request.args.get('query')
        if not query:
            return {"error": "Query parameter is required."}, 400

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
            return jsonify(books)
        except requests.RequestException as e:
            return {"error": "Erro ao consultar API externa."}, 500

# Classe para recomendações
class Recommendations(Resource):
    def get(self):
        try:
            connection = get_mysql_connection()
            cursor = connection.cursor()

            user_id = request.args.get('user_id')
            cursor.execute("""
                SELECT livros.id, livros.titulo, COUNT(emprestimos.id) AS total_emprestimos
                FROM livros
                JOIN emprestimos ON livros.id = emprestimos.id_livro
                GROUP BY livros.id, livros.titulo
                ORDER BY total_emprestimos DESC
                LIMIT 5
            """)
            recommendations = cursor.fetchall()
            return {"user_id": user_id, "recommendations": recommendations}, 200
        except Exception as e:
            return {"error": f"Erro ao pesquisar recomendações: {e}"}, 500
        finally:
            cursor.close()
            connection.close()
            
@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    """
    Retorna recomendações de livros com base no histórico do utilizador.

    Query Params:
        user_id (int): ID do utilizador.

    Returns:
        json: Lista de recomendações.
    """
    try:
        user_id = request.args.get('user_id', type=int)

        if not user_id:
            return jsonify({"error": "O parâmetro 'user_id' é obrigatório."}), 400

        # Exemplo de dados históricos (substitua pela base de dados real)
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT emprestimos.id_users AS user_id, livros.id AS book_id, 
                   livros.titulo AS title, livros.genero AS genre
            FROM emprestimos
            JOIN livros ON emprestimos.id_livro = livros.id
        """)
        historical_data = cursor.fetchall()
        historical_df = pd.DataFrame(historical_data)

        # Gerar recomendações
        recommendations = generate_recommendations(user_id, historical_df)

        return jsonify({"user_id": user_id, "recommendations": recommendations}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar recomendações: {e}"}), 500
            
# Classe para obter relatórios            
class Reports(Resource):
    def get(self):
        try:
            # Obter relatórios de atividades do MongoDB
            logs = user_logs.find()
            reports = []

            for log in logs:
                reports.append({
                    "user_id": log.get("user_id"),
                    "action": log.get("action"),
                    "book_id": log.get("book_id"),
                    "timestamp": log.get("timestamp"),
                })

            if not reports:
                return {"message": "Nenhum relatório encontrado."}, 404

            return reports, 200
        except Exception as e:
            return {"error": f"Erro ao carregar relatórios: {e}"}, 500
    def delete(self):
        try:
            user_logs.delete_many({})  # Remove todos os logs
            return {"message": "Todos os registros de atividades foram apagados com sucesso."}, 200
        except Exception as e:
            return {"error": f"Erro ao limpar registros de atividades: {e}"}, 500

@app.route('/reports', methods=['GET'])
def get_reports():
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor()

        # Consultar informações de empréstimos e devoluções
        cursor.execute("""
            SELECT 
                emprestimos.id AS emprestimo_id,
                emprestimos.data_emprestimo,
                emprestimos.data_devolucao,
                users.nome AS utilizador,
                livros.titulo AS livro
            FROM emprestimos
            JOIN users ON emprestimos.id_users = users.id
            JOIN livros ON emprestimos.id_livro = livros.id
            ORDER BY emprestimos.data_emprestimo DESC
        """)
        mysql_reports = cursor.fetchall()

        formatted_mysql_reports = [
            {
                "emprestimo_id": report["emprestimo_id"],
                "data_emprestimo": report["data_emprestimo"].strftime("%Y-%m-%d %H:%M:%S") if report["data_emprestimo"] else None,
                "data_devolucao": report["data_devolucao"].strftime("%Y-%m-%d %H:%M:%S") if report["data_devolucao"] else "Não devolvido",
                "utilizador": report["utilizador"],
                "livro": report["livro"]
            }
            for report in mysql_reports
        ]

        # Consultar informações do MongoDB
        logs = user_logs.find()
        mongo_reports = [
            {
                "user_id": log.get("user_id"),
                "action": log.get("action"),
                "book_id": log.get("book_id"),
                "timestamp": log.get("timestamp"),
            }
            for log in logs
        ]

        # Combinar as duas fontes de dados
        combined_reports = {
            "mysql_reports": formatted_mysql_reports,
            "mongo_reports": mongo_reports
        }

        return jsonify(combined_reports), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao carregar relatórios: {e}"}), 500
    finally:
        cursor.close()
        connection.close()

# Classe para sincronização de dados
class Sync(Resource):
    def post(self):
        try:
            connection = get_mysql_connection()
            cursor = connection.cursor()

            request_data = request.get_json()
            data_type = request_data.get("type")
            data_list = request_data.get("data", [])

            if data_type not in ["books", "users"]:
                return {"error": "Tipo de dados inválido. Use 'books' ou 'users'."}, 400

            if data_type == "books":
                for book in data_list:
                    if "id" not in book or "titulo" not in book or "autor" not in book:
                        return {"error": "Dados de livro inválidos."}, 400
                    cursor.execute("""
                        INSERT INTO livros (id, titulo, autor)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        titulo = VALUES(titulo), autor = VALUES(autor)
                    """, (book["id"], book["titulo"], book["autor"]))
            elif data_type == "users":
                for user in data_list:
                    if "id" not in user or "nome" not in user or "email" not in user:
                        return {"error": "Dados de utilizador inválidos."}, 400
                    cursor.execute("""
                        INSERT INTO users (id, nome, email)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        nome = VALUES(nome), email = VALUES(email)
                    """, (user["id"], user["nome"], user["email"]))

            connection.commit()

            user_logs.insert_one({
                "action": "sync",
                "type": data_type,
                "data_count": len(data_list),
                "timestamp": datetime.now().isoformat()
            })

            return {"message": f"Sincronização de {data_type} concluída com sucesso."}, 200
        except Exception as e:
            return {"error": f"Erro ao sincronizar dados: {e}"}, 500
        finally:
            cursor.close()
            connection.close()
            

# Classe para Login de Utilizadores
class Login(Resource):
    def post(self):
        try:
            connection = get_mysql_connection()
            cursor = connection.cursor()

            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return {"error": "Username e password são obrigatórios."}, 400

            # selecionar login na base de dados
            cursor.execute("SELECT id, password_hash FROM logins WHERE username = %s", (username,))
            user = cursor.fetchone()

            if not user or not check_password_hash(user["password_hash"], password):
                return {"error": "Login ou password inválidos."}, 401

            # Criar um token simples
            token = f"TOKEN-{user['id']}-{datetime.now().timestamp()}"

            return {"message": "Login realizado com sucesso.", "token": token}, 200
        except Exception as e:
            return {"error": f"Erro ao realizar login: {e}"}, 500
        finally:
            cursor.close()
            connection.close()

# Registrar os recursos (endpoints)
api.add_resource(Books, '/books')
api.add_resource(Borrow, '/borrow')
api.add_resource(Return, '/return')
api.add_resource(Loans, '/loans')
api.add_resource(Users, '/users')
api.add_resource(ExternalBooks, '/external-books')
api.add_resource(Recommendations, '/recommendations')
api.add_resource(Reports, '/reports')
api.add_resource(Sync, '/sync')

if __name__ == "__main__":
    app.run(debug=True)
