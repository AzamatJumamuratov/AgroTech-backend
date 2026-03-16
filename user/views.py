from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from .serializers import AdminRegisterSerializer, AdminLoginSerializer, AdminUserSerializer
from news.models import News
from news.serializers import NewsSerializer
from projects.models import Project, ProjectContact, ProjectComment
from projects.serializers import ProjectSerializer, ProjectContactSerializer, ProjectCommentSerializer
from core.models import CompanyInfo, Certificate, Partner
from core.serializers import CompanyInfoSerializer, CertificateSerializer, PartnerSerializer

@api_view(['POST'])
@permission_classes([])
def admin_register(request):
    """
    Регистрация админа
    POST /api/admin/register/
    """
    serializer = AdminRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user': AdminUserSerializer(user).data,
            'message': 'Админ успешно создан'
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([])
def admin_login(request):
    """
    Авторизация админа
    POST /api/admin/login/
    """
    serializer = AdminLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user': AdminUserSerializer(user).data,
            'message': 'Успешный вход'
        })

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_logout(request):
    """
    Выход админа
    POST /api/admin/logout/
    """
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Успешный выход'})
    except:
        return Response({'message': 'Ошибка выхода'}, status=status.HTTP_400_BAD_REQUEST)

# CRUD ViewSets для контента

class AdminNewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class AdminProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class AdminProjectContactViewSet(viewsets.ModelViewSet):
    queryset = ProjectContact.objects.all()
    serializer_class = ProjectContactSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class AdminProjectCommentViewSet(viewsets.ModelViewSet):
    queryset = ProjectComment.objects.all()
    serializer_class = ProjectCommentSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class AdminCompanyInfoViewSet(viewsets.ModelViewSet):
    queryset = CompanyInfo.objects.all()
    serializer_class = CompanyInfoSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class AdminCertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class AdminPartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]