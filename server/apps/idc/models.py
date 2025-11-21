
from django.db import models
from apps.users.models import User


class DataCenter(models.Model):
    LEVEL_CHOICES = [
        ('A', 'A级'),
        ('B', 'B级'),
        ('C', 'C级')
    ]
    name = models.CharField("机房名称", max_length=100, unique=True)
    address = models.CharField("地址", max_length=255)
    contact = models.CharField("联系人", max_length=50, blank=True)
    phone = models.CharField("联系电话", max_length=20, blank=True)
    level = models.CharField("等级", max_length=10, choices=LEVEL_CHOICES, default='B')
    is_active = models.BooleanField("启用", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "机房"
        verbose_name_plural = "机房"


class Rack(models.Model):
    data_center = models.ForeignKey(DataCenter, on_delete=models.CASCADE, verbose_name="所属机房")
    name = models.CharField("机柜编号", max_length=50)
    height = models.PositiveSmallIntegerField("高度(U)", default=42)
    power_load = models.FloatField("额定功率(kW)", default=5.0)
    location = models.CharField("位置描述", max_length=100, blank=True)
    is_full = models.BooleanField("已满", default=False)

    def __str__(self):
        return f"{self.data_center.name}-{self.name}"

    class Meta:
        verbose_name = "机柜"
        verbose_name_plural = "机柜"
        unique_together = ('data_center', 'name')


class Device(models.Model):
    DEVICE_TYPES = [
        ('server', '服务器'),
        ('switch', '交换机'),
        ('firewall', '防火墙'),
        ('storage', '存储设备'),
    ]
    STATUS_CHOICES = [
        ('online', '在线'),
        ('offline', '离线'),
        ('maintenance', '维护中'),
        ('decommissioned', '已下架')
    ]
    asset_tag = models.CharField("资产编号", max_length=100, unique=True)
    name = models.CharField("设备名称", max_length=100)
    device_type = models.CharField("类型", max_length=20, choices=DEVICE_TYPES)
    model = models.CharField("型号", max_length=100)
    vendor = models.CharField("厂商", max_length=100)
    serial_number = models.CharField("序列号", max_length=100, unique=True)
    rack = models.ForeignKey(Rack, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="所在机柜")
    position_u = models.PositiveSmallIntegerField("U位起始", null=True, blank=True)
    height_u = models.PositiveSmallIntegerField("占用U数", default=1)
    ip_address = models.GenericIPAddressField("管理IP", null=True, blank=True)
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default='online')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="负责人")
    purchase_date = models.DateField("采购日期", null=True, blank=True)
    warranty_expire = models.DateField("保修到期", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "设备"
        verbose_name_plural = "设备"


class IPAddress(models.Model):
    ip = models.GenericIPAddressField("IP地址", unique=True)
    subnet_mask = models.CharField("子网掩码", max_length=15, default="255.255.255.0")
    vlan = models.CharField("VLAN", max_length=10, blank=True)
    gateway = models.GenericIPAddressField("网关", null=True, blank=True)
    is_used = models.BooleanField("已分配", default=False)
    device = models.OneToOneField(Device, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="绑定设备")
    description = models.CharField("描述", max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ip

    class Meta:
        verbose_name = "IP地址"
        verbose_name_plural = "IP地址"


class WorkOrder(models.Model):
    ORDER_TYPES = [
        ('install', '上架'),
        ('remove', '下架'),
        ('repair', '维修'),
        ('inspect', '巡检'),
    ]
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('in_progress', '处理中'),
        ('completed', '已完成'),
        ('cancelled', '已取消')
    ]
    title = models.CharField("工单标题", max_length=100)
    order_type = models.CharField("类型", max_length=20, choices=ORDER_TYPES)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name="关联设备")
    requester = models.ForeignKey(User, related_name='requested_orders', on_delete=models.CASCADE, verbose_name="申请人")
    assignee = models.ForeignKey(User, related_name='assigned_orders', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="处理人")
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField("详细说明", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "工单"
        verbose_name_plural = "工单"
