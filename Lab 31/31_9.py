import threading
import random
import time
import queue


def spectator_generator(N, t, q):
    for i in range(N):
        arrival = random.uniform(0, t)
        q.put((arrival, i))


def turnstile(q, t1, results):
    while True:
        try:
            arrival, i = q.get_nowait()
        except:
            break

        process = random.randint(1, t1)
        finish = arrival + process

        results.append(finish)

        q.task_done()


def simulate(N, m, t, t1):

    q = queue.Queue()
    results = []

    spectator_generator(N, t, q)

    threads = []

    for i in range(m):
        th = threading.Thread(target=turnstile,
                              args=(q,t1,results))
        threads.append(th)
        th.start()

    for th in threads:
        th.join()

    success = 0

    for r in results:
        if r <= t:
            success += 1

    return success / N


N = 20
m = 2
t1 = 3

t = 10

while True:

    p = simulate(N,m,t,t1)

    if p >= 0.9:
        print(t)
        break

    t += 1