from subprocess import Popen, PIPE
from threading import Thread
from queue import Queue

def reader(pipe, queue):
    try:
        with pipe:
            for line in iter(pipe.readline, b''):
                queue.put((pipe, line))
    finally:
        queue.put(None)

process = Popen(["hackrf_sweep"], stdout=PIPE, stderr=PIPE, bufsize=1)
q = Queue()
Thread(target=reader, args=[process.stdout, q]).start()
Thread(target=reader, args=[process.stderr, q]).start()
for _ in range(2):
    for source, line in iter(q.get, None):
        print("%s: %s" % (source, line))