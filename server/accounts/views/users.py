
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.serializers import MyTokenObtainPairSerializer, UserRegistrationSerializer, UserProfileSerializer
from common import APIResponse


# 登录
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# 刷新 Token
class MyTokenRefreshView(TokenRefreshView):
    pass


# 用户注册
class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return APIResponse({
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "profile": {
                        "avatar": user.profile.avatar.url if user.profile.avatar else None,
                        "address": user.profile.address,
                        "phone": user.profile.phone,
                        "bio": user.profile.bio,
                    }
                }
            }, status=status.HTTP_201_CREATED)
        return APIResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 获取用户信息
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile  # 通过 OneToOne 获取
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    # 可选：支持更新用户信息（PUT/PATCH）
    def put(self, request):
        profile = request.user.profile
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
