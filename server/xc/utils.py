def remove_empty_children(node):
    """递归移除空的 children 字段"""
    if isinstance(node, dict) and 'children' in node:
        if isinstance(node['children'], list):
            # 递归清理子节点
            cleaned_children = []
            for child in node['children']:
                cleaned_child = remove_empty_children(child)
                if cleaned_child is not None:
                    cleaned_children.append(cleaned_child)
            node['children'] = cleaned_children
        # 如果 children 为空，删除该字段
        if not node['children']:
            del node['children']
    return node


def fetch_tree(root_tag=None, queryset_values=None, primary_key='id'):
    """
    将扁平的父子结构数据构建成树。

    :param root_tag: 根节点的 parent 值（如 None, '', 0）
    :param queryset_values: QuerySet.values() 返回的字典列表，需包含 'id', 'parent'
    :param primary_key: 主键字段名，默认 'id'
    :return: 树形结构的列表
    """
    if not queryset_values:
        return []

    # 标准化数据：确保 id 和 parent 是可比较的（统一为 str 或 None）
    tree_load = {}
    processed_nodes = []

    for item in queryset_values:
        item = dict(item)  # 转为可变 dict（QuerySet.values() 返回的是不可变 Row）
        pk = item[primary_key]
        parent = item.get('parent')

        # 统一主键为字符串（便于比较），但保留原始类型也可，这里按原逻辑
        item[primary_key] = str(pk) if pk is not None else None
        # parent 为 None 或空值时，统一为 None
        item['parent'] = str(parent) if parent not in (None, '', 0) else None

        item['children'] = []
        tree_load[item[primary_key]] = item
        processed_nodes.append(item)

    # 构建父子关系
    for node in processed_nodes:
        parent_val = node['parent']
        if parent_val == root_tag:
            # 属于顶层节点
            continue
        if parent_val in tree_load:
            tree_load[parent_val]['children'].append(node)

    # 收集根节点
    root_nodes = [
        node for node in processed_nodes
        if node['parent'] == root_tag
    ]

    # 清理空 children
    tree = [remove_empty_children(node) for node in root_nodes]
    return tree
