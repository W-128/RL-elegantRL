log_file_path = 'log/request.log'
log = open(log_file_path, mode='r').readlines()

print(log[0])