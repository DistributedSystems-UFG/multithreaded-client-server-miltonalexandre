import socket
import time
import random
import endpoints
import threading


def request(arg1, arg2):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect(
        (endpoints.HOST, endpoints.PORT)
    )  # connect to server (block until accepted)

    option = arg1
    if option != "1" and option != "2":
        print("invalid option")
        quit()

    s.send(option.encode())  # send some data
    data = s.recv(1024)
    if data.decode() != "ready":
        print("error")
        quit()

    if option == "1":
        precision = arg2
        s.send(precision.encode())
    else:
        value = arg2
        s.send(value.encode())

    data = s.recv(1024)
    print(data.decode())  # print the result
    s.close()  # close the connection


if __name__ == "__main__":
    client_threads = []

    start = time.time()
    for i in range(10):
        arg1 = random.randint(1, 2)
        if arg1 == 1:
            precision = random.randint(1, 6)
            arg2 = 10 ** (-precision)
        else:
            arg2 = random.randint(1, 10)
        arg1 = str(arg1)
        arg2 = str(arg2)
        t = threading.Thread(
            target=request,
            args=(
                arg1,
                arg2,
            ),
        )

        client_threads.append(t)
        t.start()

    for t in client_threads:
        t.join()

    end = time.time()
    print(f"time: {end - start}")
