import io

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import Recipe, IngredientInRecipe


def recipe_ingredient_create(ingredients_data, models, recipe):
    bulk_create_data = (
        models(
            recipe=recipe,
            ingredient=ingredient_data['ingredient'],
            amount=ingredient_data['amount'])
        for ingredient_data in ingredients_data
    )
    models.objects.bulk_create(bulk_create_data)
