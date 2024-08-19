# clean 文件清洗

import json


# 过滤处理
# tvbox_config_file_object: 文件对象 (file object)
# 返回: json 对象
def process_clean(tvbox_config_content, task_config):
    processed_lines = []

    for line in tvbox_config_content.splitlines():
        stripped_line = line.strip()
        # 忽略以 '//' 开头的行和空行
        if not stripped_line.startswith('//') and stripped_line != '':
            processed_lines.append(stripped_line)

    content = "\n".join(processed_lines)
    return json.loads(content)
