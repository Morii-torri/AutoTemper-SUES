#!/usr/bin/python
# -*- coding: UTF-8 -*-
from aip import AipOcr
import time
import random
from selenium import webdriver
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import cv2
from selenium.webdriver import ActionChains
import base64
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from multiprocessing import Pool
from multiprocess import *

""" API """
APP_ID = '25284679'
API_KEY = 'tRx7UGHoI8sPm2fGVHrQc2cN'
SECRET_KEY = '3FLnEsBIHsvEuDf1xdbZAYxig5R8NKcO'

# 初始化AipFace对象
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

people = []
classnums = []
passages = []
receivers = []
hnums = []
dorms = []

# 从本地user_list文件获取账号密码
f = open('user_list.ini', mode='r', encoding='utf-8')  # 打开ini文件，以‘utf-8'编码读取
line = f.readline()  # 以行的形式进行读取文件
while line:
    a = line.split()
    b = a[0:len(line):5]  # 这是选取需要读取的位数
    c = a[1:len(line):5]
    d = a[2:len(line):5]
    e = a[3:len(line):5]
    g = a[4:len(line):5]
    classnums.extend(b)  # 将其添加在列表之中
    passages.extend(c)
    receivers.extend(d)
    hnums.extend(e)
    dorms.extend(g)
    line = f.readline()
f.close()
for i in range(0, len(classnums), 1):
    classnum = classnums[i]
    passage = passages[i]
    receiver = receivers[i]
    hnum = hnums[i]
    dorm = dorms[i]
    get_dict = {
        'classnum': classnum,
        'passage': passage,
        'receiver': receiver,
        'hnum': hnum,
        'dorm': dorm
    }
    people.append(get_dict)


# 读取图片
def get_file_content(path):
    with open(path, 'rb') as fp:
        return fp.read()


def img_to_str(image_path):
    image = get_file_content(image_path)

    """ 带参数调用通用文字识别 """
    result = client.basicAccurate(image)  # 通用文字识别（高精度）
    # result = client.numbers(image)  # 数字识别
    # result = client.basicGeneral(image)

    # 格式化输出-提取需要的部分
    if 'words_result' in result:
        text = ('\n'.join([w['words'] for w in result['words_result']]))
    return text


# 打印运行log
def print_log(text):
    print(text)
    syslog = 'SystemLog-' + time.strftime('%Y.%m.%d', time.localtime(time.time())) + '.txt'
    f = open(syslog, "a")
    text = '%s\t%s' % (time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())), str(text))
    print(text, file=f)
    f.close()


# 滑块移动距离
def distance(path1, path2):
    # 读入大验证码图
    image = cv2.imread(path1, 0)
    # 凸显缺口边缘  threshold1=100, threshold2=200为设定阈值
    image0 = cv2.Canny(image, threshold1=100, threshold2=200)
    # 读入小滑块（可移动）图片
    image1 = cv2.imread(path2)
    rows, cols, chanals = image1.shape
    # 裁剪小滑块（可移动）图片空白区域，大概是55*55像素
    min_x = 255
    min_y = 255
    max_x = 0
    max_y = 0
    for x in range(1, rows):
        for y in range(1, cols):
            t = set(image1[x, y])
            if len(t) >= 2:
                if x <= min_x:
                    min_x = x
                elif x >= max_x:
                    max_x = x
                if y <= min_y:
                    min_y = y
                elif y >= max_y:
                    max_y = y
    image2 = image1[min_x:max_x, min_y:max_y]
    # 同上
    can2 = cv2.Canny(image2, threshold1=100, threshold2=200)
    # 匹配缺口位置
    res = cv2.matchTemplate(image0, can2, cv2.TM_CCOEFF_NORMED)
    # 寻找最优匹配 min_val, max_val, min_loc, max_loc =0.09221141040325165 0.3617416322231293 (285, 77) (254, 146)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # max_loc为匹配最优的缺口左上角二维坐标  例如max_loc  = （254，146）
    ''' 用方框画出匹配位置
    th, tw = image1.shape[:2]
    tl = max_loc  # 左上角点的坐标
    br = (tl[0] + tw, tl[1] + th)  # 右下角点的坐标
    # cv2.rectangle(image, tl, br, (0, 255, 0), 2)
    # cv2.imwrite('TEMP1.jpg', image)
    '''
    x = max_loc[0]
    height, width, channels = image2.shape
    # print(width)
    if width == 55:
        Distance = round((x - 18) / 0.945)
    else:
        Distance = round((x - 6) / 0.945)
    return Distance


