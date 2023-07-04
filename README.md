# Hackday
## Crawler
### Developer Guide
After a period of thorough investigation and exploration, I have successfully extracted the information from the official Hubei Provincial Government Service website. The extracted information has been stored in the [data.json](data.json) file, which is an array. Each element within the array represents an object.Subsequently, I will elucidate the constituent elements of the potentially useful key-value pairs for further discussion.
```json
{
   "title": "str",
   "subtitle": "str",
   "详情": [
      {
         "标题": "基本信息",
         "<other useful info>": "str"
      },
      {
         "标题": "窗口办理",
         "<other useful info>": "str"
      },
      {
         "标题": "受理条件",
         "<other useful info>": "str"
      },
      {
         "标题": "办理流程",
         "<other useful info>": "str"
      },
      {
         "标题": "申请材料",
         "<other useful info>": "str"
      },
      {
         "标题": "许可收费",
         "<other useful info>": "str"
      },
      {
         "标题": "中介服务",
         "<other useful info>": "str"
      },
      {
         "标题": "设定依据",
         "<other useful info>": "str"
      }
   ]
}
```

Considering the size of [data.json](data.json) (approximately 7MB), it might pose challenges to obtain a satisfactory reading experience within an IDE. To facilitate reference, I can provide a Python script that utilizes streaming to iterate through each object and store them in separate files to make your life easier🤗.
```python
import json
import json_stream
from pathlib import Path

metas_fn = Path("data.json")
data_dir = Path("datas")
if not data_dir.exists():
    data_dir.mkdir()

with open(metas_fn) as f:
    for meta in json_stream.load(f):
        meta = json_stream.to_standard_types(meta)
        data_fn = data_dir / f"{str(meta['taskCode'])}.json"
        data_fn.write_text(json.dumps(meta, indent=4, ensure_ascii=False))
```
Wishing you a delightful coding experience!

# References

1. https://github.com/PKU-YuanGroup/ChatLaw
2. https://huggingface.co/IDEA-CCNL/Ziya-LLaMA-13B-v1