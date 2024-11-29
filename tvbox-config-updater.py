import json
import logging
import os
import re
import requests
import sys
from typing import List, Any, Callable

# 定义配置 key
CONFIG_KEY_TASK_CONFIG = 'taskConfig'  # 任务配置
CONFIG_KEY_MERGE_CONFIG = 'mergeConfig'  # 聚合输出配置
CONFIG_KEY_NAME = 'name'  # 任务名称
CONFIG_KEY_NUMBER = 'number'  # 任务序号
CONFIG_KEY_URL = 'url'  # 下载文件 URL
CONFIG_KEY_USER_AGENT = 'userAgent'  # 下载文件使用的用户代理
CONFIG_KEY_RETRY_TIMES = 'retryTimes'  # 下载文件重试次数
CONFIG_KEY_DOWNLOAD_FILE_PATH = 'downloadFilePath'  # 下载文件路径
CONFIG_KEY_INPUT_FILE_PATH = 'inputFilePath'  # 输入文件路径
CONFIG_KEY_OUTPUT_FILE_PATH = 'outputFilePath'  # 输出文件路径
CONFIG_KEY_JSON_FORMATTING = 'jsonFormatting'  # 格式化输出 JSON
CONFIG_KEY_FILTER = 'filter'  # 任务：过滤
CONFIG_KEY_REPLACE = 'replace'  # 任务：替换
CONFIG_KEY_APPEND = 'append'  # 任务：附加
CONFIG_KEY_ORDER = 'order'  # 任务：排序


class DefaultException(Exception):
    def __init__(self,
                 exception_type: str = "异常",
                 text: str = None,
                 task_name: int = None,
                 task_number: int = None,
                 exception: Exception = None,
                 print_exception=True):
        """
        :param exception_type: 异常类型
        :param text: 异常信息
        :param task_name: 任务名称
        :param task_number: 任务序号
        :param exception: 由于什么异常触发
        :param print_exception: 是否打印触发异常
        """
        self.text = ''

        if task_number is not None or task_name is not None:
            self.text += (f'[任务{f" {task_number}" if task_number is not None else ""}'
                          f'{f" - {task_name}" if task_name is not None else ""}] - ')

        self.text += f'{exception_type} - {text}'

        # 如果传入了 exception，打印它
        if exception is not None and print_exception:
            logging.error(f'发生异常：{exception}', exc_info=True)

    def __str__(self):
        return self.text


class ConfigException(DefaultException):
    """配置文件异常"""

    def __init__(self,
                 text: str = None,
                 task_name: int = None,
                 task_number: int = None,
                 exception: Exception = None):
        super().__init__(exception_type="配置文件异常",
                         text=text,
                         task_name=task_name,
                         task_number=task_number,
                         exception=exception)


class TaskException(DefaultException):
    """任务执行异常"""

    def __init__(self,
                 text: str = None,
                 task_name: int = None,
                 task_number: int = None,
                 exception: Exception = None):
        super().__init__(exception_type="任务执行异常",
                         text=text,
                         task_name=task_name,
                         task_number=task_number,
                         exception=exception)


class ProcessTaskException(DefaultException):
    """处理任务执行异常"""

    def __init__(self,
                 text: str = None,
                 task_name: int = None,
                 task_number: int = None,
                 exception: Exception = None):
        super().__init__(exception_type="处理任务执行异常",
                         text=text,
                         task_name=task_name,
                         task_number=task_number,
                         exception=exception)


class DownloadFileException(DefaultException):
    """下载文件异常"""

    def __init__(self,
                 url: str = None,
                 task_name: int = None,
                 task_number: int = None,
                 exception: Exception = None):
        super().__init__(exception_type="下载文件异常",
                         text=f"URL: {url}" if url is not None else None,
                         task_name=task_name,
                         task_number=task_number,
                         exception=exception)


