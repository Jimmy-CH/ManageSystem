
from rest_framework import serializers
from .models import ProcessRecord, EntryLog, OAInfo, OAPerson
from django.utils import timezone
from django.db import transaction

from .utils import mask_id_number, mask_phone_number


class EntryLogSerializer(serializers.ModelSerializer):
    card_status_display = serializers.CharField(
        source='get_card_status_display',
        read_only=True
    )
    card_type_display = serializers.CharField(
        source='get_card_type_display',
        read_only=True
    )
    id_type_display = serializers.CharField(
        source='get_id_type_display',
        read_only=True
    )
    pledged_status_display = serializers.CharField(
        source='get_pledged_status_display',
        read_only=True
    )

    class Meta:
        model = EntryLog
        fields = '__all__'


class ProcessRecordSerializer(serializers.ModelSerializer):
    person_type_display = serializers.CharField(
        source='get_person_type_display',
        read_only=True
    )
    id_type_display = serializers.CharField(
        source='get_id_type_display',
        read_only=True
    )
    registration_status_display = serializers.CharField(
        source='get_registration_status_display',
        read_only=True
    )
    card_status_display = serializers.CharField(
        source='get_card_status_display',
        read_only=True
    )
    card_type_display = serializers.CharField(
        source='get_card_type_display',
        read_only=True
    )
    pledged_status_display = serializers.CharField(
        source='get_pledged_status_display',
        read_only=True
    )
    id_number = serializers.SerializerMethodField(read_only=True)
    phone_number = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProcessRecord
        fields = '__all__'
        read_only_fields = ['create_time', 'update_time']

    def get_id_number(self, obj):
        raw = obj.id_number
        return mask_id_number(raw)

    def get_phone_number(self, obj):
        raw = obj.phone_number
        return mask_phone_number(raw)

    def validate(self, data):
        registration_status = data.get('registration_status')
        if registration_status == 2 and not data.get('entered_time'):
            raise serializers.ValidationError("已入场状态必须填写实际进入时间")
        if registration_status == 3 and not data.get('exited_time'):
            raise serializers.ValidationError("已离场状态必须填写实际离开时间")
        return data


class OAPersonSerializer(serializers.ModelSerializer):
    applicant = serializers.CharField(source='oa_info.applicant', read_only=True)
    apply_enter_time = serializers.DateTimeField(source='oa_info.apply_enter_time', read_only=True)
    oa_link = serializers.CharField(source='oa_info.oa_link', read_only=True)
    person_type_display = serializers.CharField(
        source='get_person_type_display',
        read_only=True
    )
    id_type_display = serializers.CharField(
        source='get_id_type_display',
        read_only=True
    )

    class Meta:
        model = OAPerson
        fields = [
            'id', 'person_name', 'phone_number', 'person_type', 'person_type_display',
            'id_type', 'id_type_display', 'id_number', 'unit', 'department', 'is_linked',
            'applicant', 'apply_enter_time', 'oa_link'
        ]


class OAInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = OAInfo
        fields = '__all__'
        read_only_fields = ['create_time', 'connected_count']

    def create(self, validated_data):
        persons_data = validated_data.pop('persons', [])
        oa_info = OAInfo.objects.create(**validated_data)

        for person_data in persons_data:
            OAPerson.objects.create(oa_info=oa_info, **person_data)

        # 自动更新 connected_count
        oa_info.connected_count = len(persons_data)
        oa_info.save(update_fields=['connected_count'])

        return oa_info

    def update(self, instance, validated_data):
        persons_data = validated_data.pop('persons', None)

        # 更新 OAInfo 字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if persons_data is not None:
            instance.persons.all().delete()
            for person_data in persons_data:
                OAPerson.objects.create(oa_info=instance, **person_data)
            instance.connected_count = len(persons_data)
            instance.save(update_fields=['connected_count'])

        return instance


