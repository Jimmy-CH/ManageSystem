
from django.conf import settings
from django.utils.timezone import now
from rest_framework import status
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

# 模型
from apps.basic.models import Employee, Sign, SignAPIs
from apps.xc.models import Application  # 确保路径正确
from apps.basic.serializers import SignSerializer, SignAPIsSerializer
from apps.basic.filters import SignFilter

# 工具类（你提供的）
from utils.cipher import AESCipher

__all__ = ['SignViewSet', 'SignAPIsViewSet']


class SignViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, UpdateModelMixin):
    queryset = Sign.objects.select_related('apply_user', 'application').all()
    serializer_class = SignSerializer
    filterset_class = SignFilter

    def _get_current_time_str(self):
        """替代 now_to_str，返回字符串格式时间"""
        return now().strftime('%Y-%m-%d %H:%M:%S')

    def _generate_security_key(self, apply_user_id, application_id=None):
        """使用你提供的 AESCipher 生成密钥"""
        sign_aes = AESCipher(settings.SIGN_CIPHER_KEY)
        sign_time = self._get_current_time_str()
        if application_id:
            payload = (sign_aes.key(1), f"{apply_user_id}@{application_id}", sign_time)
        else:
            payload = (sign_aes.key(1), apply_user_id, sign_time)
        return sign_aes.encrypt(payload), sign_time

    def create(self, request, *args, **kwargs):
        apply_user_id = request.data.get('apply_user_id')
        application_id = request.data.get('application_id')
        comment = request.data.get('comment', '')

        # 校验申请人
        if not Employee.objects.filter(psncode=apply_user_id).exists():
            raise ValidationError('申请人不存在，无法签发！')

        # 校验应用（如果提供）
        if application_id:
            if not Application.objects.filter(id=application_id).exists():
                raise ValidationError(f'应用 ID: {application_id} 不存在，请选择正确的应用')
            if Sign.objects.filter(apply_user_id=apply_user_id, application_id=application_id).exists():
                raise ValidationError('签证已存在，无需重复签发！')
        else:
            if Sign.objects.filter(apply_user_id=apply_user_id).exists():
                raise ValidationError('签证已存在，无需重复签发！')

        security_key, sign_time = self._generate_security_key(apply_user_id, application_id)

        # 构造数据
        data = {
            'security_key': security_key,
            'sign_time': sign_time,
            'comment': comment,
            'apply_user': apply_user_id,
            'application': application_id,
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True, url_path='redo')
    def redo(self, request, *args, **kwargs):
        instance = self.get_object()
        security_key, sign_time = self._generate_security_key(
            instance.apply_user_id,
            instance.application_id
        )
        serializer = self.get_serializer(
            instance,
            data={'security_key': security_key, 'sign_time': sign_time},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignAPIsViewSet(ModelViewSet):
    queryset = SignAPIs.objects.all()
    serializer_class = SignAPIsSerializer