class TvboxConfigFileSaver:
    """tvbox 配置文件文件保存器"""
    logger = logging.getLogger(__name__)

    def __init__(self,
                 save_config: dict,
                 to_save_tvbox_config: dict,
                 task_name: str = None,
                 task_number: int = None,
                 is_merge_config_task=False):
        """
        初始化下载器
        :param save_config: 保存文件配置
        :param to_save_tvbox_config: 要保存的 tvbox 配置文件
        :param task_name: 任务名称
        :param task_number: 任务编号
        :param is_merge_config_task: 是否是聚合配置文件任务，默认 False
        """
        self.save_config = save_config
        self.to_save_tvbox_config = to_save_tvbox_config
        self.task_name = task_name
        self.task_number = task_number
        self.is_merge_config_task = is_merge_config_task

    def execute(self):
        """执行"""
        self._save_tvbox_config_json_to_file()

    def _save_tvbox_config_json_to_file(self):
        """
        内部方法：将 tvbox 配置 json 保存到文件中
        """
        # 获取输出文件路径
        output_file_path = self._get_save_config([CONFIG_KEY_OUTPUT_FILE_PATH], "")
        if len(output_file_path) < 0:
            raise ConfigException(text="请填写输出文件路径",
                                  task_name=self.task_name,
                                  task_number=self.task_number)

        # 1. 检查是否开启 JSON 格式化输出
        indent = None
        if CONFIG_KEY_JSON_FORMATTING in self.save_config and self.save_config[CONFIG_KEY_JSON_FORMATTING] is True:
            indent = 4

        # 2. 删除输出文件（如果存在的话）
        if os.path.exists(output_file_path):
            os.remove(output_file_path)

        # 3. 将过滤后的结果写入输出的JSON文件
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            json.dump(self.to_save_tvbox_config, outfile, ensure_ascii=False, indent=indent)

        # 输出日志
        if self.is_merge_config_task:
            self._log(f'配置文件聚合完成: {output_file_path}')
        else:
            self._log(f'配置文件处理完成: {output_file_path}')

    def _get_save_config(self, keys: List[str], default_value: Any = None) -> Any:
        """
        获取配置项
        :param keys: 配置 key 数组，例：获取 a.b.c 的值，传入 ["a", "b", "c"]
        :param default_value: 如果没有对应的值，返回的默认值
        :return:
        """
        if self.save_config is None:
            return None

        item = self.save_config

        for key in keys:
            if key in item:
                # 存在该项，赋值
                item = item[key]
            else:
                # 不存在该项，返回默认值
                return default_value

        # 返回设置的值
        return item

    def _log(self, text: str, level: int = logging.INFO):
        """
        打印日志
        :param text: 日志内容
        :param level: 日志级别，默认 INFO
        :return:
        """
        log_text = ''

        if self.task_number is not None or self.task_name is not None:
            log_text += (f'[任务{f" {self.task_number}" if self.task_number is not None else ""}'
                         f'{f" ({self.task_name})" if self.task_name is not None else ""}] - ')

        log_text += text

        self.logger.log(level, log_text)


class UpdateJob:
    """更新工作类"""

    def __init__(self,
                 update_job_config: dict = None,
                 update_job_config_json_path: str = None):
        """
        初始化更新工作类示例（配置文件 dict 和 配置文件路径 二选一）
        :param update_job_config: 更新工作配置文件 dict
        :param update_job_config_json_path: 更新工作配置文件路径
        """
        self.update_job_config_json_path = update_job_config_json_path
        self.update_job_config = update_job_config
        self.tvbox_config_list = []  # 所有处理完成的 tvbox 配置文件

        # 初始化任务
        # 加载更新任务配置
        if self.update_job_config_json_path is not None:
            # 从文件读取
            try:
                with open(self.update_job_config_json_path, 'r', encoding='utf-8') as input_file:
                    self.update_job_config = json.load(input_file)
            except Exception as ujex:
                raise ConfigException('读取配置文件错误，请检查', exception=ujex)
        elif self.update_job_config is None:
            raise ConfigException('缺少任务配置文件')

        # 获取处理工作配置列表
        self.task_config_list = self._get_update_task_config([CONFIG_KEY_TASK_CONFIG])
        if self.task_config_list is None:
            raise ConfigException(f'缺少配置 [{CONFIG_KEY_TASK_CONFIG}]')

        # 获取聚合配置（如果有）
        self.merge_config = self._get_update_task_config([CONFIG_KEY_MERGE_CONFIG])

    def execute(self):
        """执行任务"""
        for index in range(len(self.task_config_list)):
            tvbox_config_dict = Task(task_config=self.task_config_list[index], task_number=index + 1).execute()
            self.tvbox_config_list.append(tvbox_config_dict)

        # 执行聚合任务
        if self._get_update_task_config([CONFIG_KEY_MERGE_CONFIG, 'enable'], False) is True:
            MergeTask(merge_config=self.merge_config, tvbox_config_list=self.tvbox_config_list).execute()

    def _get_update_task_config(self, keys: List[str], default_value: Any = None) -> Any:
        """
        获取任务配置项
        :param keys: 配置 key 数组，例：获取 a.b.c 的值，传入 ["a", "b", "c"]
        :param default_value: 如果没有对应的值，返回的默认值
        :return:
        """
        if self.update_job_config is None:
            return None

        item = self.update_job_config

        for key in keys:
            if key in item:
                # 存在该项，赋值
                item = item[key]
            else:
                # 不存在该项，返回默认值
                return default_value

        # 返回设置的值
        return item


