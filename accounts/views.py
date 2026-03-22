from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserSerializer, UpdateProfileSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Регистрация нового пользователя. Возвращает JWT токены."""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Логин пользователя. Возвращает JWT токены."""
    from django.contrib.auth import authenticate

    username = request.data.get('username', '')
    password = request.data.get('password', '')

    if not username or not password:
        return Response(
            {'error': 'Введите имя пользователя и пароль.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)
    if user is None:
        return Response(
            {'error': 'Неверное имя пользователя или пароль.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)
    return Response({
        'user': UserSerializer(user).data,
        'tokens': {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
    })


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def me(request):
    """Получить/обновить профиль текущего пользователя."""
    if request.method == 'GET':
        return Response(UserSerializer(request.user).data)

    serializer = UpdateProfileSerializer(data=request.data, partial=True)
    if serializer.is_valid():
        serializer.update(request.user, serializer.validated_data)
        return Response(UserSerializer(request.user).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
