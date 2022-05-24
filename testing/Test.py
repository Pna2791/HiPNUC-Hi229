
from queue import Queue

que = Queue()
for i in range(10):
    que.put(i)

print(que.get())
que.queue.clear()
que.put(10)
print(que.qsize())
print(que.get())
