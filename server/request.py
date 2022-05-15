import time

import datetime

import logging

# 创建logger对象
logger = logging.getLogger('test_logger')

# 设置日志等级
logger.setLevel(logging.DEBUG)

# 追加写入文件a ，设置utf-8编码防止中文写入乱码
test_log = logging.FileHandler('test.log', 'a', encoding='utf-8')

# 向文件输出的日志级别
test_log.setLevel(logging.DEBUG)

# 向文件输出的日志信息格式
formatter = logging.Formatter('%(asctime)s - %(filename)s - line:%(lineno)d - %(levelname)s - %(message)s')

test_log.setFormatter(formatter)

# 加载文件到logger对象中

logger.addHandler(test_log)


class Request:
    wait_time = 0

    def __init__(self, start_time, task_id, rtl, event) -> None:
        self.start_time = start_time
        self.task_id = task_id
        self.rtl = rtl
        self.event = event
        self.is_success = True

    def set_wait_time(self, wait_time):
        self.wait_time = wait_time

    def run(self):
        time.sleep(0.9)
        end_time = datetime.datetime.now().timestamp()
        delta_ms = int((end_time - self.start_time) * 1000)
        # logger.info("rtllevel:" + str(self.rtl) + " request response time: " + str(delta_ms) + "ms")
        logger.info("rtllevel:" + str(self.rtl) + " wait time: " + str(self.wait_time) + "ms")
