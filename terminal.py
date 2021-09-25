from subprocess import run, PIPE
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='plotter')

def terminal():
    while True:
        cmd = input('$ ')
        ret = run(cmd, shell=True, capture_output=True)
        channel.basic_publish(exchange='', routing_key='plotter', body='$ ' + ret.args.lower() + '\n')
        message = ret.stdout.decode().lower() if ret.returncode == 0 else ret.stderr.decode().lower()
        for line in message.splitlines():
            print(line)
            channel.basic_publish(exchange='', routing_key='plotter', body=line + '\n')
        
if __name__ == '__main__':
    terminal()
