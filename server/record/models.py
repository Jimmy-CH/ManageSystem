from django.db import models
from common.base_model import BaseModel
from utils.encrypted_field import EncryptedCharField


class OAInfo(models.Model):
    """
    OA信息模型
    """
    applicant = models.CharField(verbose_name="申请人员姓名", blank=True, null=True, max_length=50)
    apply_enter_time = models.DateTimeField(verbose_name="申请进入日期时间", null=True, blank=True)
    apply_leave_time = models.DateTimeField(verbose_name="申请离开日期时间", null=True, blank=True)
    apply_count = models.PositiveSmallIntegerField(verbose_name="申请进入人数", default=1, help_text="可手动修改")
    connected_count = models.PositiveSmallIntegerField(verbose_name="已关联人数", default=0, help_text="可手动修改")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="同步数据时间")
    is_post_entry = models.BooleanField(verbose_name="是否为后补流程", default=True, help_text="True表示为后补流程")
    oa_link = models.CharField(verbose_name="关联OA流程", max_length=256, blank=True, null=True,
                               help_text="补流程时填写OA申请链接")

    class Meta:
        verbose_name = "OA信息"
        verbose_name_plural = "OA信息"
        ordering = ['-id']
        db_table = 'record_oa_info'


class OAPerson(models.Model):
    """
    OA人员信息模型
    """
    name = models.CharField(verbose_name="人员姓名", blank=True, null=True, max_length=50)
    phone_number = EncryptedCharField(verbose_name="电话号码", max_length=200, null=True, blank=True,
                                      help_text="请输入电话号码")
    person_type = models.SmallIntegerField(verbose_name="人员类型", default=1, help_text="根据单位自动判断内外部人员",
                                           choices=((1, "内部"), (2, "外部")))
    id_type = models.SmallIntegerField(verbose_name="证件类型", default=1, help_text="工牌或身份证等",
                                       choices=((1, "工牌"), (2, "身份证"), (3, "驾驶证"), (4, "护照")))
    id_number = EncryptedCharField(verbose_name="证件号码", max_length=200, help_text="工牌号或身份证号等")
    unit = models.CharField(verbose_name="人员单位", max_length=100, null=True, blank=True,
                            help_text="来自OA申请单位，支持选择蛟龙集团单位或手动输入外部单位")
    department = models.CharField(verbose_name="人员部门", max_length=100, null=True, blank=True,
                                  help_text="来自OA申请部门，支持选择内部部门或手动输入外部部门")
    is_linked = models.BooleanField(verbose_name="是否关联星辰", default=False, help_text="需要用户手动关联星辰")

    oa_info = models.ForeignKey(
        OAInfo,
        on_delete=models.CASCADE,    # 级联删除：删除 OAInfo 时，其所有关联的 OAPerson 也会被删除
        related_name='persons',      # 反向查询用：oa_info.persons.all()
        verbose_name="所属OA申请",
        help_text="该人员所属的OA审批记录"
    )

    class Meta:
        verbose_name = "OA人员信息"
        verbose_name_plural = "OA人员信息"
        db_table = 'record_oa_person'


