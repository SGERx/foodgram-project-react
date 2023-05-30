def recipe_ingredient_create(ingredients_data, models, recipe):
    bulk_create_data = (
        models(
            recipe=recipe,
            ingredient=ingredient_data['ingredient'],
            amount=ingredient_data['amount'])
        for ingredient_data in ingredients_data
    )
    models.objects.bulk_create(bulk_create_data)
