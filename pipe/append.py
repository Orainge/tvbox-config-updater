# append 添加

# 添加
def process_append(tvbox_config_json, append_config):
    if len(append_config) > 0:
        for key, values in append_config.items():
            for value in values:
                tvbox_config_json[key].append(value)
