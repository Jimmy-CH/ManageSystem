# 事件优先级
PRIORITY_CHOICES = [
    (1, '低'),
    (2, '中'),
    (3, '高'),
    (4, '紧急'),
]

# 故障状态
FAULT_STATUS_CHOICES = [
    (0, '未处理'),
    (1, '处理中'),
    (2, '已解决'),
    (3, '已关闭'),
    (4, '无效'),
]

# 事件来源
SOURCE_CHOICES = [
    (1, '用户上报'),
    (2, '监控告警'),
    (3, '巡检发现'),
    (4, '自动检测'),
]

LEVEL_CHOICES = (
    (1, "一级分类"),
    (2, "二级分类"),
    (3, "三级分类"),
    (4, "四级分类")
)

# 权限
INCIDENT_PERMISSIONS = [
    ('view_incident', '查看事件'),
    ('add_incident', '创建事件'),
    ('change_incident', '修改事件'),
    ('delete_incident', '删除事件'),
    ('respond_incident', '响应事件'),
    ('resolve_incident', '解决事件'),
    ('export_incident', '导出事件'),
    ('view_statistics', '查看统计'),
]
