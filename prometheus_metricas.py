from flask import Flask
from flask_restful import Api
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
api = Api(app)
metrics = PrometheusMetrics(app)  # Adiciona o monitorização do Prometheus

# Continuar com as configurações e endpoints do app...

if __name__ == "__main__":
    app.run(debug=True)