class ProcessRecord(BaseModel):
    """
    机房人员进出登记记录模型
    支持常规（OA同步）和紧急（手动添加）两种方式
    """
    PERSON_TYPE_CHOICES = ((1, "内部"), (2, "外部"))
    ID_TYPE_CHOICES = ((0, "未质押"), (1, "工牌"), (2, "身份证"), (3, "驾驶证"), (4, "护照"))
    STATUS_CHOICES = ((1, "未入场"), (2, "已入场"), (3, "已离场"), (4, "已废止"))
    CARD_STATUS_CHOICES = ((1, "无需发卡"), (2, "已发卡"), (3, "已归还"), (4, "未归还"))
    PLEDGED_STATUS_CHOICES = ((1, "未质押"), (2, "已质押"), (3, "已归还"), (4, "未归还"))
    CARD_TYPE_CHOICES = ((1, "卡1"), (2, "卡2"), (3, "卡3"), (4, "卡4"), (5, "卡5"))

    applicant = models.CharField(verbose_name="申请人", blank=True, null=True, max_length=50)
    name = models.CharField(verbose_name="人员姓名", blank=True, null=True, max_length=50)
    phone_number = EncryptedCharField(verbose_name="电话号码", max_length=200, null=True, blank=True,
                                      help_text="请输入电话号码")
    person_type = models.SmallIntegerField(verbose_name="人员类型", default=1, help_text="根据证件类型自动判断内外部人员",
                                           choices=PERSON_TYPE_CHOICES)
    id_type = models.SmallIntegerField(verbose_name="证件类型", default=0, help_text="工牌或身份证等", choices=ID_TYPE_CHOICES)
    id_number = EncryptedCharField(verbose_name="证件号码", max_length=200, null=True, blank=True, help_text="工牌号或身份证号等")
    unit = models.CharField(verbose_name="人员单位", max_length=100, null=True, blank=True,
                            help_text="来自OA申请单位，支持选择蛟龙集团单位或手动输入外部单位")
    department = models.CharField(verbose_name="人员部门", max_length=100, null=True, blank=True,
                                  help_text="来自OA申请部门，支持选择内部部门或手动输入外部部门")
    status = models.SmallIntegerField("登记状态", choices=STATUS_CHOICES, default=1, db_index=False)
    apply_enter_time = models.DateTimeField(verbose_name="申请进入日期时间", null=True, blank=True,
                                            help_text="由OA审批流程自动带出，不可编辑")
    apply_leave_time = models.DateTimeField(verbose_name="申请离开日期时间", null=True, blank=True,
                                            help_text="由OA审批流程自动带出，不可编辑")
    entered_time = models.DateTimeField(verbose_name="实际进入时间", blank=True, null=True, help_text="点击“已进入”时自动填充")
    exited_time = models.DateTimeField(verbose_name="实际离开时间", blank=True, null=True, help_text="点击“已离开”时自动填充")
    enter_count = models.PositiveSmallIntegerField(verbose_name="实际进出次数", default=1, help_text="可手动修改")
    companion = models.CharField(verbose_name="陪同人", max_length=128, default="无", help_text="可填写具体姓名或“无”")
    reason = models.TextField(verbose_name="进入原因", blank=True, null=True, help_text="自动带出OA申请中的进入原因")
    carried_items = models.TextField(verbose_name="携带物品", blank=True, null=True, help_text="自动带出OA申请中的携带物品")
    card_status = models.SmallIntegerField("门禁卡状态", choices=CARD_STATUS_CHOICES, default=1, db_index=False)
    card_type = models.SmallIntegerField("门禁卡类型", choices=CARD_TYPE_CHOICES, default=1, db_index=False)
    pledged_status = models.SmallIntegerField("证件质押状态", choices=PLEDGED_STATUS_CHOICES, default=1, db_index=False)
    remarks = models.TextField(verbose_name="备注", blank=True, null=True, help_text="异常情况说明：超时、损坏、脏乱差、补流程等")
    oa_link = models.CharField(verbose_name="关联OA流程", max_length=256, blank=True, null=True, help_text="补流程时填写OA申请链接")
    is_emergency = models.BooleanField(verbose_name="是否为紧急进出", default=False, help_text="True表示手动添加的紧急记录")
    is_normal = models.BooleanField(verbose_name="是否为正常进出", default=True, help_text="True表示正常进出记录")
    is_linked = models.BooleanField(verbose_name="是否关联OA", default=True, help_text="紧急情况下选择False")
    create_user = models.CharField(max_length=64, blank=True, null=True, verbose_name="创建人姓名", default="admin")
    update_user = models.CharField(max_length=10, blank=True, null=True, verbose_name="修改人姓名", default="admin")

    class Meta:
        verbose_name = "人员进出记录"
        verbose_name_plural = "人员进出记录"
        ordering = ['-created_at']
        db_table = 'record_process_record'
        indexes = [
            models.Index(fields=['entered_time', 'status']),
            models.Index(fields=['unit']),
        ]


class EntryLog(models.Model):
    """
    进机房人员进出记录模型
    """
    process_record = models.ForeignKey(
        ProcessRecord,              # 关联的模型
        on_delete=models.CASCADE,   # 级联删除：当登记记录被删除，其所有进出日志也删除
        related_name='entry_logs',  # 反向查询用：process_record.entry_logs.all()
        verbose_name="关联的登记记录"
    )
    entered_time = models.DateTimeField(
        verbose_name="实际进入时间",
        blank=True,
        null=True,
        help_text="点击“已进入”时自动填充"
    )
    exited_time = models.DateTimeField(
        verbose_name="实际离开时间",
        blank=True,
        null=True,
        help_text="点击“已离开”时自动填充"
    )
    create_user = models.CharField(max_length=64, blank=True, null=True, verbose_name="创建人姓名", default="admin")
    update_user = models.CharField(max_length=10, blank=True, null=True, verbose_name="修改人姓名", default="admin")
    card_status = models.SmallIntegerField("门禁卡状态", choices=((1, "无需发卡"), (2, "已发卡"), (3, "已归还"), (4, "未归还")),
                                           default=1, db_index=False)
    card_type = models.SmallIntegerField("门禁卡类型", choices=((1, "卡1"), (2, "卡2"), (3, "卡3"), (4, "卡4"), (5, "卡5")),
                                         default=1, db_index=False)
    pledged_status = models.SmallIntegerField("证件质押状态", choices=((1, "未质押"), (2, "已质押"), (3, "已归还"), (4, "未归还")),
                                              default=1, db_index=False)
    id_type = models.SmallIntegerField(verbose_name="证件类型", default=0, help_text="工牌或身份证等",
                                       choices=((0, "未质押"), (1, "工牌"), (2, "身份证"), (3, "驾驶证"), (4, "护照")))
    remarks = models.TextField(verbose_name="备注", blank=True, null=True,
                               help_text="异常情况说明：超时、损坏、脏乱差、补流程等")
    is_normal = models.BooleanField(verbose_name="是否为正常进出", default=True, help_text="True表示正常进出记录")

    class Meta:
        verbose_name = "进出日志"
        verbose_name_plural = "进出日志"
        db_table = 'record_entry_log'
        indexes = [
            models.Index(fields=['entered_time']),    # 按进出时间查询
            models.Index(fields=['process_record']),  # 按登记记录查询
        ]

