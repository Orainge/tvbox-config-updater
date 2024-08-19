# replace 替换

# 替换
def process_replace(tvbox_config_json, replace_config):
    if len(replace_config) > 0:
        for key, value in replace_config.items():
            tvbox_config_json[key] = value
