from rest_framework import serializers
from .models import (
    EventCategory, EventComponentInfo, Event,
    EventDeviceInfo, EventHandleProcess,
    EventTimeEffective, EventTimeSpecial
)


class EventCategorySerializer(serializers.ModelSerializer):
    child_category = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = EventCategory
        fields = '__all__'


class EventComponentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventComponentInfo
        fields = '__all__'


class EventDeviceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventDeviceInfo
        fields = '__all__'
        extra_kwargs = {
            'update_time': {'read_only': True},
            'create_time': {'read_only': True},
        }


class EventHandleProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventHandleProcess
        fields = '__all__'
        extra_kwargs = {
            'update_time': {'read_only': True},
            'create_time': {'read_only': True},
        }


class EventSerializer(serializers.ModelSerializer):
    device_info = EventDeviceInfoSerializer(many=True, read_only=True)
    event_handle_process = EventHandleProcessSerializer(many=True, read_only=True)

    # 支持创建时写入设备和处理过程
    device_info_create = EventDeviceInfoSerializer(many=True, write_only=True, required=False)
    handle_process_create = EventHandleProcessSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Event
        fields = '__all__'

    def create(self, validated_data):
        device_data = validated_data.pop('device_info_create', [])
        process_data = validated_data.pop('handle_process_create', [])

        event = Event.objects.create(**validated_data)

        for dev in device_data:
            EventDeviceInfo.objects.create(event=event, **dev)
        for proc in process_data:
            EventHandleProcess.objects.create(event=event, **proc)

        return event

    def update(self, instance, validated_data):
        # 提取嵌套数据
        device_data_list = validated_data.pop('device_info_create', None)
        process_data_list = validated_data.pop('handle_process_create', None)

        # 更新 Event 主表字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if device_data_list is not None:
            self._update_device_info(instance, device_data_list)

        if process_data_list is not None:
            self._update_handle_process(instance, process_data_list)

        return instance

    def _update_device_info(self, event, device_data_list):
        """
        全量更新设备信息：
        - 已存在的记录：更新
        - 新增的记录：创建
        - 原有但未传入的记录：删除（可选）
        """
        existing_ids = set(event.device_info.values_list('id', flat=True))
        input_ids = set()

        for dev_data in device_data_list:
            dev_id = dev_data.get('id')
            if dev_id:
                # 更新已有记录
                try:
                    obj = EventDeviceInfo.objects.get(id=dev_id, event=event)
                    for key, value in dev_data.items():
                        setattr(obj, key, value)
                    obj.save()
                    input_ids.add(dev_id)
                except EventDeviceInfo.DoesNotExist:
                    # id 不存在？当作新增（或抛错，根据业务）
                    obj = EventDeviceInfo.objects.create(event=event, **dev_data)
                    input_ids.add(obj.id)
            else:
                # 新增记录
                obj = EventDeviceInfo.objects.create(event=event, **dev_data)
                input_ids.add(obj.id)

        # 可选：删除前端未传入的旧记录（实现“全量同步”）
        to_delete = existing_ids - input_ids
        if to_delete:
            EventDeviceInfo.objects.filter(id__in=to_delete).delete()

    def _update_handle_process(self, event, process_data_list):
        """
        全量更新处理过程
        """
        existing_ids = set(event.event_handle_process.values_list('id', flat=True))
        input_ids = set()

        for proc_data in process_data_list:
            proc_id = proc_data.get('id')
            if proc_id:
                try:
                    obj = EventHandleProcess.objects.get(id=proc_id, event=event)
                    for key, value in proc_data.items():
                        setattr(obj, key, value)
                    obj.save()
                    input_ids.add(proc_id)
                except EventHandleProcess.DoesNotExist:
                    obj = EventHandleProcess.objects.create(event=event, **proc_data)
                    input_ids.add(obj.id)
            else:
                obj = EventHandleProcess.objects.create(event=event, **proc_data)
                input_ids.add(obj.id)

        # 删除未传入的旧记录
        to_delete = existing_ids - input_ids
        if to_delete:
            EventHandleProcess.objects.filter(id__in=to_delete).delete()


class EventTimeEffectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTimeEffective
        fields = '__all__'


class EventTimeSpecialSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTimeSpecial
        fields = '__all__'
