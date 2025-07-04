"""
Tests for the healthcheck api
"""

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

class HealthCheckTests(TestCase):

    def test_healthcheck(self):
        """Test health check api"""

        client = APIClient()
        url = reverse('health-check')
        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        