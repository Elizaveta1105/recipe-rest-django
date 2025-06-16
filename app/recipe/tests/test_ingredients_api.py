"""
Tests for ingredient API
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user"""
    return get_user_model().objects.create(email=email, password=password)


def detail_url(ingredient_id):
    """Return ingredient detail url"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


class PublicIngredientsApiTest(TestCase):
    """Test unauth api requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is requireed for retrieving ingredients"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTest(TestCase):
    """Test auth api requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)


    def test_retrieve_ingredients(self):
        """Test retrieve the list of tags"""
        Ingredient.objects.create(user=self.user, name='potato')
        Ingredient.objects.create(user=self.user, name='onion')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to auth user"""
        user2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user=user2, name='vanilla')
        ingredient = Ingredient.objects.create(user=self.user, name='ice')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)


    def test_update_ingredient(self):
        """Test updating an ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='milk')

        payload = {'name': 'Coriander'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])


    def test_delete_ingredient(self):
        """Test deleting an ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='salt')

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())


    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingrediesnt by those assigned to recipes"""
        i1 = Ingredient.objects.create(user=self.user, name='apples')
        i2 = Ingredient.objects.create(user=self.user, name='turkey')

        recipe = Recipe.objects.create(
            title='Apple pie',
            time_minutes=5,
            price=Decimal('4.50'),
            user= self.user
        )

        recipe.ingredients.add(i1)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        s1 = IngredientSerializer(i1)
        s2 = IngredientSerializer(i2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients are unique"""
        ing = Ingredient.objects.create(user=self.user, name='eggs')
        Ingredient.objects.create(user=self.user, name='lentils')

        recipe1 = Recipe.objects.create(
            title='Eggs benedict',
            time_minutes=60,
            price=Decimal('7.50'),
            user=self.user
        )

        recipe2 = Recipe.objects.create(
            title='Herb eggs',
            time_minutes=20,
            price=Decimal('4.00'),
            user=self.user
        )

        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
