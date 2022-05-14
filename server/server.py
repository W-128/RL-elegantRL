import datetime
from flask import Flask
from buffer import Buffer
from buffer_fifo import BufferFIFO
import time
import csv
from threading import Thread
import threading
from request import Request

app = Flask(__name__)

env = None
with open('request_record.csv', 'w', newline='') as f:
    f_csv = csv.writer(f)
    f_csv.writerow(['arrive_time', 'request_id', 'rtl'])


def print_task_id(task_id, rtl):
    print(task_id)
    print(rtl)


def save_arrive_time_and_task_id_and_rtl_to_csv(task_id, rtl, arrive_time):
    with open('request_record.csv', 'a', newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerow([arrive_time, task_id, rtl])


@app.route('/complete_task/<task_id>/<rtl>')
def complete_task(task_id, rtl):
    event = threading.Event()
    now_time = datetime.datetime.now()
    req = Request(now_time.timestamp(), task_id, int(rtl), event)
    save_arrive_time_and_task_id_and_rtl_to_csv(task_id, rtl, now_time.strftime('%Y-%m-%d %H:%M:%S.%f'))
    BufferFIFO.get_instance().produce(req)
    event.wait()
    if req.is_success:
        return {
            "msg": "success",
            "data": {
                "task_id": task_id,
                "rtl": rtl,
            }
        }
    return '超时拒绝', 500


if __name__ == '__main__':
    app.run()
