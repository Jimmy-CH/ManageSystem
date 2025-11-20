from django.db.models import F

from apps.basic.models import Menu, MenuConnPermission, Org, Employee

ROOT_CODE = '888888'  # 集团的部门编码
TECH_ROOT = '999158'  # 信息科技公司编码


def remove_empty_children(node):
    if isinstance(node, dict) and 'children' in node:
        # 递归处理子节点
        if isinstance(node['children'], list):
            node['children'] = [remove_empty_children(child) for child in node['children']]
            # 移除空的子节点
            node['children'] = [child for child in node['children'] if child is not None]
        # 移除当前节点的children属性，如果它是空的
        if not node['children']:
            del node['children']
    return node


def fetch_tree(root_tag=None, queryset_values=None, primary_key='id'):
    """
    root_tag：所属节点下的子节点，若拿所有节点root_tag为一级节点的parent值(通常为None、空字符串)
    queryset_values：传入资源节点的queryset.values(*fields)
    primary_key: 资源数据的主键字段
    """
    tree_load, tree_data = {}, []
    for value in queryset_values:
        value['children'] = []
        value[primary_key] = str(value[primary_key])
        value['parent'] = str(value['parent']) if value['parent'] else value['parent']
        tree_load[value[primary_key]] = value
    for value in queryset_values:
        if value['parent'] == root_tag:
            tree_data.append(value)
        if value['parent'] in tree_load:
            tree_load[value['parent']]['children'].append(value)
    tree = [remove_empty_children(node) for node in tree_data]
    return tree


def fetch_menu_tree(root_menu=None, menus=None):
    """
    root_menu：所属菜单下的子菜单，None代表拿所有菜单
    menus：如果需要外界循环调用，建议外部传入menus
    """
    tree_load, tree_data = {}, []
    if menus is None:
        menus = Menu.objects.select_related('created_by').order_by('order').values(
            'id', 'name', 'level', 'kind', 'parent', 'path', 'component', 'icon', 'order', 'is_active',
            'is_hidden', 'created_time', 'created_by__psncode', 'created_by__psnname', 'created_by__deptcode__org_name'
        )
    for m in menus:
        m['create_user_info'] = {
            'psncode': m.get('created_by__psncode'),
            'psnname': m.get('created_by__psnname'),
            'org_name': m.get('created_by__deptcode__org_name')
        }
        m.pop('created_by__psncode', None)
        m.pop('created_by__psnname', None)
        m.pop('created_by__deptcode__org_name', None)
        m['children'] = []
        tree_load[m['id']] = m
    for m in menus:
        if m['parent'] is root_menu:
            tree_data.append(m)
        if m['parent'] in tree_load:
            tree_load[m['parent']]['children'].append(m)

    without_empty_children_tree = [remove_empty_children(tree) for tree in tree_data]
    return without_empty_children_tree


def split_and_concat_last_three(input_string):
    parts = input_string.split('|')
    parts = [part for part in parts if part]
    # 获取最后三个部分
    last_three_parts = parts[-3:]
    result = '-'.join(last_three_parts)
    return result


def fetch_menu_permission_tree():
    """
    组装菜单+权限的多级树状结构
    """
    menus = []
    for menu in Menu.objects.values('id', 'name', 'parent', 'kind'):
        menus.append({
            'id': menu['id'],
            'name': menu['name'],
            'parent': menu['parent'],
            'category': 'menu'
        })
    permissions = []
    for conn in MenuConnPermission.objects.select_related().values('permission_id', 'permission__name', 'menu_id'):
        permissions.append({
            'id': conn['permission_id'],
            'name': conn['permission__name'],
            'parent': conn['menu_id'],
            'category': 'permission'
        })

    data = []
    data.extend(list(menus))
    data.extend(list(permissions))

    return fetch_tree(root_tag=None, queryset_values=data)


def fetch_department_tree_list(root_department=TECH_ROOT, deps=None):
    """
   root_department：所属部门(公司)的组织架构，1001『集团』
   deps：如果需要外界循环调用，建议外部传入deps
   """
    tree_load, tree_data = {}, []
    if deps is None:
        deps = Org.objects.filter(seal_status='N').values('id', 'org_code', 'org_name', 'parent_code', 'principal_code')
    for d in deps:
        d['children'] = []
        tree_load[d['org_code']] = d
    for d in deps:
        if d['parent_code'] == root_department:
            tree_data.append(d)
        elif d['parent_code'] in tree_load:
            tree_load[d['parent_code']]['children'].append(d)
    return tree_data


def fetch_department_tree():
    tree_list = fetch_department_tree_list()
    tree = tree_list[0] if tree_list else {}
    without_empty_children_tree = remove_empty_children(tree)
    return without_empty_children_tree


def fetch_department_user_tree():
    tree_load, tree_data = {}, []
    deps = Org.objects.filter(seal_status='N'). \
        annotate(code=F('org_code'), name=F('org_name'), parent=F('parent_code')). \
        values('id', 'code', 'name', 'parent')
    users = Employee.objects.filter(psnclscope=0). \
        annotate(parent=F('deptcode'), code=F('psncode'), name=F('psnname')). \
        values('id', 'code', 'name', 'parent')

    data = []
    data.extend(list(deps))
    data.extend(list(users))

    for d in data:
        d['code'] = str(d['code'])
        d['parent'] = str(d['parent'])
        d['children'] = []
        tree_load[d['code']] = d
    for d in data:
        if d['parent'] == TECH_ROOT:
            tree_data.append(d)
        elif d['parent'] in tree_load:
            tree_load[d['parent']]['children'].append(d)
    tree = tree_data[0] if tree_data else {}
    without_empty_children_tree = remove_empty_children(tree)
    return without_empty_children_tree