class PersonnelItemSerializer(serializers.Serializer):
    person_name = serializers.CharField(max_length=50)
    phone_number = serializers.CharField(max_length=200, required=False, allow_blank=True)
    person_type = serializers.ChoiceField(choices=ProcessRecord.PERSON_TYPE_CHOICES)
    id_type = serializers.ChoiceField(choices=ProcessRecord.ID_TYPE_CHOICES)
    id_number = serializers.CharField(max_length=200, required=False, allow_blank=True)
    unit = serializers.CharField(max_length=100, required=False, allow_blank=True)
    department = serializers.CharField(max_length=100, required=False, allow_blank=True)
    card_status = serializers.ChoiceField(choices=ProcessRecord.CARD_STATUS_CHOICES, default=1)
    card_type = serializers.ChoiceField(choices=ProcessRecord.CARD_TYPE_CHOICES, default=1)
    pledged_status = serializers.ChoiceField(choices=ProcessRecord.PLEDGED_STATUS_CHOICES, default=1)
    pledged_id_type = serializers.ChoiceField(choices=ProcessRecord.ID_TYPE_CHOICES, default=0)


class ProcessRecordBatchRegisterSerializer(serializers.Serializer):
    apply_enter_time = serializers.DateTimeField(required=False)
    apply_leave_time = serializers.DateTimeField(required=False)
    reason = serializers.CharField(required=False, allow_blank=True)
    carried_items = serializers.CharField(required=False, allow_blank=True)
    companion = serializers.CharField(max_length=128, default="无", allow_blank=True)
    remarks = serializers.CharField(required=False, allow_blank=True)
    personnel = PersonnelItemSerializer(many=True)
    entered_time = serializers.DateTimeField(required=False)

    def validate_personnel(self, value):
        if not value:
            raise serializers.ValidationError("至少需要登记一人。")
        if len(value) > 50:
            raise serializers.ValidationError("单次登记人数不能超过50人。")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user_info = request.user
            operator_code = user_info.get('uuid', 'admin')
            operator_name = user_info.get('user_name', 'admin')
        else:
            operator_code = 'system'
            operator_name = '系统'

        personnel_data = validated_data.pop('personnel')
        now = timezone.now()

        common_fields = {
            'reason': validated_data.get('reason'),
            'carried_items': validated_data.get('carried_items'),
            'companion': validated_data.get('companion', '无'),
            'remarks': validated_data.get('remarks'),
            # 'apply_enter_time': validated_data.get('apply_enter_time') or now,
            # 'apply_leave_time': validated_data.get('apply_leave_time') or (now + timezone.timedelta(hours=24)),
            'is_emergency': True,
            'is_linked': False,
            'registration_status': 2,
            'create_user_code': operator_code,
            'create_user_name': operator_name,
            'change_user_code': operator_code,
            'change_user_name': operator_name,
            'entered_time': validated_data.get('entered_time') or now,
            'enter_count': 1,
        }

        created_records = []

        with transaction.atomic():
            for person in personnel_data:
                record = ProcessRecord(
                    person_name=person['person_name'],
                    phone_number=person.get('phone_number'),
                    person_type=person['person_type'],
                    id_type=person['id_type'],
                    id_number=person.get('id_number'),
                    unit=person.get('unit'),
                    department=person.get('department'),
                    card_status=person['card_status'],
                    card_type=person['card_type'],
                    pledged_status=person['pledged_status'],
                    **common_fields
                )
                record.save()
                created_records.append(record)

                EntryLog.objects.create(
                    process_record=record,
                    entered_time=record.entered_time,
                    create_time=record.entered_time,
                    create_user_code=operator_code,
                    create_user_name=operator_name,
                    card_status=record.card_status,
                    card_type=record.card_type if record.card_status == 2 else 0,
                    pledged_status=record.pledged_status,
                    id_type=person['pledged_id_type'] if record.pledged_status == 2 else 0,
                    companion=record.companion,
                    remarks=record.remarks,
                    operation="入场"
                )

        return created_records


class ProcessRecordDetailSerializer(serializers.ModelSerializer):
    latest_entry = serializers.SerializerMethodField()
    latest_exit = serializers.SerializerMethodField()
    id_number = serializers.SerializerMethodField(read_only=True)
    phone_number = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProcessRecord
        fields = '__all__'

    def get_id_number(self, obj):
        raw = obj.id_number
        return mask_id_number(raw)

    def get_phone_number(self, obj):
        raw = obj.phone_number
        return mask_phone_number(raw)

    def get_latest_entry(self, obj):
        latest = EntryLog.objects.filter(
            process_record=obj,
            operation='入场'
        ).order_by('-entered_time').first()
        return EntryLogSerializer(latest, context=self.context).data if latest else None

    def get_latest_exit(self, obj):
        latest = EntryLog.objects.filter(
            process_record=obj,
            operation='离场'
        ).order_by('-exited_time').first()
        return EntryLogSerializer(latest, context=self.context).data if latest else None


