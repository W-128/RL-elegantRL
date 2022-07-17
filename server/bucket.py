import queue


class Bucket:

    def __init__(self, expire_time):
        self.expire_time = expire_time
        # key=rtl value =queue 里面添加req
        self.rtl_req_dic = {}

    def add_request(self, request):
        rtl = request.get_rtl()
        if rtl not in self.rtl_req_dic:
            self.rtl_req_dic[rtl] = queue.Queue()
        self.rtl_req_dic[rtl].put(request)

    def get_q_size(self):
        qsize = 0
        for rtl in self.rtl_req_dic:
            qsize = qsize + self.rtl_req_dic[rtl].qsize()
        return qsize

    def get_a_request(self):
        return self.request_queue.get()

    def get_requests(self, req_num):
        if (req_num == 0):
            return []
        submit_request_list = []
        rtl_num = req_num / len(self.rtl_req_dic.keys())
        remain_count = 0
        for queue in self.rtl_req_dic.values():
            remove_count = 0
            while queue.qsize() != 0:
                if remove_count >= rtl_num:
                    break
                remove_count = remove_count + 1
                submit_request_list.append(queue.get())
            remain_count = remain_count + rtl_num - remove_count

        if remain_count != 0:
            for queue in self.rtl_req_dic.values():
                if remain_count <= 0:
                    break
                while queue.qsize() != 0:
                    if remain_count <= 0:
                        break
                    remain_count = remain_count - 1
                    submit_request_list.append(queue.get())
        return submit_request_list
