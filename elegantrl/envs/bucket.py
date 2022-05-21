import queue


class Bucket:

    def __init__(self, expire_time):
        self.expire_time = expire_time
        self.request_queue = queue.Queue()

    def add_request(self, request):
        self.request_queue.put(request)

    def get_q_size(self):
        return self.request_queue.qsize()

    def get_a_request(self):
        return self.request_queue.get()
