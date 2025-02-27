"""
Credit goes to https://github.com/bertie2 for this wrapper
"""

import multiprocessing
import threading
import time
import enlighten
import enum

class MessageType(enum.Enum):
    CREATE_BAR = 1
    UPDATE_BAR = 2
    CREATE_COUNTER = 3
    UPDATE_COUNTER = 4

class Message():
    def __init__(self, type, id, data):
        self.type = type
        self.id = id
        self.data = data

class Bar():
    # a wrapper for a specific enlighten status bar which can be sent to other processes
    def __init__(self, queue, id):
        self.queue = queue
        self.id = id
    
    def update(self, *objects, **fields):
        self.queue.put(Message(MessageType.UPDATE_BAR, self.id, {"objects": objects, "fields": fields}))

class Counter():
    # a wrapper for a specific enlighten counter which can be sent to other processes
    def __init__(self, queue, id):
        self.queue = queue
        self.id = id
    
    def update(self, incr=1, force=False, **fields):
        self.queue.put(Message(MessageType.UPDATE_COUNTER, self.id, {"incr": incr, "force": force, "fields": fields}))

class Client():
    # a full wrapper of an enlighten manager which can be sent to other processes,
    # and can create and update bars and counters
    def __init__(self, queue, client_idx):
        self.queue = queue
        self.client_idx = client_idx
        self.message_idx = 0
    
    def status_bar(self, *args, **kwargs):
        self.queue.put(Message(MessageType.CREATE_BAR, (self.client_idx, self.message_idx), {"args": args, "kwargs": kwargs}))
        bar = Bar(self.queue, (self.client_idx, self.message_idx))
        self.message_idx += 1
        return bar

    def counter(self, position=None, **kwargs):
        self.queue.put(Message(MessageType.CREATE_COUNTER, (self.client_idx, self.message_idx), {"position": position, "kwargs": kwargs}))
        counter = Counter(self.queue, (self.client_idx, self.message_idx))
        self.message_idx += 1
        return counter

class Server():
    def __init__(self):
        # no_resize=True because resizing doesnt work with multithreading let alone multiprocessing
        self.manager = enlighten.get_manager(no_resize=True)
        self.queue_manager = multiprocessing.Manager()
        self.queue = self.queue_manager.Queue()
        self.stopped = False
        self.thread = threading.Thread(target=self.run)
        self.bars: dict[tuple[int, int], enlighten.StatusBar] = {}
        self.counters: dict[tuple[int, int], enlighten.Counter] = {}
        self.client_idx = 1 # 0 is reserved for the server
        self.message_idx = 0
        self.thread.start()

    def run(self):
        while(not self.stopped):
            if(not self.queue.empty()):
                try:
                    message: Message = self.queue.get(timeout=0.1)
                    if(message.type == MessageType.UPDATE_BAR):
                        self.bars[message.id].update(*message.data["objects"], **message.data["fields"])
                    elif(message.type == MessageType.UPDATE_COUNTER):
                        self.counters[message.id].update(message.data["incr"], message.data["force"], **message.data["fields"])
                    elif(message.type == MessageType.CREATE_BAR):
                        id = message.id
                        data = message.data
                        self.bars[id] = self.manager.status_bar(*data["args"], **data["kwargs"])
                    elif(message.type == MessageType.CREATE_COUNTER):
                        id = message.id
                        data = message.data
                        self.counters[id] = self.manager.counter(data["position"], **data["kwargs"])
                except Exception as e:
                    print(e)

    def get_client(self):
        client = Client(self.queue, self.client_idx)
        self.client_idx += 1
        return client
    
    def status_bar(self, name, color, justify):
        id = (0, self.message_idx)
        self.message_idx += 1
        self.bars[id] = self.manager.status_bar(name, color=color, justify=justify)
        return Bar(self.queue, id)
    
    def counter(self, total, desc, unit, color):
        id = (0, self.message_idx)
        self.message_idx += 1
        self.counters[id] = self.manager.counter(total=total, desc=desc, unit=unit, color=color)
        return Counter(self.queue, id)
    
    def stop(self):
        self.stopped = True
        self.queue_manager.shutdown()
        self.manager.stop()

def _test_worker(args):
    todo, counter = args
    for i in range(todo):
        counter.update()
        time.sleep(0.1)

def _test_worker2(args):
    todo, client = args
    counter = client.counter(total=100, desc="Counter", unit="items", color="green")
    for i in range(todo):
        counter.update()
        time.sleep(0.1)

if __name__ == '__main__':
    # built in tests / examples
    server = Server()
    pool = multiprocessing.Pool(10)

    main_bar = server.status_bar("Main", "green", "center")
    main_counter = server.counter(1000, desc="Main Counter", unit="items", color="green")
    args = [(100, main_counter) for _ in range(10)]
    pool.map(_test_worker, args)

    # args = [(100, server.get_client()) for _ in range(10)]
    # pool.map(_test_worker2, args)

    pool.close()
    pool.join()
    server.stop()