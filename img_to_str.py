# -*- coding: UTF-8 -*-
from aip import AipOcr

""" API """
APP_ID = '25284679'
API_KEY = 'tRx7UGHoI8sPm2fGVHrQc2cN'
SECRET_KEY = '3FLnEsBIHsvEuDf1xdbZAYxig5R8NKcO'

# 初始化AipFace对象
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


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


if __name__ == '__main__':
    print(img_to_str('/path'))
