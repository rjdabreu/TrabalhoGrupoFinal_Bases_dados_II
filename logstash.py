#direcione logs para um arquivo usando logging

import logging

logging.basicConfig(filename='app.log', level=logging.INFO)

@app.route('/books')
def get_books():
    logging.info('Endpoint /books acedido')
    # Lógica do endpoint
