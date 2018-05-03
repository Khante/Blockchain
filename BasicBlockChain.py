import time
import sys
import threading
import os
import zmq
import os
import random
import json
import hashlib

def heartbeat():
    global socketBindArray
    global socketSendArray
    global identity
    while True:
        for i in range(len(socketSendArray)):
                    if (i+1)!=int(identity):
                        socketSendArray[i].send_json("heartbeat")
        time.sleep(1)

def client():
    global block_chain
    global socketBindArray
    global socketSendArray
    global block_number
    global identity
    while True:
        message = [0,0,0,0,0]
        for i in range(len(socketBindArray)):
            if (i+1)!=int(identity):
                message[i] = socketBindArray[i].recv_json()
                #print(message[i])
        if (message[4] != 'heartbeat') and (message[4] != 0):
            if(message[4]['block_number']!='bs_block'):
                #print("j is" + str(j))
                block_chain.append(message[4]) #might create problems with big message sizes
                print("added")
                print(block_chain[-1])


def server_master():
    global block_chain
    global socketBindArray
    global socketSendArray
    global block_counter
    global identity
    while True:
        message = [0,0,0,0,0]
        for i in range(len(socketBindArray)):
            if (i+1)!=int(identity):
                message[i] = socketBindArray[i].recv_json()
                #print(message[i])
        #print(message)
        correct_generators = []
        for j in range(len(message)):
            if (message[j] != 'heartbeat') and (message[j] != 0):
                if(message[j]['block_number']!='bs_block'):
                    correct_generators.append(message[j])
        for k in range(len(correct_generators)):
            if correct_generators[k]['identity'] == 1:
                correct_generators[0]['a_balance'] *= 1.1
            elif correct_generators[k]['identity'] == 1:
                correct_generators[0]['b_balance'] *= 1.1
            elif correct_generators[k]['identity'] == 1:
                correct_generators[0]['c_balance'] *= 1.1
            elif correct_generators[k]['identity'] == 1:
                correct_generators[0]['d_balance'] *= 1.1 #assigns rewards and benifits
        if(len(correct_generators)>=1):
            for i in range(len(socketSendArray)):
                if (i+1)!=int(identity):
                    socketSendArray[i].send_json(correct_generators[0])
        #message = [0,0,0,0,0]

def server():
    global block_chain
    global socketBindArray
    global socketSendArray
    global block_counter
    global identity
    while True:
        time.sleep(10) #change this for everyone
        p = random.randint(1,100)
        print("p is "+ str(p))
        if(p>25):
            generated_block = {'block_number':'bs_block', 'prev_hash':0, 'current_hash':0,\
         'a_balance':0,  'b_balance':0,    'c_balance':0,'d_balance':0}
        else:
            #block_counter += 1
            x = random.randint(1,2)
            #print("x is " + str(x))
            xx = random.randint(1,2)
            #print("xx is " + str(xx))
            stake = random.randint(10,15)
            #might want to send identity to help figure out which blocks stake to be considered in case of tally
            hash_string = str(block_chain[-1]['current_hash']) + str(block_chain[-1]['a_balance']-x) + str(block_chain[-1]['b_balance']+x) + \
            str(block_chain[-1]['c_balance']-xx) + str(block_chain[-1]['d_balance']+xx)
            generated_block = {'block_number':(block_chain[-1]['block_number']+1), 'prev_hash':block_chain[-1]['current_hash'], 'current_hash':hashlib.md5(hash_string.encode()).hexdigest(),\
            'a_balance':(block_chain[-1]['a_balance']-x),\
            'b_balance':(block_chain[-1]['b_balance']+x), \
            'c_balance':(block_chain[-1]['c_balance']-xx) ,'d_balance':(block_chain[-1]['d_balance']+xx), 'stake':stake, 'identity':identity}
            print("generated block below")
            print(generated_block)
            print("\n")
        for i in range(len(socketSendArray)):
            if (i+1)!=int(identity):
                socketSendArray[i].send_json(generated_block) #you have just sent the block. You need to get confirmation from the master node
        #block_chain.append(generated_block)

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
    ipAddresses = ['10.142.0.2','10.142.0.3','10.142.0.4','10.142.0.5', '10.142.0.6'] #u only have 4

    contextBindOne, contextBindTwo, contextBindThree, contextBindFour, contextBindFive = zmq.Context(), zmq.Context() , zmq.Context() , zmq.Context(), zmq.Context()
    socketBindOne, socketBindTwo, socketBindThree, socketBindFour, socketBindFive= contextBindOne.socket(zmq.PAIR), contextBindTwo.socket(zmq.PAIR), contextBindThree.socket(zmq.PAIR), contextBindFour.socket(zmq.PAIR), contextBindFive.socket(zmq.PAIR)
    global socketBindArray
    socketBindArray = [socketBindOne, socketBindTwo, socketBindThree, socketBindFour, socketBindFive]
    for i in range(len(socketBindArray)):
        if (i+1)!=int(identity):
            #print(int(port)+i+1)
            socketBindArray[i].bind("tcp://*:%s" % str(int(port)+i+1))
    contextSendOne, contextSendTwo, contextSendThree, contextSendFour, contextSendFive= zmq.Context(), zmq.Context() , zmq.Context() , zmq.Context(), zmq.Context()
    socketSendOne, socketSendTwo, socketSendThree, socketSendFour, socketSendFive = contextSendOne.socket(zmq.PAIR), contextSendTwo.socket(zmq.PAIR), contextSendThree.socket(zmq.PAIR), contextSendFour.socket(zmq.PAIR), contextSendFive.socket(zmq.PAIR)
    global socketSendArray
    socketSendArray = [socketSendOne, socketSendTwo, socketSendThree, socketSendFour, socketSendFive]
    for i in range(len(socketSendArray)):
        if (i+1)!=int(identity):
            #print(int(port)+i+1)
            socketSendArray[i].connect("tcp://" + ipAddresses[i]+ ":%s" % str(int(port)+int(identity)))
    time.sleep(4)

    client_thread = threading.Thread(target=client)
    server_thread = threading.Thread(target=server)
    heartbeat_thread = threading.Thread(target=heartbeat)
    server_master_thread = threading.Thread(target=server_master)
    heartbeat_thread.start()
    if(sys.argv[2] != 'm'):
        client_thread.start()
        server_thread.start()
    else:
        server_master_thread.start()