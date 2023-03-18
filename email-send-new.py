# !/usr/bin/python
# -*- coding: UTF-8 -*-
import cv2
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import time
from multiprocessing import Pool
import os
from multiprocess import *
# print(cv2.__file__)

people = []
classnums = []
passages = []
receivers = []

# 从本地user_list文件获取账号密码
f = open('email.txt', mode='r', encoding='utf-8')  # 打开txt文件，以‘utf-8'编码读取
line = f.readline()  # 以行的形式进行读取文件
while line:
    a = line.split()
    b = a[0:len(line):3]  # 这是选取需要读取的位数
    c = a[1:len(line):3]
    d = a[2:len(line):3]
    classnums.extend(b)  # 将其添加在列表之中
    passages.extend(c)
    receivers.extend(d)
    line = f.readline()
f.close()
for i in range(0, len(classnums), 1):
    classnum = classnums[i]
    passage = passages[i]
    receiver = receivers[i]
    get_dict = {
        'classnum': classnum,
        'passage': passage,
        'receiver': receiver
    }
    people.append(get_dict)


def email(get_dict):
    try:
        # 发送邮箱提示
        my_sender = '2038120042@qq.com'  # 发件人邮箱账号
        my_pass = 'jrejodegxbioefeb'  # 发件人邮箱密码
        message = '%s\t%s\n' % (time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time())), str("\n您好，"+get_dict['classnum']+"\n您的账号已成功录入系统，系统将自动运行，届时您会收到邮箱提示。\n感谢您的使用，祝您生活愉快。"))
        print(message)
        my_user = get_dict['receiver']  # 接受人邮箱账号
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['From'] = formataddr(["Robot", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(["User", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "系统提示"  # 邮件的主题，也可以说是标题
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
        print(my_user + '邮件发送成功')
    except:
        print(my_user + '邮件发送失败')


if __name__ == '__main__':
    multiprocessing.freeze_support()
    # 下面参数processes可以修改，processes=2意思是2线程
    pool = Pool(processes=1)
    # 调用函数write_tem
    pool.map(email, people)
    # 上面函数多线程结束后关闭并加入新线程，直到参数people跑完
    pool.close()
    pool.join()