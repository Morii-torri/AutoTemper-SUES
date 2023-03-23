import time

text_list = []
max_area = 10


def add_log(text):
    if text != '':
        text_add = '%s\t%s' % (time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())), str(text))
        # 设置syslog为文件名【SystemLog-YYYY.MM.DD】
        text_list.append(text_add)
        if len(text_list) % max_area == 0:
            print_log()
            print("xx")
            text_list.clear()
        return True


def print_log():
    syslog = 'SystemLog-' + time.strftime('%Y.%m.%d', time.localtime(time.time())) + '.txt'
    # 打开syslog，写入日志
    f = open(syslog, "a")
    for i in range(0, len(text_list), 1):
        print(text_list[i], file=f)
    f.close()


if __name__ == '__main__':
    Flag = True
    while Flag:
        Flag = add_log(input())
