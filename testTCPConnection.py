from TCPConnection import TCPConnection
import time
import pickle

role = 'server'
role = 'client'

print('I\'m a beautiful', role, '!')

if role == 'server':
    print('creating socket')
    server_connection = TCPConnection('', 20030, True)
    print('waiting client')
    server_connection.wait_client()
    for t in range(8):
        print('server sleeping for', t+1)
        time.sleep(1)
    print('sleeping done!')
    print('sending memory')
    server_connection.send_memory_update(pickle.dumps({'a': 1, 'b': 20, 'c': 33, 33: '55'}))
    print('receiving model')
    memory = server_connection.recv_model_update()

    print('memory received:', memory)

    print('All done!')



else:
    print('creating socket')
    client_connection = TCPConnection('192.168.7.2', 20030)
    print('connection to server')
    client_connection.connect_to_server()
    received = False

    print('try to receive memory')
    while received == False:
        received = client_connection.try_recv_memory_update()
        print(received, end='_|_')
        time.sleep(1)

    print('received', received)

    message = 'boooooora negaaada!'
    message_sent = False
    print('try to send model')
    while message_sent == False:
        message_sent = client_connection.try_send_model_update(message.encode())
        print(len(message_sent), end='_|_')
        time.sleep(1)

    print('All done!')