class Task:
    """任务类"""
    logger = logging.getLogger(__name__)

    def __init__(self,
                 task_config: dict,
                 task_number: int):
        """
        初始化
        :param task_config: 任务配置
        :param task_number: 任务序号
        """
        self.tvbox_config = None
        self.task_config = task_config
        self.task_name = self._get_task_config([CONFIG_KEY_NAME], "")
        self.task_number = task_number

    def execute(self) -> dict:
        """
        执行任务
        :return: tvbox 配置 dict
        """
        # 加载 tvbox 配置文件
        self._load_tvbox_config()

        # 清洗 tvbox 配置文件
        self._clean()

        # 将文件转换为 dict
        self.tvbox_config = json.loads(self.tvbox_config_text)

        # 执行处理工作
        self.tvbox_config = ProcessTask(tvbox_config=self.tvbox_config,
                                        process_task_config=self.task_config,
                                        task_name=self.task_name,
                                        task_number=self.task_number).execute()
        # 将文件保存到硬盘上（如果需要）
        output_file_path = self._get_task_config([CONFIG_KEY_OUTPUT_FILE_PATH], "")
        if len(output_file_path) == 0:
            self._log("未填写输出文件保存路径，处理完成的文件不会被保存到硬盘上",
                      level=logging.WARNING)
        else:
            TvboxConfigFileSaver(save_config=self.task_config,
                                 to_save_tvbox_config=self.tvbox_config,
                                 task_name=self.task_name,
                                 task_number=self.task_number).execute()

        # 执行完成，返回 tvbox 配置 dict
        return self.tvbox_config

    def _load_tvbox_config(self):
        """
        获取 tvbox 配置
        """
        if self._get_task_config([CONFIG_KEY_URL], "") != "":
            # 下载文件
            self._download_tvbox_config_file()
        elif self._get_task_config([CONFIG_KEY_INPUT_FILE_PATH], "") != "":
            # 读取文件
            self._input_tvbox_config_file()
        else:
            # 抛出异常
            raise ConfigException(text="请至少指定一个 tvbox 配置文件来源",
                                  task_name=self.task_name,
                                  task_number=self.task_number)

    def _download_tvbox_config_file(self):
        """
        内部方法：下载文件
        :return tvbox 配置文件文本
        """
        # 获取下载文件保存路径
        user_agent = self._get_task_config([CONFIG_KEY_USER_AGENT], "okhttp/3.15")  # 请求用户代理
        retry_times = self._get_task_config([CONFIG_KEY_RETRY_TIMES], 3)  # 请求的最大重试次数
        download_file_path = self._get_task_config([CONFIG_KEY_DOWNLOAD_FILE_PATH], "")
        if len(download_file_path) == 0:
            self._log('未填写下载文件保存路径，下载的文件不会被保存到硬盘上',
                      level=logging.WARNING)

        # 获取文件 URL
        url = self._get_task_config([CONFIG_KEY_URL])

        for attempt in range(retry_times):
            try:
                response = requests.get(url=url,
                                        headers={'User-Agent': user_agent})
                response.raise_for_status()

                # 直接将内容写入目标文件，覆盖原文件
                if download_file_path is not None:
                    with open(download_file_path, 'wb') as file:
                        file.write(response.content)

                self._log(f'文件下载成功: {download_file_path}')

                # 将下载的内容返回，不需要再从文件读入，文件下载仅作保存使用
                self.tvbox_config_text = response.content.decode('UTF-8')
                return

            except requests.exceptions.RequestException:
                self._log(f'文件下载失败 (第 {attempt + 1} 次尝试)',
                          level=logging.WARNING)

        # 重试下载失败，直接抛出异常
        self._log(f'文件下载失败 (共重试 {retry_times} 次)', level=logging.ERROR)
        raise DownloadFileException(url=url)

    def _input_tvbox_config_file(self):
        """
        从文件中读取 tvbox 配置文件文本
        :return tvbox 配置文件文本
        """
        input_file_path = self._get_task_config([CONFIG_KEY_INPUT_FILE_PATH])

        # 读取文件到变量中
        with open(input_file_path, 'r', encoding='utf-8') as infile:
            file_content = infile.read()

        # 返回文件内容
        self.tvbox_config_text = file_content

    def _clean(self):
        """
        清洗 tvbox 配置文本
        :return: 清洗后的文本
        """
        processed_lines = []

        for line in self.tvbox_config_text.splitlines():
            stripped_line = line.strip()
            # 忽略以 '//' 开头的行和空行
            if not stripped_line.startswith('//') and stripped_line != '':
                processed_lines.append(stripped_line)

        self.tvbox_config_text = "\n".join(processed_lines)

    def _get_task_config(self, keys: List[str], default_value: Any = None) -> Any:
        """
        获取任务配置项
        :param keys: 配置 key 数组，例：获取 a.b.c 的值，传入 ["a", "b", "c"]
        :param default_value: 如果没有对应的值，返回的默认值
        :return:
        """
        if self.task_config is None:
            return None

        item = self.task_config

        for key in keys:
            if key in item:
                # 存在该项，赋值
                item = item[key]
            else:
                # 不存在该项，返回默认值
                return default_value

        # 返回设置的值
        return item

    def _log(self, text: str, level: int = logging.INFO):
        """
        打印日志
        :param text: 日志内容
        :param level: 日志级别，默认 INFO
        :return:
        """
        log_text = ''

        if self.task_number is not None or self.task_name is not None:
            log_text += (f'[任务{f" {self.task_number}" if self.task_number is not None else ""}'
                         f'{f" ({self.task_name})" if self.task_name is not None else ""}] - ')

        log_text += text

        self.logger.log(level, log_text)


