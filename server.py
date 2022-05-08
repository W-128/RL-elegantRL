import datetime
from flask import Flask
import time
import csv

app = Flask(__name__)
with open('request_record.csv', 'w', newline='') as f:
    f_csv = csv.writer(f)
    f_csv.writerow(['arrive_time', 'task_id', 'rtl'])


def print_task_id(task_id, rtl):
    print(task_id)
    print(rtl)


def save_arrive_time_and_task_id_and_rtl_to_csv(task_id, rtl):
    arrive_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    with open('request_record.csv', 'a', newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerow([arrive_time, task_id, rtl])


@app.route('/complete_task/<task_id>/<rtl>')
def complete_task(task_id, rtl):
    save_arrive_time_and_task_id_and_rtl_to_csv(task_id, rtl)
    return {
        "msg": "success",
        "data": {
            "task_id": task_id,
            "rtl": rtl,
        }
    }


app.run()