from django.shortcuts import get_object_or_404, render, redirect
from accounts.models import Account
from store.models import Product, Variation
from .models import Cart, CartItem
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    current_user = request.user

    if current_user.role == Account.VENDOR:
        messages.error(request, "Vendors not authorized to add items to the cart.")
        return redirect('home')

    product = Product.objects.get(id=product_id) #this will get the product

    # Get all existing cart items for the current user
    cart_items = CartItem.objects.filter(user=current_user)

    if cart_items.exists():
        # Get the vendor of the first cart item (assuming all should have same vendor)
        existing_vendor = cart_items.first().product.vendor

        # Check if the vendor of the new product is same
        if product.vendor != existing_vendor:
            messages.error(request, "You can only add items from the same vendor in one cart.")
            return redirect(reverse('product_detail', args=[product.category.slug, product.slug]))

    # if the user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == "POST":
            for key, value in request.POST.items():
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        is_cart_item_exist = CartItem.objects.filter(product=product, user=current_user).exists()


        if is_cart_item_exist:
            cart_item = CartItem.objects.filter(product=product, user=current_user)

            ext_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ext_variation_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ext_variation_list:
                # increased cart item quantity
                index = ext_variation_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation )
            cart_item.save()

        return redirect('cart')

    else:
         # if the user is notauthenticated
        product_variation = []
        if request.method == "POST":
            for key, value in request.POST.items():
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass


        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) #get the cart using cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )

        cart.save()


        is_cart_item_exist = CartItem.objects.filter(product=product, cart=cart).exists()

        if is_cart_item_exist:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            # existing variation -> database
            # current variation - > product_variation
            # item_id -> database

            ext_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ext_variation_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ext_variation_list:
                # increased cart item quantity
                index = ext_variation_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation )
            cart_item.save()

        return redirect('cart')

def remove_cart(request, product_id, cart_item_id):

    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total)/100
        grand_total = total + tax
    except Exception as E:
        pass


    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
    }

    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total)/100
        grand_total = total + tax
    except Exception as E:
        pass


    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
    }
    return render(request, 'store/checkout.html', context)