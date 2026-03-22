from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import ContactInfo, SocialLink

class SingletonEndpointsTests(APITestCase):
    def test_contact_info_empty(self):
        """Test that contact-info returns 200 OK even if no data exists."""
        url = reverse('contact-info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_social_links_empty(self):
        """Test that social-links returns 200 OK even if no data exists."""
        url = reverse('social-links')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})
