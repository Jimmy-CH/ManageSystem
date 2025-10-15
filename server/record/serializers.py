
from rest_framework import serializers
from .models import ProcessRecord, EntryLog, OAInfo, OAPerson


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

    class Meta:
        model = ProcessRecord
        fields = '__all__'
        read_only_fields = ['create_time', 'update_time']

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
    # persons = OAPersonSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = OAInfo
        fields = '__all__'
        read_only_fields = ['create_time', 'connected_count']  # connected_count 由逻辑控制

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


class ProcessRecordBatchRegisterSerializer(serializers.Serializer):
    apply_enter_time = serializers.DateTimeField(required=False)
    apply_leave_time = serializers.DateTimeField(required=False)
    reason = serializers.CharField(required=False, allow_blank=True)
    carried_items = serializers.CharField(required=False, allow_blank=True)
    companion = serializers.CharField(max_length=128, default="无")
    remarks = serializers.CharField(required=False, allow_blank=True)
    personnel = PersonnelItemSerializer(many=True)

    def validate_personnel(self, value):
        if not value:
            raise serializers.ValidationError("至少需要登记一人。")
        if len(value) > 50:
            raise serializers.ValidationError("单次登记人数不能超过50人。")
        return value

    def create(self, validated_data):
        personnel_data = validated_data.pop('personnel')
        records = []

        # 公共字段
        common_fields = {
            'reason': validated_data.get('reason'),
            'carried_items': validated_data.get('carried_items'),
            'companion': validated_data.get('companion', '无'),
            'remarks': validated_data.get('remarks'),
            'apply_enter_time': validated_data.get('apply_enter_time'),
            'apply_leave_time': validated_data.get('apply_leave_time'),
            # 紧急登记标志
            'is_emergency': True,
            'is_normal': False,
            'is_linked': False,
            'registration_status': 1,  # 未入场
        }

        from django.utils import timezone
        now = timezone.now()
        if not common_fields['apply_enter_time']:
            common_fields['apply_enter_time'] = now
        if not common_fields['apply_leave_time']:
            common_fields['apply_leave_time'] = now + timezone.timedelta(hours=24)

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
            records.append(record)

        # 批量创建
        created_records = ProcessRecord.objects.bulk_create(records)
        return created_records
