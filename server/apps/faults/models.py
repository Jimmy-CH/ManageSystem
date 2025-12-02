from django.db import models
from decimal import Decimal
from django.db.models import JSONField


class CbaseModel(models.Model):
    """项目配置"""

    change_user = models.CharField(max_length=64, blank=True, null=True, verbose_name="修改人", default="admin")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True
        default_permissions = ("get", "add", "change", "delete")


class EventCategory(CbaseModel):
    """事件管理 事件分类"""
    name = models.CharField("分类名称", max_length=128, default="")
    active = models.SmallIntegerField("是否启用", choices=((1, "启用"), (2, "禁用")), default=1)
    parent = models.ForeignKey(to='self', verbose_name="父级分类", null=True, blank=True, db_index=True,
                               related_name='child_category', on_delete=models.SET_NULL)
    depth = models.SmallIntegerField("层级", default=1)

    class Meta:
        unique_together = (("name", "parent"),)
        ordering = ('-update_time',)
        db_table = "event_category"
        verbose_name = "事件分类"


class EventComponentInfo(CbaseModel):
    """事件管理 部件信息"""
    event_sub = models.ForeignKey(to=EventCategory, verbose_name="故障分类",  related_name='component_info',
                                  on_delete=models.SET_NULL, null=True, blank=True)
    component_sn = models.CharField("部件编码", max_length=50, blank=True, null=True)
    component_name = models.CharField("部件名", max_length=50, blank=True, null=True)
    component_brand = models.CharField("部件品牌", max_length=50, blank=True, null=True)
    component_model = models.CharField("部件型号", max_length=50, blank=True, null=True)
    component_specification = models.CharField("部件规格", max_length=32, blank=True, null=True)
    component_info = JSONField("部件json", blank=True, null=True)
    slot = models.CharField("槽位", max_length=500, blank=True, null=True)

    class Meta:
        db_table = "event_component_info"
        verbose_name = "部件信息"
        verbose_name_plural = verbose_name
        ordering = ('-update_time',)


class Event(CbaseModel):
    """事件管理 事件表"""
    EVENT_CHOICE = ((1, "故障单"), (2, "事故单"), (3, "其他"))
    EVENT_LEVEL_CHOICE = ((1, "轻微"), (2, "一般"), (3, "严重"), (4, "灾难"), (5, "无影响"))
    EVENT_STATUS_CHOICE = ((1, "开始"), (2, "挂起"), (3, "结束"), (4, "废弃"), (5, "历史"))
    OVERTIME_CHOICE = ((0, "不清楚"), (1, "超时"), (2, "未超时"))
    MAINTENANCE_TYPE_CHOICE = ((1, "厂商"), (2, "第三方"))
    EVENT_SOLUTION_TYPE = ((1, "自行处理"), (2, "服务商处理"), (0, "其它"))
    MAINTENANCE_STATUS_CHOICE = ((0, "未处理"), (1, "处理中"), (2, "已处理"))

    category = models.SmallIntegerField(choices=EVENT_CHOICE, default=1, verbose_name="类别", db_index=True)
    level = models.SmallIntegerField("故障等级", choices=EVENT_LEVEL_CHOICE, default=2, db_index=True)
    registrant = models.CharField("登记人", max_length=32, default="")
    handler = models.CharField("处理人", max_length=32, default="", null=True, blank=True)
    mal_id = models.CharField("故障id", max_length=32, unique=True)
    start_time = models.IntegerField("开始时间", db_index=True)
    end_time = models.IntegerField("结束时间", null=True)
    # 处理时间=结束时间-开始时间 所有场景保持一致，单位为分钟
    duration = models.IntegerField("处理时间", null=True, blank=True, default=0)
    mal_reason = models.CharField("故障原因", max_length=1024, default="")
    cause_department = JSONField("引起部门", null=True, blank=True)
    solution = models.CharField("解决方案", max_length=512, default="", null=True, blank=True)
    description = models.TextField("事故现象描述", default="", null=True, blank=True)
    mal_result = models.SmallIntegerField("当前状态", choices=EVENT_STATUS_CHOICE, default=1, db_index=True)
    reason = models.CharField("原因", max_length=512, default="", null=True, blank=True)
    key_endpoint = models.CharField("关键点", max_length=2000, null=True, blank=True)
    related_event = models.CharField("关联故障", max_length=32, default=None, null=True, blank=True)
    maintenance = models.CharField("维保商", max_length=32, default="", null=True, blank=True)
    maintenance_type = models.SmallIntegerField("维保商类型", choices=MAINTENANCE_TYPE_CHOICE, default=1)
    impact_pro = JSONField("影响项目", blank=True, null=True)
    maintenance_remarks = JSONField("分包商评分", blank=True, null=True)
    first_level = models.CharField("一级分类", max_length=128, default="默认", null=True, blank=True)
    subdivision = models.CharField("二级分类", max_length=128, default="默认", null=True, blank=True)
    third_level = models.CharField("三级分类", max_length=128, default="默认", null=True, blank=True)
    fourth_level = models.CharField("四级分类", max_length=128, default="默认", null=True, blank=True)
    is_overtime = models.SmallIntegerField("是否超时时间", choices=OVERTIME_CHOICE, default=0, null=True, blank=True)
    child_event = models.CharField("子事件", max_length=32, default="", null=True, blank=True)
    score = models.IntegerField("维保商评分", default=0, null=True, blank=True)
    maintenance_duration = models.IntegerField("维保商处理时间", default=0, null=True, blank=True)
    maintenance_status = models.SmallIntegerField("维保商处理状态", choices=MAINTENANCE_STATUS_CHOICE, default=-1,
                                                  null=True, blank=True)
    solution_type = models.SmallIntegerField("解决方式", choices=EVENT_SOLUTION_TYPE, default=0, null=True, blank=True)
    document_id = models.CharField("知识库id", max_length=128, null=True, blank=True)

    class Meta:
        db_table = "event"
        verbose_name = "事件表"
        verbose_name_plural = verbose_name
        ordering = ('-update_time',)


