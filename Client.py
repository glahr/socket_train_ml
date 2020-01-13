import socket
import pickle

def create_network():
    import keras
    from keras.models import Sequential
    from keras.layers import Dense, LSTM
    # from keras.optimizers import Adam
    import keras.backend as K
    from keras.optimizers import Adadelta
    import tensorflow as tf
    # from collections import deque
    # import numpy as np

    config = K.tf.ConfigProto()
    config.gpu_options.allow_growth = True
    session = K.tf.Session(config=config)

    model = Sequential()
    model.add(LSTM(20, input_shape = (1, 12), return_sequences = True))
    model.add(LSTM(15))
    model.add(Dense(4, activation = "relu"))
    LEARNING_RATE = 0.001
    adadelta = Adadelta(lr=LEARNING_RATE, rho=0.95, epsilon=1e-6, decay=0.95)
    model.compile(loss="mse", optimizer=adadelta)

    weights = pickle.dumps(model.get_weights())

    return weights


msgFromClient = create_network()

# msgFromClient = "Hello UDP Server"
# bytesToSend = str.encode(msgFromClient)
bytesToSend = msgFromClient

print(len(bytesToSend))

serverAddressPort = ("192.168.10.15", 5000)

# bufferSize = 20000

# Create a UDP socket at client side
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

tcp.connect(serverAddressPort)

# Send to server using created UDP socket
print("conectei")
length_msg = str(len(bytesToSend))
tcp.send(str.encode(length_msg))

print("esperando receber")
msgFromServer = tcp.recv(1024)
print(msgFromServer)

print("enviando weights")
tcp.send(bytesToSend)
msgFromServer = tcp.recv(1024)

msg = "Message from Server {}".format(msgFromServer)

print(msg)
