# filter 过滤器

import re


# 过滤器-保留
# tvbox_config_json: tvbox 配置文件
# regex_dict: 正则表达式字典 (满足其中一个即命中)
# key_name: 一级 key 名称
# second_key_name: 二级 key 名称
def filter_keep(tvbox_config_json, regex_dict, key_name, second_key_name):
    # 编译正则表达式
    # 如果存在 "*"，则跳过正则检查
    if "*" in regex_dict:
        return

    regexes = [re.compile(regex)
               for regex in regex_dict if regex != '']

    if key_name in tvbox_config_json:
        # any: 任一条件满足; all: 所有条件满足
        tvbox_config_json[key_name] = [key_data for key_data in tvbox_config_json[key_name]
                                       if any(regex.search(key_data[second_key_name]) for regex in regexes)]


# 过滤处理
def process_filter(tvbox_config_json, filter_config):
    # keep
    keep_filters = [
        ['keepSitesName', 'sites', 'name'],
        ['keepParsesName', 'parses', 'name'],
        ['keepLivesName', 'lives', 'name'],
    ]
    for keep_filter in keep_filters:
        key = keep_filter[0]
        if key in filter_config and filter_config[key] is not None:
            filter_keep(tvbox_config_json, filter_config[key], keep_filter[1], keep_filter[2])

# TODO remove
