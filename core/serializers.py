from rest_framework import serializers
from .models import CompanyInfo, Certificate, Partner, ContactInfo, SocialLink
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField

class CompanyInfoSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=CompanyInfo)

    class Meta:
        model = CompanyInfo
        fields = ['id', 'translations', 'created_at']
        read_only_fields = ['created_at']

class CertificateSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = ['id', 'image', 'image_url', 'caption', 'created_at']
        read_only_fields = ['created_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        return None

class PartnerSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Partner)
    class Meta:
        model = Partner
        fields = ['id', 'name', 'description', 'is_foreign', 'translations']


class ContactInfoSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=ContactInfo)

    class Meta:
        model = ContactInfo
        fields = ['email','translations', 'phone', 'created_at']
        read_only_fields = ['created_at']

    def validate_email(self, value):
        """Validate email format."""
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value
    def validate_phone(self, value):
        """Validate phone format."""
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        return value
    def validate_address(self, value):
        """Validate address format."""
        if not value:
            raise serializers.ValidationError("Address is required.")
        return value.strip()


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = [ 'telegram', 'instagram', 'facebook', 'linkedin']


    def validate_telegram(self, value):
        """Validate Telegram URL."""
        if not value:
            raise serializers.ValidationError("Telegram link is required.")
        return value

    def validate_instagram(self, value):
        """Validate Instagram URL."""
        if not value:
            raise serializers.ValidationError("Instagram link is required.")
        return value

    def validate_facebook(self, value):
        """Validate Facebook URL."""
        if not value:
            raise serializers.ValidationError("Facebook link is required.")
        return value

    def validate_linkedin(self, value):
        """Validate Facebook URL."""
        if not value:
            raise serializers.ValidationError("LinkedIn link is required.")
        return value
