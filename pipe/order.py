# order 排序

import re


# 排序
# tvbox_config_json: tvbox 配置文件
# regex_dict: 正则表达式字典 (满足其中一个即命中)
# key_name: 一级 key 名称
# second_key_name: 二级 key 名称
def order(tvbox_config_json, regex_dict, key_name, second_key_name):
    order_data = []

    # 读取数据
    check_data_list = tvbox_config_json[key_name]
    for regex in regex_dict:
        # 检查该正则是否有效
        # 如果表达式为空 / 等于空字符串 / 等于 "*"，则跳过检查
        if regex is None or regex == '' or regex == '*':
            continue
        # 遍历数据
        for i in range(len(check_data_list)):
            data = check_data_list[i]
            # 如果该项命中
            if re.search(regex, data[second_key_name]):
                # 命中
                order_data.append(data)
                # 从原始列表删除
                del check_data_list[i]
                # 中断这一次遍历，检查下一个正则表达式
                break
            # 未命中，则继续检查

    # 检查原始数据是否还有元素，如果有就附加上
    if len(check_data_list) > 0:
        order_data.extend(check_data_list)

    # 回写数据
    tvbox_config_json[key_name] = order_data


# 过滤处理
def process_order(tvbox_config_json, order_config):
    order_filters = [
        ['sitesName', 'sites', 'name'],
        ['parsesName', 'parses', 'name'],
        ['livesName', 'lives', 'name'],
    ]
    for order_filter in order_filters:
        key = order_filter[0]
        if key in order_config and order_config[key] is not None:
            order(tvbox_config_json, order_config[key], order_filter[1], order_filter[2])
