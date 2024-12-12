import pika

def publish_message(queue_name, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='', routing_key=queue_name, body=message)
    print(f"Mensagem enviada para a fila '{queue_name}': {message}")
    connection.close()

# Exemplo de uso:
publish_message('catalog_updates', 'Novo livro adicionado!')
