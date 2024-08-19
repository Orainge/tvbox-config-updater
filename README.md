# tvbox-config-updater
tvbox 配置文件更新合并程序

启动命令：

```sh
python tvbox-config-updater.py <json 配置文件路径, 默认为当前命令路径下的 config.json>
```

# 1 程序执行流程说明

`读取配置文件->下载配置文件->clean（将输入的文件尽可能地变成标准json格式）->filter->replace->append->order->文件输出`

如果需要合并文件，则将上面的文件合并输出：

`上一步输出的文件->在合并规则的基础上进行合并->filter->replace->append->order->文件输出`

# 2 合并规则

- 以下参数置为空，可通过流程`replace`进行修改：spider
- 以下参数按照`configs`的顺序取第一个存在的值，如没有则不输出：wallpaper、logo
- 以下参数按照`configs`的顺序分别对应追加：sites、parses、lives
- 以下参数的每个object，在合并时会追加参数`jar`，值为对应各自配置文件里`spider`的值：sites

# 3 配置文件示例

```json
{
	"taskConfig": [{
		"name": "XX平台",
        "url": "http://xxx.xxx/xx.json",
        "downloadFilePath": "/home/test/a.json",
		"outputFilePath": "/home/test/a_output.json",
        "jsonFormatting": true,
		"filter": {
			"keepSitesName": ["影视仓", "XX影视"],
			"keepParsesName": ["Json聚合", "Web聚合"],
			"keepLivesName": ["live1", "live2"]
		},
		"replace": {
			"spider": "http://xx.xx",
			"wallpaper": "http://xx.xx",
			"logo": "http://xx.xx"
		},
		"append": {
			"sites": [{
				"key": "xxx",
				"name": "xxx",
				"type": 3,
				"searchable": 0,
				"ext": "http://xx.xxx",
				"api": "http://xx.xxx"
			}],
			"parses": [{
				"name": "xxx",
				"type": 3,
				"url": "xxx"
			}],
			"lives": [{
				"name": "live",
				"type": 0,
				"playerType": 1,
				"url": "http://xx.xxx",
				"epg": "http://xx.xxx",
				"logo": "http://xx.xxx"
			}]
		},
		"order": {
			"sitesName": ["第1个名称", "第2个名称"],
			"parsesName": ["第1个名称", "第2个名称"],
			"livesName": ["第1个名称", "第2个名称"]
		}
	}],
	"mergeConfig": {
		"enable": true,
		"outputFilePath": "/home/test/merge.json",
        "jsonFormatting": true,
		"config": {
			"filter": {
				"keepSitesName": ["影视仓", "XX影视"],
				"keepParsesName": ["Json聚合", "Web聚合"],
				"keepLivesName": ["live1", "live2"]
			},
			"replace": {
				"spider": "http://xx.xx",
				"wallpaper": "http://xx.xx",
				"logo": "http://xx.xx"
			},
			"append": {
				"sites": [{
					"key": "xxx",
					"name": "xxx",
					"type": 3,
					"searchable": 0,
					"ext": "http://xx.xxx",
					"api": "http://xx.xxx"
				}],
				"parses": [{
					"name": "xxx",
					"type": 3,
					"url": "xxx"
				}],
				"lives": [{
					"name": "live",
					"type": 0,
					"playerType": 1,
					"url": "http://xx.xxx",
					"epg": "http://xx.xxx",
					"logo": "http://xx.xxx"
				}]
			},
			"order": {
				"sitesName": ["第1个名称", "第2个名称"],
				"parsesName": ["第1个名称", "第2个名称"],
				"livesName": ["第1个名称", "第2个名称"]
			}
		}
	}
}
```

# 4 配置文件说明

## 4.1 Object

| 参数名称    | 可选/必选 | 类型   | 说明                                                   |
| ----------- | --------- | ------ | ------------------------------------------------------ |
| taskConfig  | 必选      | Object | 更新文件的配置                                         |
| mergeConfig | 可选      | Object | 聚合配置文件的配置，如果不需要合并输出文件，该项可不填 |

## 4.2 configs

| 参数名称         | 可选/必选 | 类型    | 说明                                                         | 示例                       |
| ---------------- | --------- | ------- | ------------------------------------------------------------ | -------------------------- |
| name             | 必选      | String  | 配置项名称，用于日志输出                                     | XX平台                     |
| url              | 必选      | String  | 原始tvbox配置文件的 URL                                      | "http://xxx.xxx/xx.json"   |
| downloadFilePath | 必选      | String  | 下载的tvbox配置文件的存放路径                                | "/home/test/a.json"        |
| outputFilePath   | 必选      | String  | 输出的tvbox配置文件的存放路径                                | "/home/test/a_output.json" |
| jsonFormatting   | 可选      | Boolean | 输出的tvbox配置文件是否格式化，默认为false，设置为false关闭格式化可以减小文件体积 | true                       |
| filter           | 可选      | Object  | 配置项：过滤器                                               |                            |
| replace          | 可选      | Object  | 配置项：替换                                                 |                            |
| append           | 可选      | Object  | 配置项：附加内容                                             |                            |
| order            | 可选      | Object  | 配置项：过滤器                                               |                            |