# 解码
def decode_base64(src, path):
    # 切割字符串，获取后面图片数据部分
    image_data = src.split(',')[1]
    # 解码-->二进制数据
    image = base64.b64decode(image_data)
    # 保持图片
    with open(path, 'wb') as f:
        f.write(image)


# 等待时间
def stop():
    time.sleep(round(random.uniform(1, 3)))


# 正常体温
def rands():
    tw = '{:.1f}'.format(random.uniform(35.4, 36.7))
    return tw


# 体温填写
def write_tem(get_dict):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    driver = webdriver.Chrome(options=options)
    # 进入网址
    login_url = "https://web-vpn.sues.edu.cn"
    driver.get(login_url)

    # 重复登录，直到登录成功
    path = ''
    bool_flag = True
    while bool_flag == True:
        try:
            # 填写用户名
            print_log(get_dict['classnum'] + "正在登入")
            driver.implicitly_wait(10)
            driver.find_element(By.ID, "username").clear()
            driver.find_element(By.ID, "username").send_keys(get_dict['classnum'])

            # 填写密码
            time.sleep(0.5)
            driver.find_element(By.ID, "password").clear()
            driver.find_element(By.ID, "password").send_keys(get_dict['passage'])
            # 设置存放验证码路径  './'表示保持为当前目录  get_dict['classnum'] 表示当前填写人学号
            path = './' + get_dict['classnum'] + '.png'  # 字符串拼接
            try:
                driver.find_element(By.XPATH, "//*[@id='fm1']/div[4]/img").screenshot(path)
                # 调用前面识别函数,得到验证码数字
                verify_word = img_to_str(path)
                # 填写进验证码
                driver.find_element(By.ID, "authcode").clear()
                time.sleep(1)
                driver.find_element(By.ID, "authcode").send_keys(verify_word)
            except:
                pass
            time.sleep(1)
            # 登录
            driver.find_element(By.CLASS_NAME, "login_btn").click()
            stop()
            driver.set_page_load_timeout(20)
            # 先寻找健康信息填报链接元素
            temporary_element = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div/div[3]/div/div[2]/div/div[1]/div/div[1]/div/div[1]/a/div[2]')
        except NoSuchElementException:
            # 没找到就意味者没有成功登录进去
            print_log(get_dict['classnum'] + "数字验证码识别错误------重新登录")
            # 若执行下面则继续执行while循环
            bool_flag = True
            continue  # 进行下一次while循环
        else:
            # 执行下面就停止while循环
            temporary_element.click()
            print_log(get_dict['classnum'] + "登录成功")
            bool_flag = False

    # 转到健康信息填报页面
    stop()
    windows = driver.window_handles
    driver.switch_to.window(windows[1])

    # # 点击体温一栏
    # driver.find_element(By.XPATH, "//div[@class='input-group']/input").click()
    #
    # # 清空填报信息，（可以省略）
    # driver.implicitly_wait(10)
    # driver.find_element(By.XPATH, "//div[@class='input-group']/input").clear()
    #
    # # 填写体温
    # time.sleep(0.5)
    # driver.find_element(By.XPATH, "//div[@class='input-group']/input").send_keys(rands())

    # 提交
    driver.set_page_load_timeout(20)
    try:
        driver.find_element(By.XPATH, "//*[@id='form']/div[10]/div/div/div[2]/div/div/label[2]").click()
        time.sleep(0.5)
        driver.find_element(By.XPATH, "//*[@id='form']/div[18]/div/div/div[2]/div/div/label[1]").click()
        time.sleep(0.5)
        # driver.find_element(By.XPATH, "//*[@id='ssl']/input").clear()
        # driver.find_element(By.XPATH, "//*[@id='ssl']/input").send_keys(get_dict['hnum'])
        # time.sleep(0.5)
        # driver.find_element(By.XPATH, "//*[@id='qs']/input").clear()
        # driver.find_element(By.XPATH, "//*[@id='qs']/input").send_keys(get_dict['dorm'])
        # time.sleep(0.5)
        # driver.find_element(By.XPATH, "//*[@id='form']/div[19]/div/div/div[2]/div/div/label[1]").click()
    except:
        print_log("定位错误")
        pass
    driver.find_element(By.ID, "post").click()
    time.sleep(2)
    bool_flag_1 = True
    j = 0
    path1 = ''
    path2 = ''
    while bool_flag_1 == True:
        # 多次重新尝试点击刷新
        try:
            driver.implicitly_wait(1)
            driver.find_element(By.XPATH, '//*[@id = "layui-layer100001"]/div /div/div/div[2]/div[3]/img').click()
            print_log(get_dict['classnum'] + "失败过多------点击重试")
            time.sleep(1)
        except:
            pass

        try:
            # 取滑块图片标签
            img1_label = driver.find_element(By.XPATH, "//*[@id='layui-layer100001']/div/div/div/div[1]/img[1]")
            time.sleep(1)
            img2_label = driver.find_element(By.XPATH, "//*[@id='layui-layer100001']/div/div/div/div[1]/img[2]")

            # 得到两个图片链接----在src中且为base64编码形式，这种形式可以直接解码为图片，网页中不占内存
            img1_url = img1_label.get_attribute("src")
            img2_url = img2_label.get_attribute("src")

            # path1 存放滑块验证码路径
            path1 = './' + get_dict['classnum'] + 'a' + '.jpg'
            path2 = './' + get_dict['classnum'] + 'b' + '.jpg'

            # 调用解码函数
            decode_base64(img1_url, path1)
            decode_base64(img2_url, path2)

            # 调用函数获取距离
            x = distance(path1, path2)
            # 获取滑块元素
            slide = driver.find_element(By.XPATH, "//div[@class='ap-bar-ctr']")
            # 下面方法是托slide元素到x距离后并松开  0代表高度，这里不用上下拖动，所以为0
            ActionChains(driver).drag_and_drop_by_offset(slide, x, 0).perform()
            time.sleep(1.5)
            temporary_element1 = driver.find_element(By.XPATH, "//*[@id='layui-layer100003']/div[3]/a")
        except NoSuchElementException:
            # 没找到就意味者没有成功验证
            print_log(get_dict['classnum'] + "滑块验证码识别错误------重新尝试")
            j = j + 1
            if j == 10:
                print_log(get_dict['classnum'] + "体温填写失败")
                bool_flag_1 = False
            else:
                # 若执行下面则继续执行while循环
                bool_flag_1 = True
                continue  # 进行下一次while循环
        else:
            # 执行下面就停止while循环
            temporary_element1.click()
            print_log(get_dict['classnum'] + "体温填报成功")
            bool_flag_1 = False

    # 关闭浏览器
    driver.quit()
    try:
        # 发送邮箱提示
        my_sender = '2038120042@qq.com'  # 发件人邮箱账号
        my_pass = 'jrejodegxbioefeb'  # 发件人邮箱密码
        if j == 10:
            message = '%s\t%s\n' % (
                time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time())), str('体温填报失败' + get_dict['classnum']))
        else:
            message = '%s\t%s\n' % (
                time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time())), str('体温填报成功' + get_dict['classnum']))
        my_user = get_dict['receiver']  # 接受人邮箱账号
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['From'] = formataddr(["Robot", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(["User", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "系统提示"  # 邮件的主题，也可以说是标题
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
        print_log(my_user + '邮件发送成功')
    except:
        print_log(my_user + '邮件发送失败')
    # 删除冗余文件
    try:
        os.remove(path)
        os.remove(path1)
        os.remove(path2)
    except:
        pass


if __name__ == '__main__':
    multiprocessing.freeze_support()
    # 下面参数processes可以修改，processes=2意思是2线程
    pool = Pool(processes=1)
    # 调用函数write_tem
    pool.map(write_tem, people)
    # 上面函数多线程结束后关闭并加入新线程，直到参数people跑完
    pool.close()
    pool.join()
