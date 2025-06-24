# coordinator.py
import socket
import threading
import random
import pickle

NUM_PARTIES = 3
HOST = 'localhost'
PORT = 9999
clients = []

def share_secret(secret):
    s1 = random.randint(0, 100)
    s2 = random.randint(0, 100)
    s3 = secret - s1 - s2
    return [s1, s2, s3]

def send_all(data):
    for client in clients:
        client.sendall(pickle.dumps(data))

def recv_all():
    return [pickle.loads(clients[i].recv(4096)) for i in range(NUM_PARTIES)]

def handle_client(conn, addr):
    print(f"[+] Party connected: {addr}")
    if len(clients) == NUM_PARTIES:
        run_mpc()

def run_mpc():
    x, y = 7, 3  # You can change these inputs
    print(f"\n🔐 Running MPC for x = {x}, y = {y}")

    x_shares = share_secret(x)
    y_shares = share_secret(y)

    a = random.randint(1, 10)
    b = random.randint(1, 10)
    c = a * b
    a_shares = share_secret(a)
    b_shares = share_secret(b)
    c_shares = share_secret(c)

    print(f"🔑 Beaver Triple: a = {a}, b = {b}, c = {c}\n")

    # Send shares to each party
    for i in range(NUM_PARTIES):
        clients[i].sendall(pickle.dumps({
            'x': x_shares[i],
            'y': y_shares[i],
            'a': a_shares[i],
            'b': b_shares[i],
            'c': c_shares[i]
        }))

    # Receive d_i, e_i
    responses = recv_all()
    d = sum(r['d'] for r in responses)
    e = sum(r['e'] for r in responses)
    print(f"🧾 Public d = {d}, e = {e}")

    # Send d, e back to each party
    send_all({'d': d, 'e': e})

    # Receive final result shares
    result_shares = recv_all()
    result = sum(r['share'] for r in result_shares)

    print(f"\n✅ Secure x × y = {result}")
    print(f"✅ Actual x × y = {x * y}\n")

# Start coordinator
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("🧠 Coordinator waiting for 3 parties...")

    while len(clients) < NUM_PARTIES:
        conn, addr = s.accept()
        clients.append(conn)
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

    while True:
        pass  # Keep server alive