### 4.2.1 filter

> 常见正则表达式写法：
>
> 不要保留的关键字：^(?!.*不想保留的关键字).*$
>
> 全部不保留（都不命中）：^$
>
> 兼容通配符"*"，即只写星号表示全部命中

| 参数名称      | 可选/必选 | 类型     | 说明                                                         | 示例                    |
| ------------- | --------- | -------- | ------------------------------------------------------------ | ----------------------- |
| keepSitesName | 可选      | [String] | 参数 "sites" 保留的正则表达式，根据对象参数 "name" 检测，可填入多个，多个表示任意一个参数命中即可。 | ["影视仓", "XX影视"]    |
| keepParses    | 可选      | [String] | 参数 "parses" 保留的正则表达式，根据对象参数 "name" 检测，可填入多个，多个表示任意一个参数命中即可。 | ["Json聚合", "Web聚合"] |
| keepLivesName | 可选      | [String] | 参数 "lives" 保留的正则表达式，根据对象参数 "name" 检测，可填入多个，多个表示任意一个参数命中即可。 | ["live1", "live2"]      |

### 4.2.2 replace

| 参数名称  | 可选/必选 | 类型   | 说明                                        | 示例           |
| --------- | --------- | ------ | ------------------------------------------- | -------------- |
| spider    | 可选      | String | 覆写参数 "spider" 的值，不填写表示不复写    | "http://xx.xx" |
| wallpaper | 可选      | String | 覆写参数 "wallpaper" 的值，不填写表示不复写 | "http://xx.xx" |
| logo      | 可选      | String | 覆写参数 "logo" 的值，不填写表示不复写      | "http://xx.xx" |

### 4.2.3 replace

| 参数名称 | 可选/必选 | 类型     | 说明                                     | 示例 |
| -------- | --------- | -------- | ---------------------------------------- | ---- |
| sites    | 可选      | [Object] | 向参数 "sites" 追加值，不填写表示不追加  |      |
| parses   | 可选      | [Object] | 向参数 "parses" 追加值，不填写表示不追加 |      |
| lives    | 可选      | [Object] | 向参数 "lives" 追加值，不填写表示不追加  |      |

### 4.2.4 order

| 参数名称   | 可选/必选 | 类型     | 说明                                                         | 示例                       |
| ---------- | --------- | -------- | ------------------------------------------------------------ | -------------------------- |
| sitesName  | 可选      | [String] | 参数 "sites" 中的对象根据键 "name" 进行排序，如果参数数量少于原始数据个数，那么剩余项将按照原始顺序排序 | ["第1个名称", "第2个名称"] |
| parsesName | 可选      | [String] | 参数 "parses" 中的对象根据键 "name" 进行排序，如果参数数量少于原始数据个数，那么剩余项将按照原始顺序排序 | ["第1个名称", "第2个名称"] |
| livesName  | 可选      | [String] | 参数 "lives" 中的对象根据键 "name" 进行排序，如果参数数量少于原始数据个数，那么剩余项将按照原始顺序排序 | ["第1个名称", "第2个名称"] |

## 4.3 mergeConfig

| 参数名称       | 可选/必选 | 类型    | 说明                                                         | 示例                    |
| -------------- | --------- | ------- | ------------------------------------------------------------ | ----------------------- |
| enable         | 必选      | Boolean | 是否启用聚合输出                                             | true                    |
| outputFilePath | 必选      | String  | 聚合的tvbox配置文件的输出路径                                | "/home/test/merge.json" |
| jsonFormatting | 可选      | Boolean | 输出的tvbox配置文件是否格式化，默认为false，设置为false关闭格式化可以减小文件体积 | true                    |
| config         | 必选      | String  | 配置项：聚合输出                                             |                         |

### 4.3.1 config

| 参数名称 | 可选/必选 | 类型   | 说明                               | 示例 |
| -------- | --------- | ------ | ---------------------------------- | ---- |
| filter   | 可选      | Object | 配置项：过滤器，参数说明同 2.2.1   |      |
| replace  | 可选      | Object | 配置项：替换，参数说明同 2.2.2     |      |
| append   | 可选      | Object | 配置项：附加内容，参数说明同 2.2.3 |      |
| order    | 可选      | Object | 配置项：过滤器，参数说明同 2.2.4   |      |
