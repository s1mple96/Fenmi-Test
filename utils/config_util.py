import os
import json
from utils.path_util import resource_path

FOUR_ELEMENTS_KEYS = ['name', 'id_card', 'phone', 'bank_card']

def read_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def four_elements_path():
    return resource_path(os.path.join('config', 'four_elements.json'))

def load_four_elements():
    import os
    from utils.path_util import resource_path
    path = resource_path(os.path.join('config', 'four_elements.json'))
    item = read_json(path)
    if isinstance(item, list) and item:
        item = item[-1]
    elif not item:
        item = {}
    # 只返回四要素字段
    return {k: item.get(k, '') for k in FOUR_ELEMENTS_KEYS}

def save_four_elements(item):
    import os
    from utils.path_util import resource_path
    path = resource_path(os.path.join('config', 'four_elements.json'))
    data = read_json(path)
    if not data:
        data = []
    elif not isinstance(data, list):
        data = [data]
    # 只保存四要素字段
    four_item = {k: item.get(k, '') for k in FOUR_ELEMENTS_KEYS}
    data.append(four_item)
    write_json(path, data)