class EventDeviceInfo(models.Model):
    """事件管理 设备信息"""

    event = models.ForeignKey(to=Event, verbose_name="故障记录", related_name='device_info', on_delete=models.CASCADE)
    equipment_ip = models.CharField("设备IP", max_length=128, null=False, db_index=True)
    equipment_sn = models.CharField("设备SN", max_length=128, null=False, db_index=True)
    machine_info = models.CharField("机器信息", max_length=128, null=False)     # 服务器信息
    rack_location = models.CharField("机架位置", max_length=128, null=False)
    # 共有信息
    brand = models.CharField("设备品牌", max_length=128, null=False)
    device_model = models.CharField("设备型号", max_length=128, null=False)
    # IDC 信息
    device_location = models.CharField("设备位置", max_length=128, null=False)  # IDC
    device_name = models.CharField("设备名称", max_length=128, null=False)
    # component = models.ForeignKey(to=EventComponentInfo, verbose_name="部件信息", null=True, blank=True)
    component_name = models.CharField("部件名称", max_length=128, null=False)
    component_brand = models.CharField("部件品牌", max_length=128, null=False)
    # 部件规格改为部件型号 字段名称暂时不变以兼容旧接口 component_specification对应部件表的component_model
    component_specification = models.CharField("部件规格", max_length=512, null=False)
    slot = models.CharField("槽位", max_length=128, null=False)
    notes = models.TextField("备注", blank=True, null=True)

    class Meta:
        db_table = "event_device_info"
        verbose_name = "设备信息"
        verbose_name_plural = verbose_name


class EventHandleProcess(models.Model):
    """故障处理过程"""
    event = models.ForeignKey(to=Event, verbose_name="故障记录", related_name='event_handle_process',
                              on_delete=models.CASCADE)
    handle_process = models.TextField("处理过程", default="")

    class Meta:
        db_table = "event_handle_process"
        verbose_name = "故障处理过程"
        verbose_name_plural = verbose_name


class EventTimeEffective(CbaseModel):
    """时效控制 标准时效"""
    category = models.SmallIntegerField(choices=Event.EVENT_CHOICE, default=1, verbose_name="类别")
    first_level = models.CharField("一级分类，组名", max_length=32)
    second_level = models.CharField("二级分类", max_length=32)
    third_level = models.CharField("三级分类", max_length=32, default="")
    fourth_level = models.CharField("四级分类", max_length=32, default="")
    level = models.SmallIntegerField("故障等级", choices=Event.EVENT_LEVEL_CHOICE, default=2)
    standard = models.DecimalField("标准失效", max_digits=10, decimal_places=2, default=Decimal('0.00'),
                                   null=True, blank=True)

    class Meta:
        db_table = "event_time_effective"
        verbose_name = "标准时效"
        verbose_name_plural = verbose_name
        ordering = ('-update_time',)
        unique_together = (("category", "first_level", "second_level", "fourth_level", "level", "standard"),)


class EventTimeSpecial(CbaseModel):
    """时效控制 特殊时效"""
    component_name = models.CharField("部件名", max_length=50, blank=True, null=True)
    component_brand = models.CharField("部件品牌", max_length=50, blank=True, null=True)
    component_model = models.CharField("部件型号", max_length=50, blank=True, null=True)
    standard = models.DecimalField("标准时效", max_digits=10, decimal_places=2, default=Decimal('0.00'),
                                   null=True, blank=True)

    class Meta:
        db_table = "event_time_special"
        verbose_name = "特殊时效"
        verbose_name_plural = verbose_name
        ordering = ('-update_time',)