class MergeTask:
    """聚合任务类"""
    logger = logging.getLogger(__name__)

    def __init__(self,
                 merge_config: dict,
                 tvbox_config_list: list,
                 task_name: str = None,
                 task_number: int = None):
        """
        初始化
        :param merge_config: 聚合任务配置
        :param tvbox_config_list: tvbox 配置文件列表
        :param task_name: 任务名称
        :param task_number: 任务序号
        :return:
        """
        self.merge_config = merge_config
        self.tvbox_config_list = tvbox_config_list
        self.task_name = task_name
        self.task_number = task_number
        self.merge_tvbox_config = None

    def execute(self):
        # 配置项
        # 取第一个有值的 key
        get_first_value_keys = ['wallpaper', 'logo']

        # 需要追加合并的 key
        append_value_keys = ['sites', 'parses', 'lives']

        # 1. 根据合并规则进行处理
        self.merge_tvbox_config = {
            'spider': '',  # 1.1 spider 置为空字符串
        }

        # 配置追加数组
        for key in append_value_keys:
            self.merge_tvbox_config[key] = []

        # 用于判断是否取值完成
        get_first_value_keys_tag = {}

        # 遍历每个 tvbox_config
        for tvbox_config in self.tvbox_config_list:
            # 1.2 追加数据到合并项中
            for key in append_value_keys:
                if key in tvbox_config:
                    self.merge_tvbox_config[key].extend(tvbox_config[key])

            # 1.3 向每个项目追加项 jar（如果不存在 jar）, 值为 各自的 spider 的值（如有）
            if ('spider' in tvbox_config
                    and tvbox_config['spider'] is not None
                    and tvbox_config['spider'] != ''):
                spider = tvbox_config['spider']
                for site in tvbox_config['sites']:
                    if 'jar' not in site:
                        site['jar'] = spider

            # 1.4 取第一个有值的项目
            for key in get_first_value_keys:
                # 如果该 key 没有取值，则尝试取值
                if key not in get_first_value_keys_tag:
                    # 检查是否能取值
                    if key in tvbox_config and tvbox_config[key] != '':
                        # 取值
                        self.merge_tvbox_config[key] = tvbox_config[key]
                        get_first_value_keys_tag[key] = True  # 设置标志位为 "已取值"

        # 2. 处理配置文件
        self.merge_tvbox_config = ProcessTask(tvbox_config=self.merge_tvbox_config,
                                              process_task_config=self.merge_config,
                                              task_name="聚合任务").execute()

        # 3. 将聚合后的配置文件写入到目标文件中
        output_file_path = self._get_merge_config([CONFIG_KEY_OUTPUT_FILE_PATH], "")
        if len(output_file_path) == 0:
            raise TaskException(text="未填写聚合配置文件输出路径",
                                task_name=self.task_name,
                                task_number=self.task_number)
        else:
            TvboxConfigFileSaver(save_config=self.merge_config,
                                 to_save_tvbox_config=self.merge_tvbox_config,
                                 task_name=self.task_name,
                                 task_number=self.task_number,
                                 is_merge_config_task=True).execute()

    def _get_merge_config(self, keys: List[str], default_value: Any = None) -> Any:
        """
        获取任务配置项
        :param keys: 配置 key 数组，例：获取 a.b.c 的值，传入 ["a", "b", "c"]
        :param default_value: 如果没有对应的值，返回的默认值
        :return:
        """
        if self.merge_config is None:
            return None

        item = self.merge_config

        for key in keys:
            if key in item:
                # 存在该项，赋值
                item = item[key]
            else:
                # 不存在该项，返回默认值
                return default_value

        # 返回设置的值
        return item

    def _log(self, text: str, level: int = logging.INFO):
        """
        打印日志
        :param text: 日志内容
        :param level: 日志级别，默认 INFO
        :return:
        """
        log_text = ''

        if self.task_number is not None or self.task_name is not None:
            log_text += (f'[任务{f" {self.task_number}" if self.task_number is not None else ""}'
                         f'{f" ({self.task_name})" if self.task_name is not None else ""}] - ')

        log_text += text

        self.logger.log(level, log_text)


