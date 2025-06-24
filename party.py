# party.py
import socket
import pickle

HOST = 'localhost'
PORT = 9999

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    # Step 1: Receive shares
    data = pickle.loads(s.recv(4096))
    x = data['x']
    y = data['y']
    a = data['a']
    b = data['b']
    c = data['c']

    # Step 2: Compute masked differences
    d_i = x - a
    e_i = y - b
    s.sendall(pickle.dumps({'d': d_i, 'e': e_i}))

    # Step 3: Receive public d, e and share of d*e
    d_e = pickle.loads(s.recv(4096))
    d = d_e['d']
    e = d_e['e']
    de_share = d_e['de_share']

    # Step 4: Correct final share calculation (no rounding!)
    share = de_share + d * b + e * a + c
    s.sendall(pickle.dumps({'share': share}))
