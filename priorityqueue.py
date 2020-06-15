
class PriorityQueue(object):
    def __init__(self):
        self.queue  = []

    def push(self, _):
        if len(self.queue) == 0:
            self.queue.append(_)
            return
        for i in range(len(self.queue)):
            if _[0] < self.queue[i][0]:
                self.queue.insert(i, _)
                return
            elif _[0] == self.queue[i][0] and _[1] < self.queue[i][1]:
                self.queue.insert(i, _)
                return
        self.queue.append(_)

    def pop(self):
        obj = self.queue[0]
        self.queue = self.queue[1:]
        return obj

    def get(self):
        return self.queue[0]

if __name__ == "__main__":
    pq = PriorityQueue()
    pq.push((3, 2))
    pq.push((1, 2))
    pq.push((2, 1))
    pq.push((1, 1))
    pq.push((5, 1))
    print(pq.pop())
    print(pq.pop())
    print(pq.pop())
    print(pq.pop())
    print(pq.pop())