class ProcessTask:
    """处理任务类"""
    logger = logging.getLogger(__name__)

    def __init__(self, tvbox_config: dict,
                 process_task_config: dict,
                 task_name: str = None,
                 task_number: int = None):
        """
        初始化任务类实例
        :param tvbox_config: tvbox 配置文件 dict
        :param process_task_config: 处理工作配置
        :param task_name: 任务名称
        :param task_number: 任务序号
        """
        self.tvbox_config = tvbox_config
        self.process_task_config = process_task_config
        self.task_name = task_name
        self.task_number = task_number

    def execute(self):
        """
        执行处理任务
        :return: 处理完成的 tvbox 配置文件 dict
        """
        try:
            # 1. 任务：过滤
            self._execute(self._filter, CONFIG_KEY_FILTER)

            # 2. 任务：替换
            self._execute(self._replace, CONFIG_KEY_REPLACE)

            # 3. 任务：附加参数
            self._execute(self._append, CONFIG_KEY_APPEND)

            # 4. 任务：排序
            self._execute(self._order, CONFIG_KEY_ORDER)
        except Exception as ptex:
            raise ProcessTaskException(task_name=self.task_name,
                                       task_number=self.task_number,
                                       exception=ptex)

        # 返回处理完成的 tvbox 配置文件 dict
        return self.tvbox_config

    def _execute(self, processor: Callable, config_key: str):
        """
        判断是否需要执行处理器
        :param processor: 处理器函数
        :param config_key: 处理器使用的配置 dict 在任务配置中的 key
        :return:
        """
        if config_key in self.process_task_config and len(self.process_task_config[config_key]) > 0:
            processor(config_key=config_key)

    def _filter(self, config_key: str):
        """
        处理器：过滤
        :param config_key: 配置 key
        :return:
        """
        # 定义过滤规则
        keep_filters = [
            ['keepSitesName', 'sites', 'name'],
            ['keepParsesName', 'parses', 'name'],
            ['keepLivesName', 'lives', 'name'],
        ]

        # 遍历过滤规则并执行
        filter_config = self.process_task_config[config_key]
        for keep_filter in keep_filters:
            key = keep_filter[0]
            if key in filter_config and filter_config[key] is not None:
                self._filter_keep(filter_config[key], keep_filter[1], keep_filter[2])

    def _filter_keep(self, regex_dict, key_name, second_key_name):
        """
        过滤器: 按指定正则表达式过滤数据
        :param regex_dict: 正则表达式字典 (满足其中一个即命中)
        :param key_name: 一级 key 名称
        :param second_key_name: 二级 key 名称
        """
        # 如果存在 "*"，则直接跳过正则检查
        if "*" in regex_dict:
            return

        # 编译正则表达式
        regexes = [re.compile(regex) for regex in regex_dict if regex != '']

        if key_name in self.tvbox_config:
            # 筛选满足条件的数据
            self.tvbox_config[key_name] = [
                key_data for key_data in self.tvbox_config[key_name]
                if second_key_name in key_data and any(
                    regex.search(key_data[second_key_name]) for regex in regexes
                )]

    def _replace(self, config_key: str):
        """
        处理器：替换
        :param config_key: 配置 key
        :return:
        """

        # 定义哪些字段需要替换
        replace_keys = ['sites', 'parses', 'lives']

        # 执行替换过程
        replace_config = self.process_task_config[config_key]
        for key, value in replace_config.items():
            if key not in replace_keys:
                # 原值替换
                self.tvbox_config[key] = value
            else:
                # 根据 key 进行替换
                target_list = self.tvbox_config[key]  # 原始列表
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
                                        # 如果值为 None，则删除该项
                                        del obj[rk]
                                    else:
                                        # 否则赋新值
                                        obj[rk] = rv

                            # 从 replace_list 中移除要匹配的值
                            del replace_list[ri]

                            # 中断 replace_list 循环
                            break

    def _append(self, config_key: str):
        """
        处理器：附加参数
        :param config_key: 配置 key
        :return:
        """
        append_config = self.process_task_config[config_key]
        if self.tvbox_config is not None and len(append_config) > 0:
            for key, values in append_config.items():
                for value in values:
                    self.tvbox_config[key].append(value)

    def _order(self, config_key: str):
        """
        处理器：排序
        :param config_key: 配置 key
        :return:
        """
        # 定义哪些字段需要排序
        order_keys = [
            ['sitesName', 'sites', 'name'],
            ['parsesName', 'parses', 'name'],
            ['livesName', 'lives', 'name'],
        ]

        # 执行排序
        order_config = self.process_task_config[config_key]
        for order_filter in order_keys:
            key = order_filter[0]
            if key in order_config and order_config[key] is not None:
                self._order_data(order_config[key], order_filter[1], order_filter[2])

    def _order_data(self, regex_dict, key_name, second_key_name):
        """
        内部方法：排序
        :param regex_dict: 正则表达式字典 (满足其中一个即命中)
        :param key_name: 一级 key 名称
        :param second_key_name: 二级 key 名称
        :return: 排序后的配置文件
        """
        order_data = []

        # 读取数据
        check_data_list = self.tvbox_config[key_name]
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
        self.tvbox_config[key_name] = order_data

    def _get_process_job_config(self, keys: List[str], default_value: Any = None) -> Any:
        """
        获取任务配置项
        :param keys: 配置 key 数组，例：获取 a.b.c 的值，传入 ["a", "b", "c"]
        :param default_value: 如果没有对应的值，返回的默认值
        :return:
        """
        if self.process_task_config is None:
            return None

        item = self.process_task_config

        for key in keys:
            if key in item:
                # 存在该项，赋值
                item = item[key]
            else:
                # 不存在该项，返回默认值
                return default_value

        # 返回设置的值
        return item

    def _log(self, text: str, level: int = logging.INFO):
        """
        打印日志
        :param text: 日志内容
        :param level: 日志级别，默认 INFO
        :return:
        """
        log_text = ''

        if self.task_number is not None or self.task_name is not None:
            log_text += (f'[任务{f" {self.task_number}" if self.task_number is not None else ""}'
                         f'{f" ({self.task_name})" if self.task_name is not None else ""}] - ')

        log_text += text

        self.logger.log(level, log_text)


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        # 展示使用方法
        if sys.argv[1] == '--help':
            print("""tvbox 配置文件更新助手
            用法:
                tvbox-config-updater.py [选项] <配置文件路径>

            说明:
                <配置文件路径> 可以填写多个，默认为当前命令路径下的 config.json。

            选项:
                --help       显示此帮助信息
            """)
            sys.exit(1)
        else:
            # 获取多个配置文件路径
            update_job_config_file_path_list = sys.argv[1:]
    else:
        update_job_config_file_path_list = ['config.json']

    logging.basicConfig(
        level=logging.INFO,  # 设置日志级别
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 设置日志格式
        datefmt='%Y-%m-%d %H:%M:%S',  # 自定义时间格式，不包含毫秒
        handlers=[logging.StreamHandler()]  # 设置日志输出到控制台
    )

    # 遍历配置文件路径进行执行
    for path in update_job_config_file_path_list:
        UpdateJob(update_job_config_json_path=path).execute()
