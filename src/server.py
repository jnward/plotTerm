import pika
from flask import Flask, request
# from plotter import Plotter

app = Flask(__name__)

# plot = Plotter(60, 20, debug=True)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='plotter')

@app.route('/print', methods=['POST'])
def recieve_message():
	message = request.json.get('message', '')
	channel.basic_publish(exchange='', routing_key='plotter', body=message.lower())
	# plot.print_string(message)
	return ('', 200)