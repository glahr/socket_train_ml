from TCPConnection import TCPConnection
import time
import pickle

role = 'server'

if role == 'server':
    server_connection = TCPConnection('', 5022, True)
    server_connection.wait_client()
    for t in range(8):
        print('server sleeping for', t+1)
        time.sleep(1)
    print('sleeping done!')

    server_connection.send_memory_update(pickle.dump({'a': 1, 'b': 20, 'c': 33, 33: '55'}))

    memory = server_connection.recv_model_update()

    print('memory received:',memory)

    print('All done!')



else:
    client_connection = TCPConnection('192.168.7.2', 5022)
    client_connection.connect_to_server()
    received = False

    while received == False:
        received = client_connection.try_recv_memory_update()
        time.sleep(1)

    print(received)

    message = 'boooooora negaaada!'
    message_sent = False
    while message_sent == False:
        message_sent = client_connection.try_send_model_update(message.encode())
        time.sleep(1)

    print('All done!')

