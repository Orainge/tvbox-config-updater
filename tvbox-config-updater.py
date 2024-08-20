#!/usr/bin/python3

import json
import sys
import os
from datetime import datetime

from pipe import append, clean, inputfile, filter, order, replace


# 根据任务配置，处理 tvbox 配置文件
def process(tvbox_config_json, task_config):
    # 1.filter
    if 'filter' in task_config:
        filter.process_filter(tvbox_config_json, task_config['filter'])

    # 2.replace
    if 'replace' in task_config:
        replace.process_replace(tvbox_config_json, task_config['replace'])

    # 3.append
    if 'append' in task_config:
        append.process_append(tvbox_config_json, task_config['append'])

    # 4.order
    if 'order' in task_config:
        order.process_order(tvbox_config_json, task_config['order'])


# 将 tvbox 配置 json 保存到文件中
def save_tvbox_config_json_to_file(tvbox_config_json, task_config, task_num, is_merge_config=False):
    output_file_path = task_config['outputFilePath']

    # 1. 删除输出文件（如果存在的话）
    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    # 2. 检查是否开启 JSON 格式化输出
    indent = None
    if 'jsonFormatting' in task_config and task_config['jsonFormatting'] is True:
        indent = 4

    # 3. 将过滤后的结果写入输出的JSON文件
    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        json.dump(tvbox_config_json, outfile, ensure_ascii=False, indent=indent)

    # 输出日志
    if is_merge_config:
        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - [任务 {task_num}]'
              f' - 聚合配置文件输出成功: {output_file_path}')
    else:
        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - [任务 {task_num}] - [{task_config["name"]}]'
              f' - 配置文件替换完成: {output_file_path}')


# 执行单个配置文件的任务
def execute(config_json_path, task_num):
    task_num += 1

    # 读取配置文件
    try:
        with open(config_json_path, 'r', encoding='utf-8') as input_config_json:
            config_json = json.load(input_config_json)

    except Exception as e:
        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - [任务 {task_num}] - 读取配置文件错误，请检查')
        raise e

    # 聚合输出参数准备
    # 聚合输出时，临时存放各个 tvbox 配置 json 的 list
    tvbox_config_json_list = None
    enable_merge = False
    merge_config = None
    if 'mergeConfig' in config_json and config_json['mergeConfig']['enable'] is True:
        tvbox_config_json_list = []
        enable_merge = True
        merge_config = config_json['mergeConfig']

    # 遍历任务配置
    task_config_json = config_json['taskConfig']
    for task_config in task_config_json:
        task_name = '未知任务'
        try:
            # 任务名称
            task_name = task_config['name']

            # 1. 选择下载文件还是输入文件
            if "inputFilePath" in task_config:
                # 输入文件
                tvbox_config_content = inputfile.process_input_file(task_config)
            elif 'url' in task_config and 'downloadFilePath' in task_config:
                # 下载文件，将内容保存到文件，并得到文件内容
                tvbox_config_content = inputfile.process_download(task_config, task_num)
            else:
                print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - [任务 {task_num}] - '
                      f'[{task_name}] - 任务执行异常：请输入 inputFilePath 或 url+downloadFilePath')
                continue

            # 2. 清洗文件，得到 json dict 对象
            tvbox_config_json = clean.process_clean(tvbox_config_content, task_config)

            # 3. 处理配置文件
            process(tvbox_config_json, task_config)

            # 4. 输出到文件
            save_tvbox_config_json_to_file(tvbox_config_json, task_config, task_num)

            # 5. 如果需要聚合输出，则将 tvbox 的配置文件放入临时 list
            if enable_merge:
                tvbox_config_json_list.append(tvbox_config_json)
        except Exception as e:
            print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - [任务 {task_num}] - [{task_name}] - 任务执行异常')
            raise e

    # 聚合输出
    if enable_merge:
        # 配置项
        # 取第一个有值的 key
        get_first_value_keys = ['wallpaper', 'logo']
        # 需要追加合并的 key
        append_value_keys = ['sites', 'parses', 'lives']

        # 1. 根据合并规则进行处理
        merge_tvbox_config_json = {
            'spider': '',  # 1.1 spider 置为空字符串
        }

        # 配置追加数组
        for key in append_value_keys:
            merge_tvbox_config_json[key] = []

        # 用于判断是否取值完成
        get_first_value_keys_tag = {}

        # 遍历每个 tvbox_config_json
        for tvbox_config_json in tvbox_config_json_list:
            # 1.2 追加数据到合并项中
            for key in append_value_keys:
                if key in tvbox_config_json:
                    merge_tvbox_config_json[key].extend(tvbox_config_json[key])

            # 1.3 向每个项目追加项 jar, 值为 各自的 spider 的值（如有）
            if ('spider' in tvbox_config_json
                    and tvbox_config_json['spider'] is not None
                    and tvbox_config_json['spider'] != ''):
                spider = tvbox_config_json['spider']
                for site in tvbox_config_json['sites']:
                    site['jar'] = spider

            # 1.4 取第一个有值的项目
            for key in get_first_value_keys:
                # 如果该 key 没有取值，则尝试取值
                if key not in get_first_value_keys_tag:
                    # 检查是否能取值
                    if key in tvbox_config_json and tvbox_config_json[key] != '':
                        # 取值
                        merge_tvbox_config_json[key] = tvbox_config_json[key]
                        get_first_value_keys_tag[key] = True  # 设置标志位为 "已取值"

        # 2. 处理配置文件
        process(merge_tvbox_config_json, merge_config['config'])

        # 3. 将聚合后的配置文件写入到目标文件中
        save_tvbox_config_json_to_file(merge_tvbox_config_json, merge_config, task_num, is_merge_config=True)


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        # 展示使用方法
        if sys.argv[1] == '--help':
            print("用法: tvbox-config-updater.py <json 配置文件路径, 可以填写多个，默认为当前命令路径下的 config.json>")
            sys.exit(1)
        else:
            # 获取多个配置文件路径
            config_json_path_list = sys.argv[1:]
    else:
        config_json_path_list = ['config.json']

    # 遍历配置文件路径进行执行
    for i in range(len(config_json_path_list)):
        config_json_file_path = config_json_path_list[i]
        execute(config_json_file_path, i)

    # 输出日志
    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - 所有任务执行完成')
