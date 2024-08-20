# replace 替换

# 替换
def process_replace(tvbox_config_json, replace_config):
    # 哪些项是根据数组里 object 的 key 进行替换的
    replace_by_key_keys = ['sites', 'parses', 'lives']

    if len(replace_config) > 0:
        for key, value in replace_config.items():
            if key not in replace_by_key_keys:
                # 原值替换
                tvbox_config_json[key] = value
            else:
                # 根据 key 进行替换
                target_list = tvbox_config_json[key]  # 原始列表
                replace_list = value.copy()  # 需要替换的列表

                for obj in target_list:
                    for ri in range(len(replace_list)):
                        replace_obj = replace_list[ri]
                        # 如果 key 匹配
                        if obj['key'] == replace_obj['key']:
                            # 匹配
                            for rk, rv in replace_obj.items():
                                if rk != 'key':
                                    if rv is None:
                                        # 如果 key == null，则删除该项
                                        del obj[rk]
                                    else:
                                        # 否则赋新值
                                        obj[rk] = rv

                            # 从 replace_list 中移除要匹配的值
                            del replace_list[ri]

                            # 中断 replace_list 循环
                            break
