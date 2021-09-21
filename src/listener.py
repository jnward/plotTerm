import pika
from datetime import datetime, timedelta
from plotter import Plotter


def main():
	plot = Plotter(160, 20, debug=True)

	def callback(body):
		print('Plotting', body.decode())
		plot.print_string(body.decode())

	connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
	channel = connection.channel()

	channel.queue_declare(queue='plotter')
	channel.queue_purge(queue='plotter')

	print('Listener started, waiting for messages...')
	last_message = datetime.now()
	home = True
	while True:
		method_frame, header_frame, body = channel.basic_get('plotter')
		if method_frame is not None:
			channel.basic_ack(method_frame.delivery_tag)
			callback(body)
			last_message = datetime.now()
			home = False
		else:
			if datetime.now() - last_message > timedelta(seconds=2) and not home:
				print('Wait timeout, returning home')
				plot.show()
				home = True

if __name__ == '__main__':
	main()