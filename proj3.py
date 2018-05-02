import time
import sys
import threading
import os
import zmq
import os
import random
import json

def heartbeat():
    global socketBindArray
    global socketSendArray
    global identity
    while True:
        for i in range(len(socketSendArray)):
                    if (i+1)!=int(identity):
                        socketSendArray[i].send_json("heartbeat")
        time.sleep(0.3)

def client():
    global block_chain
    global socketBindArray
    global socketSendArray
    global block_number
    global identity
    message = [0,0,0,0]
    while True:
        for i in range(len(socketBindArray)):
            if (i+1)!=int(identity):
                #print(int(port)+i+1)
                message[i] = socketBindArray[i].recv_json()
                #print(message[i])
                if message[i] != 'heartbeat':
                    #print("getting a block")
                    block_chain.append(message[i])
                    print("incoming block below ")
                    print(json.dumps(message[i])+ "\n" )
                    #print(block_chain)
                    #socketSendArray[int(message[i].split(':')[0])-1].send_json(str(identity)+":ack")

def server():
    global block_chain
    global socketBindArray
    global socketSendArray
    global block_counter
    global identity
    while True:
        time.sleep(int(sys.argv[2])) #change this for everyone
        #block_counter += 1
        x = random.randint(1,5)
        print("x is " + str(x))
        xx = random.randint(1,5)
        print("xx is " + str(xx))
        generated_block = {'block_number':(block_chain[-1]['block_number']+1), 'prev_hash':0, 'current_hash':0, 'a_balance':(block_chain[-1]['a_balance']-x), 'b_balance':(block_chain[-1]['b_balance']+x), \
        'c_balance':(block_chain[-1]['c_balance']-xx) ,'d_balance':(block_chain[-1]['d_balance']+xx)}
        print("generated block below")
        print(generated_block)
        print("\n")
        for i in range(len(socketSendArray)):
            if (i+1)!=int(identity):
                socketSendArray[i].send_json(generated_block)
        block_chain.append(generated_block)

if __name__ == "__main__":
    global identity
    global block_chain
    block_chain = []
    global block_counter
    block_counter = 1
    identity = int(sys.argv[1]) #identity = 1, 2, 3, 4
    init_block = {'block_number':block_counter, 'prev_hash':0, 'current_hash':0, 'a_balance':100, 'b_balance':100, 'c_balance':100,\
    'd_balance':100}
    block_chain.append(init_block)
    port = "6000"
    ipAddresses = ['10.142.0.2','10.142.0.3','10.142.0.4','10.142.0.5'] #u only have 4

    contextBindOne, contextBindTwo, contextBindThree, contextBindFour = zmq.Context(), zmq.Context() , zmq.Context() , zmq.Context()
    socketBindOne, socketBindTwo, socketBindThree, socketBindFour= contextBindOne.socket(zmq.PAIR), contextBindTwo.socket(zmq.PAIR), contextBindThree.socket(zmq.PAIR), contextBindFour.socket(zmq.PAIR)
    global socketBindArray
    socketBindArray = [socketBindOne, socketBindTwo, socketBindThree, socketBindFour]
    for i in range(len(socketBindArray)):
        if (i+1)!=int(identity):
            print(int(port)+i+1)
            socketBindArray[i].bind("tcp://*:%s" % str(int(port)+i+1))
    contextSendOne, contextSendTwo, contextSendThree, contextSendFour= zmq.Context(), zmq.Context() , zmq.Context() , zmq.Context()
    socketSendOne, socketSendTwo, socketSendThree, socketSendFour = contextSendOne.socket(zmq.PAIR), contextSendTwo.socket(zmq.PAIR), contextSendThree.socket(zmq.PAIR), contextSendFour.socket(zmq.PAIR)
    global socketSendArray
    socketSendArray = [socketSendOne, socketSendTwo, socketSendThree, socketSendFour]
    for i in range(len(socketSendArray)):
        if (i+1)!=int(identity):
            #print(int(port)+i+1)
            socketSendArray[i].connect("tcp://" + ipAddresses[i]+ ":%s" % str(int(port)+int(identity)))

    client_thread = threading.Thread(target=client)
    server_thread = threading.Thread(target=server)
    heartbeat_thread = threading.Thread(target=heartbeat)
    client_thread.start()
    server_thread.start()
    heartbeat_thread.start()