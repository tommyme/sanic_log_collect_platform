def get_lake_keys(data: dict, needed_fields):
    return [key for key in needed_fields if key not in data.keys()]

def build_keys_dict(data: dict, needed_fields):
    return {k: v for k, v in data.items() if k in needed_fields}

def query_build(data, needed_fields):
    """检查need fields 对data进行裁剪"""
    lake_keys = get_lake_keys(data, needed_fields)
    query = build_keys_dict(data, needed_fields)
    return lake_keys, query

def query_build_trust(data, needed_fields):
    """检查need fields 不对data进行裁剪"""
    lake_keys = get_lake_keys(data, needed_fields)
    # query = build_keys_dict(data, needed_fields)
    return lake_keys, data