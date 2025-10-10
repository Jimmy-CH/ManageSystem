
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
    status_display = serializers.CharField(
        source='get_status_display',
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
        read_only_fields = ['created_at', 'updated_time']

    def validate(self, data):
        status = data.get('status')
        if status == 2 and not data.get('entered_time'):
            raise serializers.ValidationError("已入场状态必须填写实际进入时间")
        if status == 3 and not data.get('exited_time'):
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
            'id', 'name', 'phone_number', 'person_type', 'person_type_display',
            'id_type', 'id_type_display', 'id_number', 'unit', 'department', 'is_linked',
            'applicant', 'apply_enter_time', 'oa_link'
        ]


class OAInfoSerializer(serializers.ModelSerializer):
    persons = OAPersonSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = OAInfo
        fields = '__all__'
        read_only_fields = ['create_time', 'connected_count']  # connected_count 由逻辑控制

    def create(self, validated_data):
        persons_data = validated_data.pop('persons', [])
        oa_info = OAInfo.objects.create(**validated_data)

        for person_data in persons_data:
            OAPerson.objects.create(oa_info=oa_info, **person_data)

        oa_info.connected_count = len(persons_data)
        oa_info.save(update_fields=['connected_count'])

        return oa_info

    def update(self, instance, validated_data):
        persons_data = validated_data.pop('persons', None)

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

