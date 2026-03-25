import threading
import queue
import random
import time

#31.3
def producer(q, t1):
    i = 1
    while True:
        time.sleep(random.randint(1, t1))
        msg = "Message " + str(i)
        q.put(msg)
        i += 1


def consumer(q, t2):
    while True:
        msg = q.get()
        time.sleep(random.randint(1, t2))
        print(msg)
        q.task_done()


t1 = 5
t2 = 4

q = queue.Queue()

p = threading.Thread(target=producer, args=(q,t1))
c = threading.Thread(target=consumer, args=(q,t2))

p.start()
c.start()

p.join()
c.join()

#31.4
import threading
import random
import time
from collections import deque


class MessageDeque(deque):

    def add_normal(self, msg):
        self.append(msg)

    def add_priority(self, msg):
        self.appendleft(msg)

    def get_message(self):
        if len(self) > 0:
            return self.popleft()


def producer(d, t1):
    i = 1
    while True:
        time.sleep(random.randint(1, t1))

        if random.randint(1,4) == 1:
            msg = "Priority " + str(i)
            d.add_priority(msg)
        else:
            msg = "Message " + str(i)
            d.add_normal(msg)

        i += 1


def consumer(d, t2):
    while True:
        if len(d) > 0:
            msg = d.get_message()
            time.sleep(random.randint(1, t2))
            print(msg)


t1 = 5
t2 = 4

d = MessageDeque()

p = threading.Thread(target=producer, args=(d,t1))
c = threading.Thread(target=consumer, args=(d,t2))

p.start()
c.start()

p.join()
c.join()