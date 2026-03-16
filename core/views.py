from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import CompanyInfo, Certificate, Partner, ContactInfo, SocialLink
from .serializers import CompanyInfoSerializer, CertificateSerializer, PartnerSerializer, ContactInfoSerializer, SocialLinkSerializer

class SingletonModelViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset().first()
        if not instance:
            return Response({'detail': 'Нет данных'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_queryset().first()
        if not instance:
            return Response({'detail': 'Нет данных'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        return Response({'detail': 'Создание запрещено'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Удаление запрещено'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_object(self):
        return self.get_queryset().first()


class CompanyInfoViewSet(viewsets.ModelViewSet):
    queryset = CompanyInfo.objects.all()
    serializer_class = CompanyInfoSerializer
    permission_classes = [AllowAny]

class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [AllowAny]

class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [AllowAny]


class ContactInfoViewSet(SingletonModelViewSet):
    queryset = ContactInfo.objects.all()
    serializer_class = ContactInfoSerializer
    permission_classes = [AllowAny]

class SocialLinkViewSet(SingletonModelViewSet):
    queryset = SocialLink.objects.all()
    serializer_class = SocialLinkSerializer
    permission_classes = [AllowAny]

