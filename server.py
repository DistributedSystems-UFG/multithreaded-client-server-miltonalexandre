#!/usr/bin/env python3
import socket
import threading
import endpoints
import logging
import time
import random

# TODO: disparar uma thread para cada requisição recebida
# TODO: fazer um experimento para medir o desempenho para o envio, processamento e resposta de uma certa quantidade (suficientemente grande) de requisições.
# TODO: repetir o mesmo experimento com o par cliente-servidor single-threaded
# TODO: Comparar também com o desempenho da versão original, com multithreading apenas no servidor


class ThreadedServer:
    def __init__(self, host="localhost", port=5678, backlog=100):
        self.host = host
        self.port = port
        self.backlog = backlog

        self.server_socket = None
        self.running = False

        self.client_threads = []
        self.lock = threading.Lock()

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(threadName)s: %(message)s",
        )

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.backlog)
        self.server_socket.settimeout(1.0)

        self.running = True

        logging.info(f"Server listening on {self.host}:{self.port}")

        try:
            self.accept_loop()
        finally:
            self.stop()

    def stop(self):
        self.running = False

        if self.server_socket:
            try:
                self.server_socket.close()
            except OSError:
                pass

        logging.info("Waiting for client threads...")

        for t in self.client_threads:
            t.join(timeout=2)

        logging.info("Server stopped")

    def accept_loop(self):
        while self.running:
            try:
                client_sock, addr = self.server_socket.accept()  # type: ignore
            except socket.timeout:
                continue
            except OSError:
                break

            logging.info(f"Connection from {addr}")

            t = threading.Thread(
                target=self.client_wrapper, args=(client_sock, addr), daemon=True
            )
            t.start()

            with self.lock:
                self.client_threads.append(t)

    def client_wrapper(self, client_sock, addr):
        with client_sock:
            client_sock.settimeout(60)

            try:
                self.handle_client(client_sock, addr)
            except Exception as e:
                logging.exception(f"Client {addr} error: {e}")
            finally:
                logging.info(f"Disconnected {addr}")

    def handle_client(self, client_sock, addr):
        data = client_sock.recv(1024)  # receive data from client
        if not data:
            return  # stop if client stopped
        option = data.decode()
        client_sock.send("ready".encode())
        value = client_sock.recv(1024)
        if option == "1":
            precision = float(value.decode())
            start = time.time()
            pi_value = self.calc_pi(precision)
            end = time.time()
            elapsed_time = end - start
            msg = "PI: " + str(pi_value) + "\nElapsed time: " + str(elapsed_time)
        else:
            guess = int(value.decode())
            random_number = random.randint(1, 10)
            if guess == random_number:
                msg = "correct"
            else:
                msg = "wrong"

        time.sleep(0.5)
        client_sock.send(msg.encode())  # return sent data plus an "*"

    def calc_pi(self, precision):
        k = 1
        parcel = 4 / k
        s = 0
        i = 0
        while abs(parcel) > precision:
            s += parcel
            k += 2
            i += 1
            if i % 2 == 0:
                parcel = 4 / k
            else:
                parcel = -4 / k
        return s


if __name__ == "__main__":
    s = ThreadedServer(host=endpoints.HOST, port=endpoints.PORT)
    s.start()
