# inputfile 导入配置文件

import requests
from datetime import datetime

# 配置变量
retry_count = 3  # 设置重试次数
user_agent = "okhttp/3.15"  # 替换为你的用户代理字符串


# 下载文件的函数
# 返回: 下载的内容
def download_file(task_num, task_name, url, download_file_path):
    attempt = 1

    while attempt <= retry_count:
        try:
            headers = {'User-Agent': user_agent}
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # 检查请求是否成功

            # 直接将内容写入目标文件，覆盖原文件
            with open(download_file_path, 'wb') as file:
                file.write(response.content)

            print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - [任务 {task_num}] - [{task_name}]'
                  f' - 文件下载成功: {download_file_path}')

            # 将下载的内容返回，不需要再从文件读入，文件下载仅作保存使用
            return response.content.decode('UTF-8')

        except requests.exceptions.RequestException as e:
            print(
                f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - [任务 {task_num}] - [{task_name}]'
                f' - 文件下载失败 (第 {attempt} 次尝试)')
            attempt += 1

    # 重试下载失败，直接抛出异常
    if attempt > retry_count:
        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - [任务 {task_num}] - [{task_name}]'
              f' - 下载失败 (共重试 {retry_count} 次)')
        raise Exception


# 执行下载动作
# task_config: 配置文件 config
# 返回: 下载的内容
def process_download(task_config, task_num):
    return download_file(task_num, task_config['name'], task_config['url'], task_config['downloadFilePath'])


# 执行下载动作
# task_config: 配置文件 config
# 返回: 下载的内容
def process_input_file(task_config):
    input_file_path = task_config['inputFilePath']

    # 读取文件到变量中
    with open(input_file_path, 'r', encoding='utf-8') as infile:
        file_content = infile.read()

    return file_content
