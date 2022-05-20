import multiprocessing
import os

if not os.path.exists('log'):
    os.mkdir('log')

debug = True
loglevel = 'debug'
bind = '127.0.0.1:5000'
pidfile = 'log/gunicorn.pid'
logfile = 'log/debug.log'
errorlog = 'log/error.log'
accesslog = 'log/access.log'
daemon = 'false'
# 启动的进程数
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
threads = 2
x_forwarded_for_header = 'X-FORWARDED-FOR'
# 设置最大并发量
worker_connections = 2000
# 设置日志记录水平
loglevel = 'warning'