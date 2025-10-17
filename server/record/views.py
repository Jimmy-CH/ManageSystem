import json
import pytz
import datetime
import pandas as pd
from django.views import View
from django.conf import settings
from django.http import HttpResponse
from rest_framework import viewsets

from common.pagination import StandardResultsSetPagination
from utils.cipher import AESCipher
from .models import ProcessRecord, EntryLog, OAInfo, OAPerson
from .serializers import ProcessRecordSerializer, EntryLogSerializer, OAInfoSerializer, OAPersonSerializer, \
    ProcessRecordBatchRegisterSerializer
from .filters import ProcessRecordFilter, OAInfoFilter, OAPersonFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.db.models import Count, Q
from utils.date_transform import get_date_range
from django.db import transaction


class ProcessRecordViewSet(viewsets.ModelViewSet):
    queryset = ProcessRecord.objects.all()
    serializer_class = ProcessRecordSerializer
    filterset_class = ProcessRecordFilter
    pagination_class = StandardResultsSetPagination
    ordering_fields = ['create_time', 'entered_time', 'exited_time']
    search_fields = ['person_name', 'unit', 'department', 'reason']

    def get_serializer_class(self):
        if self.action == 'register':
            return ProcessRecordBatchRegisterSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        """
        批量手动登记多人进出记录（紧急登记）
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            created_records = serializer.save()
            return Response({
                "message": f"成功登记 {len(created_records)} 人"
            }, status=status.HTTP_201_CREATED)
        return Response({
            "error": "数据校验失败",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        # 获取东八区时区
        shanghai_tz = pytz.timezone('Asia/Shanghai')

        data = []
        for record in queryset:
            def localize_dt(dt):
                """将带时区的 datetime 转为东八区 naive 时间；若为 None 则返回 None"""
                if dt is None:
                    return None
                if timezone.is_aware(dt):
                    # 转换为东八区时间，然后移除时区信息
                    return dt.astimezone(shanghai_tz).replace(tzinfo=None)
                return dt

            data.append({
                "申请人": record.applicant,
                "人员姓名": record.person_name,
                "电话号码": record.phone_number,
                "人员类型": dict(ProcessRecord.PERSON_TYPE_CHOICES).get(record.person_type, record.person_type),
                "证件类型": dict(ProcessRecord.ID_TYPE_CHOICES).get(record.id_type, record.id_type),
                "证件号码": record.id_number,
                "人员单位": record.unit,
                "人员部门": record.department,
                "登记状态": dict(ProcessRecord.STATUS_CHOICES).get(record.registration_status,
                                                                   record.registration_status),
                "申请进入时间": localize_dt(record.apply_enter_time),
                "申请离开时间": localize_dt(record.apply_leave_time),
                "实际进入时间": localize_dt(record.entered_time),
                "实际离开时间": localize_dt(record.exited_time),
                "进出次数": record.enter_count,
                "陪同人": record.companion,
                "进入原因": record.reason,
                "携带物品": record.carried_items,
                "门禁卡状态": dict(ProcessRecord.CARD_STATUS_CHOICES).get(record.card_status, record.card_status),
                "门禁卡类型": dict(ProcessRecord.CARD_TYPE_CHOICES).get(record.card_type, record.card_type),
                "证件质押状态": dict(ProcessRecord.PLEDGED_STATUS_CHOICES).get(record.pledged_status,
                                                                               record.pledged_status),
                "备注": record.remarks,
                "关联OA流程": record.oa_link,
                "是否紧急": "是" if record.is_emergency else "否",
                "是否正常": "是" if record.is_normal else "否",
                "是否关联OA": "是" if record.is_linked else "否",
                "创建时间": localize_dt(record.create_time),
            })

        df = pd.DataFrame(data)

        today = datetime.datetime.now().strftime("%Y%m%d")
        filename = f"process_records_export_{today}.xlsx"

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='人员进出记录')

        return response

    @action(detail=True, methods=['post'], url_path='enter')
    def enter(self, request, pk=None):
        """
        多次入场登记 - 每次调用新增一条 EntryLog
        """
        record = get_object_or_404(ProcessRecord, pk=pk)

        data = request.data

        companion = data.get('companion', '无')
        card_status = int(data.get('card_status', 1))
        card_type = int(data.get('card_type', 1)) if card_status == 2 else 1
        pledged_status = int(data.get('pledged_status', 1))
        id_type = int(data.get('id_type', 0)) if pledged_status == 2 else 0

        # 创建新的 EntryLog（不更新旧的）
        entry_log = EntryLog.objects.create(
            process_record=record,
            entered_time=timezone.now(),
            create_time=timezone.now(),
            create_user_name=request.user.username or 'admin',
            card_status=card_status,
            card_type=card_type,
            pledged_status=pledged_status,
            id_type=id_type,
            remarks="",
            companion=companion,
            operation="入场"
        )

        # 更新主记录为“已入场”，并更新 entered_time 为最新
        record.registration_status = 2
        record.entered_time = entry_log.entered_time
        record.companion = companion
        record.card_status = card_status
        record.card_type = card_type
        record.pledged_status = pledged_status
        record.id_type = id_type
        record.save()

        return Response({
            "code": 200,
            "msg": "入场登记成功",
            "data": {
                "entry_log_id": entry_log.id,
                "entered_time": entry_log.entered_time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='exit')
    def exit(self, request, pk=None):
        """
        多次离场登记 - 更新最近一条未离场的 EntryLog
        """
        record = get_object_or_404(ProcessRecord, pk=pk)

        data = request.data

        exit_condition = data.get('exit_condition', 'normal')
        remarks = data.get('remarks', '').strip()

        if exit_condition == "abnormal" and not remarks:
            return Response({
                "code": 400,
                "msg": "异常离场必须填写备注"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 查找该登记记录下，最近一条 entered_time 最大 且 exited_time 为空 的日志
        latest_entry = EntryLog.objects.filter(
            process_record=record,
            exited_time__isnull=True
        ).order_by('-entered_time').first()

        if not latest_entry:
            return Response({
                "code": 400,
                "msg": "没有找到未离场的进入记录，请先执行进入登记"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 校验门禁卡状态
        new_card_status = int(data.get('card_status', latest_entry.card_status))
        if latest_entry.card_status == 1 and new_card_status not in [1, 3]:
            return Response({
                "code": 400,
                "msg": "入场时无需发卡，离场卡状态只能是【无需发卡】或【已归还】"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 校验证件质押状态
        new_pledged_status = int(data.get('pledged_status', latest_entry.pledged_status))
        if latest_entry.pledged_status == 1 and new_pledged_status not in [1, 3]:
            return Response({
                "code": 400,
                "msg": "入场时未质押，离场质押状态只能是【未质押】或【已归还】"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 创建离开日志
        entry_log = EntryLog.objects.create(
            process_record=record,
            exited_time=timezone.now(),
            create_time=timezone.now(),
            create_user_name=request.user.username or 'admin',
            card_status=new_card_status,
            card_type=latest_entry.card_type,
            pledged_status=new_pledged_status,
            id_type=latest_entry.id_type,
            remarks=remarks,
            companion=latest_entry.companion,
            is_normal=True if exit_condition == 'normal' else False,
            operation="离场"
        )

        # 更新主记录为“已离场”，并更新 exited_time 为最新
        if entry_log.is_normal:
            record.registration_status = 3
            record.exited_time = entry_log.exited_time
            record.card_status = new_card_status if record.card_status != 1 else 1
            record.pledged_status = new_pledged_status if record.pledged_status != 1 else 1
            record.remarks = remarks
            record.save()
        else:
            # 有异常进出日志 则记为异常
            record.registration_status = 3
            record.exited_time = entry_log.exited_time
            record.card_status = new_card_status if record.card_status != 1 else 1
            record.pledged_status = new_pledged_status if record.pledged_status != 1 else 1
            record.is_normal = False
            record.remarks = remarks
            record.save()

        return Response({
            "code": 200,
            "msg": "离场登记成功",
            "data": {
                "entry_log_id": entry_log.id,
                "exited_time": entry_log.exited_time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='logs')
    def logs(self, request, pk=None):
        """
        查询该登记记录的所有进出日志（倒序）
        """
        record = get_object_or_404(ProcessRecord, pk=pk)

        logs = EntryLog.objects.filter(
            process_record=record
        ).order_by('-create_time', '-id')

        result = EntryLogSerializer(logs, many=True).data

        return Response({
            "code": 200,
            "data": result
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='link')
    def link(self, request, pk=None):
        record = get_object_or_404(ProcessRecord, pk=pk)
        data = request.data

        oa_info_id = data.get('oa_info_id')
        # 校验必要字段
        if not oa_info_id:
            return Response({"error": "oa_info_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            oa_info = OAInfo.objects.get(id=oa_info_id)
        except OAInfo.DoesNotExist:
            return Response({"error": "OAInfo not found"}, status=status.HTTP_404_NOT_FOUND)

        # 使用事务确保一致性
        with transaction.atomic():
            # 更新 ProcessRecord
            record.change_user_name = request.user.username or 'admin'
            record.oa_link = oa_info.oa_link
            record.is_linked = True
            record.applicant = oa_info.applicant
            record.applicant_time = oa_info.applicant_time
            record.save()

            # 更新 OAInfo
            oa_info.connected_count += 1
            oa_info.is_linked = True if oa_info.connected_count >= oa_info.apply_count else False
            oa_info.save()

        return Response({
            "msg": "关联OA成功",
        }, status=status.HTTP_200_OK)


def timestamp_ms_to_datetime(ts_ms):
    """将毫秒级时间戳转为无时区的 naive datetime（USE_TZ=False 时使用）"""
    if not ts_ms:
        return None
    return datetime.datetime.fromtimestamp(ts_ms / 1000)


class EntryLogViewSet(viewsets.ModelViewSet):
    queryset = EntryLog.objects.all()
    serializer_class = EntryLogSerializer

    def get_queryset(self):
        return EntryLog.objects.filter(process_record__isnull=False)


class OAInfoViewSet(viewsets.ModelViewSet):
    # queryset = OAInfo.objects.prefetch_related('persons').filter(is_linked=False)
    queryset = OAInfo.objects.filter(is_linked=False)
    serializer_class = OAInfoSerializer
    filterset_class = OAInfoFilter
    pagination_class = StandardResultsSetPagination
    ordering_fields = ['id', 'create_time', 'apply_enter_time']
    search_fields = ['applicant', 'oa_link_info']


class OAPersonViewSet(viewsets.ModelViewSet):
    queryset = OAPerson.objects.select_related('oa_info').filter(is_linked=False)
    serializer_class = OAPersonSerializer
    filterset_class = OAPersonFilter
    ordering_fields = ['id', 'person_name']
    search_fields = ['person_name', 'unit', 'department']


class SubmitEntryApplicationView(View):
    """
    人员或设备进出数据中心机房申请接口
    根据 fd_3e52febf30855e 判断是否为后补流程，分别存入 OAInfo 或 ProcessRecord
    """

    def post(self, request):
        try:
            result = json.loads(request.body)
            plain_text = result.get('data')
            oa_secret = settings.OA_SECRET_KEY
            aes = AESCipher(oa_secret)
            data = aes.decrypt_base64(plain_text)
        except Exception as e:
            print(f"OA推送数据解析失败：{e}")
            return HttpResponse('fail')
        print(f'OA推送数据：{data}')
        try:
            # 从顶层取 form 字段（数据结构是 {'number': ..., 'form': {...}}）
            form_data = data.get('form', {})
            process_id = data.get('processId', '')
            # 获取是否后补字段（在 form 内）
            is_post_entry_str = form_data.get("fd_3e52febf30855e", {}).get("value", "0")
            is_post_entry = is_post_entry_str == "0"
            applicant_name = form_data.get("fd_3492b1ce199d78", {}).get("value", "")
            applicant_code = form_data.get("fd_3492b1bc24dec8", {}).get("value", "")
            applicant_unit = form_data.get("fd_34a3f0e5cb22b6", {}).get("value", "")
            applicant = f'{applicant_name}({applicant_code})'
            applicant_time = timestamp_ms_to_datetime(form_data.get("fd_3492b1dca12354", {}).get("value"))
            oa_link = f'{settings.OA_BASE_URL}{process_id}'
            oa_link_info = f'{applicant_unit}{applicant_name}的人员或设备进出圆通数据中心机房申请'
            if is_post_entry:
                # ========== 后补流程：存入 OAInfo + OAPerson ==========
                oa_info = OAInfo.objects.create(
                    applicant=applicant[0] if isinstance(applicant, tuple) else applicant,
                    apply_enter_time=timestamp_ms_to_datetime(form_data.get("fd_3b8333606a75b2", {}).get("value")),
                    apply_leave_time=timestamp_ms_to_datetime(form_data.get("fd_3b83336261114c", {}).get("value")),
                    apply_count=int(form_data.get("fd_3b8333adc9bac8", {}).get("value", 1)),  # 供应商人数
                    connected_count=0,
                    is_post_entry=True,
                    oa_link=oa_link,
                    create_time=timezone.now(),
                    oa_link_info=oa_link_info,
                    applicant_time=applicant_time
                )

                # 处理明细表1：人员信息
                person_list = form_data.get("fd_3586e01ffb8ada", {}).get("value", [])
                for p in person_list:

                    id_type_map = {"工牌": 1, "身份证": 2, "驾驶证": 3, "护照": 4}
                    id_type_str = p.get("fd_3e5302cbb15384", {}).get("value", "工牌")
                    id_type = id_type_map.get(id_type_str, 1)

                    unit = p.get("fd_3e53011e4a1d6a", {}).get("value", "")
                    # 人员类型根据工牌判断
                    person_type = 1 if id_type == 1 else 2

                    # 工号优先，非工号备用
                    id_number = p.get("fd_3b833bb674cdae", {}).get("value") or p.get("fd_3e5338ea59258c", {}).get("value", "")

                    OAPerson.objects.create(
                        oa_info=oa_info,
                        person_name=p.get("fd_3b833bb44fff40", {}).get("value", "")[:50],
                        phone_number=p.get("fd_3b833bb7abbb8c", {}).get("value", ""),
                        person_type=person_type,
                        id_type=id_type,
                        id_number=id_number,
                        unit=unit,
                        department=p.get("fd_3e53011edca3fe", {}).get("value", "")
                    )

                print("保存OAInfo成功")
                return HttpResponse("ok")

            else:
                # ========== 正常流程：存入 ProcessRecord（每人一条记录） ==========
                enter_time = timestamp_ms_to_datetime(form_data.get("fd_3b8333606a75b2", {}).get("value"))
                leave_time = timestamp_ms_to_datetime(form_data.get("fd_3b83336261114c", {}).get("value"))
                reason = form_data.get("fd_3b8333af8ffb8a", {}).get("value", "")
                carried_items = form_data.get("fd_3b8333b5b1c66c", {}).get("value", "")
                companion = "无"

                person_list = form_data.get("fd_3586e01ffb8ada", {}).get("value", [])
                created_records = []

                for p in person_list:
                    # 证件类型映射
                    id_type_map = {"工牌": 1, "身份证": 2, "驾驶证": 3, "护照": 4}
                    id_type_str = p.get("fd_3e5302cbb15384", {}).get("value", "工牌")
                    id_type = id_type_map.get(id_type_str, 1)

                    unit = p.get("fd_3e53011e4a1d6a", {}).get("value", "")
                    # 人员类型根据工牌判断
                    person_type = 1 if id_type == 1 else 2

                    # 工号优先，非工号备用
                    id_number = p.get("fd_3b833bb674cdae", {}).get("value") or p.get("fd_3e5338ea59258c", {}).get("value", "")

                    record = ProcessRecord.objects.create(
                        applicant=applicant[0] if isinstance(applicant, tuple) else applicant,
                        person_name=p.get("fd_3b833bb44fff40", {}).get("value", "")[:50],
                        phone_number=p.get("fd_3b833bb7abbb8c", {}).get("value", ""),
                        person_type=person_type,
                        id_type=id_type,
                        id_number=id_number,
                        unit=unit,
                        department=p.get("fd_3e53011edca3fe", {}).get("value", ""),
                        registration_status=1,  # 未入场
                        apply_enter_time=enter_time,
                        apply_leave_time=leave_time,
                        entered_time=None,
                        exited_time=None,
                        enter_count=1,
                        companion=companion,
                        reason=reason,
                        carried_items=carried_items,
                        card_status=1,  # 无需发卡
                        card_type=1,
                        pledged_status=1,  # 未质押
                        remarks="",
                        oa_link=oa_link,
                        is_emergency=False,
                        is_normal=True,
                        create_time=timezone.now(),
                        update_time=timezone.now(),
                        oa_link_info=oa_link_info,
                        applicant_time=applicant_time
                    )
                    created_records.append(record.id)

                print("保存ProcessRecord成功")
                return HttpResponse("ok")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"OA数据解析失败: {str(e)}")
            return HttpResponse("fail")


class SummaryCardsView(APIView):
    """
    获取汇总卡片数据：总人数、总次数（基于EntryLog）、单位正常占比、环比
    支持 this_week / last_week / this_month / last_month / this_year / custom 的环比
    """
    def get(self, request):
        period = request.GET.get('period', 'this_month')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        start, end = get_date_range(period, start_date, end_date)

        # 当前周期数据
        current_process_records = ProcessRecord.objects.filter(
            entered_time__gte=start,
            entered_time__lte=end,
            registration_status__in=[2, 3]  # 已入场、已离场
        )

        total_people = current_process_records.values('person_name', 'phone_number').distinct().count()
        total_entries = EntryLog.objects.filter(
            process_record__in=current_process_records,
            entered_time__isnull=False
        ).count()
        normal_count = current_process_records.filter(is_normal=True).count()
        total_process_count = current_process_records.count()
        normal_ratio = round((normal_count / total_process_count * 100), 2) if total_process_count > 0 else 0
        total_unit = current_process_records.values('unit').distinct().count()

        # === 环比周期映射 ===
        period_to_last = {
            'this_week': 'last_week',
            'last_week': 'week_before_last',
            'this_month': 'last_month',
            'last_month': 'month_before_last',
            'this_year': 'last_year',
            'custom': 'custom_last',
        }

        last_start, last_end = None, None
        if period in period_to_last:
            # custom 和 custom_last 需要传入原始 start_date/end_date
            if period == 'custom':
                if not (start_date and end_date):
                    # 无法计算环比
                    pass
                else:
                    last_start, last_end = get_date_range('custom_last', start_date, end_date)
            else:
                last_start, last_end = get_date_range(period_to_last[period])

        # 默认环比结构
        ring_ratio = {"people": 0, "entries": 0, "unit": 0, "ratio": 0}

        if last_start and last_end:
            last_process_records = ProcessRecord.objects.filter(
                entered_time__gte=last_start,
                entered_time__lte=last_end,
                registration_status__in=[2, 3]
            )

            last_people = last_process_records.values('person_name', 'phone_number').distinct().count()
            last_entries = EntryLog.objects.filter(
                process_record__in=last_process_records,
                entered_time__isnull=False
            ).count()
            last_unit = last_process_records.values('unit').distinct().count()

            last_normal = last_process_records.filter(is_normal=True).count()
            last_total_process = last_process_records.count()
            last_ratio = round((last_normal / last_total_process * 100), 2) if last_total_process > 0 else 0

            ring_ratio["people"] = round(((total_people - last_people) / last_people * 100), 2) if last_people > 0 else 0
            ring_ratio["entries"] = round(((total_entries - last_entries) / last_entries * 100), 2) if last_entries > 0 else 0
            ring_ratio["unit"] = round(((total_unit - last_unit) / last_unit * 100), 2) if last_unit > 0 else 0
            ring_ratio["ratio"] = round(normal_ratio - last_ratio, 2)

        return Response({
            "total_people": total_people,
            "total_entries": total_entries,
            "total_unit": total_unit,
            "normal_ratio_percent": normal_ratio,
            "ring_ratio": ring_ratio,
            "period": period,
            "date_range": {
                "start": start.strftime("%Y-%m-%d"),
                "end": end.strftime("%Y-%m-%d")
            }
        })


class UnitDistributionView(APIView):
    """
    获取单位分布饼图数据（基于 EntryLog 关联的 ProcessRecord.unit）
    统计每个单位的去重人数（姓名+电话），用于生成饼图和表格
    """
    def get(self, request):
        period = request.GET.get('period', 'this_month')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        start, end = get_date_range(period, start_date, end_date)

        # 查询符合条件的 ProcessRecord（已入场/已离场，且有 unit）
        process_records = ProcessRecord.objects.filter(
            entered_time__gte=start,
            entered_time__lte=end,
            registration_status__in=[2, 3],  # 已入场、已离场
            unit__isnull=False,
            unit__gt=''  # 排除空字符串
        )

        # 按单位分组，统计去重人数（person_name + phone_number）
        unit_stats = process_records.values('unit').annotate(
            count=Count('person_name', distinct=True)  # 去重人数
        ).order_by('-count')

        total_people = sum(item['count'] for item in unit_stats) or 1  # 防止除零

        top_units = []
        other_count = 0

        for i, item in enumerate(unit_stats):
            unit_name = item['unit']
            if i < 8:
                top_units.append({
                    "unit": unit_name,
                    "count": item['count'],
                    "percentage": 0
                })
            else:
                other_count += item['count']

        # 计算百分比
        for item in top_units:
            item["percentage"] = round((item["count"] / total_people * 100), 2)

        if other_count > 0:
            top_units.append({
                "unit": "其他",
                "count": other_count,
                "percentage": round((other_count / total_people * 100), 2)
            })

        return Response({"data": top_units})


class ApplicantCountView(APIView):
    """
    获取申请人次数柱状图数据（按申请人，从高到低）
    - completed: status in (2, 3)  # 已入场 或 已离场
    - pending: status = 1         # 未入场
    - status=4（已废止）不计入
    """
    def get(self, request):
        period = request.GET.get('period', 'this_month')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        start, end = get_date_range(period, start_date, end_date)

        # 只统计状态为 1, 2, 3 的记录（排除废止）
        applicant_stats = ProcessRecord.objects.filter(
            apply_enter_time__gte=start,
            apply_enter_time__lte=end,
            registration_status__in=[1, 2, 3]
        ).values('applicant').annotate(
            completed=Count('id', filter=Q(registration_status__in=[2, 3])),
            pending=Count('id', filter=Q(registration_status=1))
        ).order_by('-completed', '-pending')

        result = [
            {
                "name": item['applicant'] or "未知申请人",
                "completed": item['completed'] or 0,
                "pending": item['pending'] or 0
            }
            for item in applicant_stats
            if (item['completed'] or item['pending'])  # 理论上不会为0，但保险起见
        ]

        return Response({"data": result})
