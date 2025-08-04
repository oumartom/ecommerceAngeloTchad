from django.shortcuts import render, get_object_or_404
from .models import Product

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    products = Product.objects.all()[:6]  # on limite à 6 pour ne pas surcharger la page

    context = {
        'product': product,
        'products': products,
    }
    return render(request, 'orders/product_detail.html', context)

# from django.shortcuts import render, get_object_or_404
# from .models import Product

# def product_detail(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     context = {
#         'product': product
#     }
#     return render(request, 'orders/product_detail.html', context)


