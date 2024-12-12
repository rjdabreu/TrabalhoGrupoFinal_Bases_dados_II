from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from db_config import get_mysql_connection

app = Flask(__name__)
CORS(app)
api = Api(app)

class Sync(Resource):
    def post(self):
        try:
            # Simular integração com sistema externo
            data = request.get_json()
            external_data = data.get('external_data', [])
            # Simular sincronização (substitua com lógica real)
            return {"message": "Dados sincronizados com sucesso!", "synchronized_data": external_data}, 200
        except Exception as e:
            return {"error": f"Erro ao sincronizar: {e}"}, 500

api.add_resource(Sync, '/sync')

if __name__ == "__main__":
    app.run(port=5003, debug=True)
