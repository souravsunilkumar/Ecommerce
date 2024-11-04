
import logging
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from app.models import *
from collections import defaultdict
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from django.template.loader import render_to_string
from django.db.models import Max, Min, Sum, Q, Avg,Count
from cart.cart import Cart
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.models import Group
from app.forms import *
from django.urls import reverse
from datetime import datetime
import razorpay
from django.conf import settings


logger = logging.getLogger(__name__)


def BASE(req):
    return render(req,'base.html')

def HOME(req):
    sliders=slider.objects.all().order_by('-id')
    banners =banner_area.objects.all().order_by('-id')

    main_category = Main_category.objects.all().order_by('-id')
    product =Product.objects.filter(section__name='Top Deal of The Day')

    context ={
        'current_page': 'home',
        'sliders':sliders,
        'banners':banners,
        'main_category':main_category,
        'product':product,
    }

    return render(req,'main/home.html',context)

# Product DEtails 
def PRODUCT_DETAILS(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all()
    review_count = reviews.count()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    if request.method == 'POST':
        rating = request.POST.get('rating')
        review_text = request.POST.get('item_review')

        if rating and review_text:
            
            review = Review(
                product=product,
                rating=int(rating),
                user=request.user,
                review=review_text
            )
            review.save()
            
           
            average_rating = product.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
            product.average_rating = average_rating
            product.save()

            messages.success(request, "Your review has been submitted successfully.")
            return redirect('product_detail', slug=slug)
        else:
            messages.error(request, "Please fill out all fields.")

    context = {
        'product': product,
        'reviews': reviews,
        'review_count': review_count,
        'average_rating': average_rating,
    }

    return render(request, 'product/product_detail.html', context)


#Error
def Erro404(request, exception):
    return render(request, 'errors/404.html', status=404)

#My account
def MY_ACCOUNT(req):
    return render(req, 'account/my_account.html')

#REgister
def REGISTER(req):
    if req.method == "POST":
        username = req.POST.get('username')
        email = req.POST.get('email')
        password = req.POST.get('password')
        group_id = req.POST.get('group_id') 

        if User.objects.filter(username=username).exists():
            messages.error(req, 'Username already exists')
            return redirect('login')
        if User.objects.filter(email=email).exists():
            messages.error(req, 'Email id already exists')
            return redirect('login')

        user = User(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()

        customer_group = Group.objects.get(id=group_id)
        user.groups.add(customer_group)

        return redirect('login')


#Login    
def LOGIN(req):
    if req.method == 'POST':
        username = req.POST.get('username')
        password = req.POST.get('password')
        
        user = authenticate(req, username=username, password=password)
        if user is not None:
            login(req, user)
            if user.groups.filter(id=1).exists():  
                return redirect('admin_home')
            else:
                return redirect('home')
        else:
            messages.error(req, 'Email or Password is Invalid!')
            return redirect('login')


#is_admin
def is_admin(user):
    return user.groups.filter(id=1).exists()

#Profile
@login_required(login_url='/accounts/login/')
def PROFILE(req):
    return render(req,'profile/profile.html')

#Login
@login_required(login_url='/accounts/login/')
def PROFILE_UPDATE(req):
    if req.method == 'POST':
        username=req.POST.get('username')
        first_name=req.POST.get('first_name')
        last_name=req.POST.get('last_name')
        email=req.POST.get('email')
        password=req.POST.get('password')
        user_id=req.user.id

        user =User.objects.get(id=user_id)
        user.first_name=first_name
        user.last_name=last_name
        user.username=username
        user.email=email

        if password != None and password !="":
            user.set_password(password)
        user.save()
        messages.success(req,'Pofile is Updated Successfully')
        return redirect('profile')


#Logout
def LOGOUT(req):
    logout(req)
    return redirect('home')

def logout_confirmation(request):
    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/')
    return render(request, 'profile/logout_confirmation.html')

#notification
def Notifications(request):
    user = request.user

    return render(request, 'notification/notification.html')

def admin_notification(request):
    if request.user.groups.filter(id=1).exists():  
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True) 
        context = {'notifications': notifications}
        return render(request, 'notification/admin_notification.html', context)
    else:
        return redirect('home_url')

def Delivery_notification(request):
    
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    notifications.update(is_read=True)
    
  
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'notification/delivery_notification.html', context)

def Sales_notification(req):
    return render(req,'notification/sales_notification.html')

def ABOUT(req):
    context={
        'current_page': 'about',
    }
    return render(req,'main/about.html',context)

def CONTACT(req):
    context ={
        'current_page': 'contact',
    }

    return render(req,'main/contact.html',context)

#Product
def PRODUCT(req):
    main_category = Main_category.objects.all()
    category = Category.objects.all()
    colour = Colour.objects.all()
    brand = Brand.objects.all()

    min_price = Product.objects.all().aggregate(Min('price'))
    max_price = Product.objects.all().aggregate(Max('price'))

    ColourID = req.GET.getlist('colourID')
    FilterPrice = req.GET.get('FilterPrice')
    mainCategoryID = req.GET.get('mainCategoryID')
    categoryID = req.GET.get('categoryID')
    subCategoryID = req.GET.get('subCategoryID')
    BrandIDs = req.GET.getlist('brandID')

    filters = Q()

    if subCategoryID:
        filters &= Q(categories_id=subCategoryID)

    if FilterPrice:
        filters &= Q(price__lte=int(FilterPrice))

    if ColourID:
        filters &= Q(colour_id__in=ColourID)
    
    if BrandIDs:
        filters &= Q(brand_id__in=BrandIDs)

    if categoryID and not subCategoryID:
        sub_categories = Sub_category.objects.filter(category_id=categoryID)
        filters &= Q(categories__in=sub_categories)

    if mainCategoryID and not subCategoryID:
        categories = Category.objects.filter(main_category_id=mainCategoryID)
        sub_categories = Sub_category.objects.filter(category__in=categories)
        filters &= Q(categories__in=sub_categories)

    products = Product.objects.filter(filters).annotate(review_count=Count('reviews')).order_by('id')

    items_per_page = int(req.GET.get('items_per_page', 10))

    paginator = Paginator(products, items_per_page)
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'current_page': 'product',
        'main_category': main_category,
        'category': category,
        'product': page_obj,
        'min_price': min_price,
        'max_price': max_price,
        'FilterPrice': FilterPrice,
        'colour': colour,
        'brand': brand,
        'BrandIDs': BrandIDs,
        'ColourID': ColourID,
        'subCategoryID': subCategoryID,
        'page_obj': page_obj,
        'no_products': not products.exists(), 
        'items_per_page': items_per_page,  
    }
    return render(req, 'product/product.html', context)

#Cart
def CART(req):
    return render(req,'cart/cart.html')


@login_required(login_url="/accounts/login/")
def cart_add(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("cart_detail")


@login_required(login_url="/accounts/login/")
def item_clear(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.remove(product)
    return redirect("cart_detail")


@login_required(login_url="/accounts/login/")
def item_increment(request, id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=id)
    cart_item = cart.get_item(product)
    if cart_item and cart_item['quantity'] < product.availability:
        cart.add(product=product)
    else:
        messages.error(request, "Cannot increase quantity beyond availability.")
    return redirect("cart_detail")


@login_required(login_url="/accounts/login/")
def item_decrement(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.decrement(product=product)
    return redirect("cart_detail")


@login_required(login_url="/accounts/login/")
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")


@login_required(login_url="/accounts/login/")
def cart_detail(request):
    cart = request.session.get('cart', {})
    packing_cost = sum(i['packing_cost'] for i in cart.values() if i)
    tax = sum(i['tax'] for i in cart.values() if i)

    



    cart_total_amount = sum(i['price'] * i['quantity'] for i in cart.values() if i)


    context = {
        'packing_cost': packing_cost,
        'tax': tax,
        'cart': cart,
    }
    return render(request, 'cart/cart.html', context)


#Checkout
@login_required
def Checkout(request):
    logger.info("Checkout view accessed")
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        packing_cost = sum(i['packing_cost'] for i in cart.values() if i)
        tax = sum(i['tax'] for i in cart.values() if i)
        cart_total_amount = sum(i['price'] * i['quantity'] for i in cart.values() if i)

        

        discounted_total = cart_total_amount

        if discounted_total > 1000:
            total_amount_paid = discounted_total + packing_cost + tax
        else:
            total_amount_paid = discounted_total + packing_cost + tax + 120

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postcode = request.POST.get('postcode')
        state = request.POST.get('state')
        country = request.POST.get('country')
        payment_method = request.POST.get('payment_method')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

       
        if payment_method == 'online_payment':
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            try:
                client.utility.verify_payment_signature(params_dict)
            except:
                return HttpResponse("Payment verification failed.")

       
        for key, value in cart.items():
            total_price = value['price'] * value['quantity']
            product = get_object_or_404(Product, id=value['product_id'])
            product.availability -= value['quantity']
            product.save()

            order = Order.objects.create(
                user=request.user,
                product_image=value['featured_image'],
                product_name=value['product_name'],
                quantity=value['quantity'],
                unit_price=value['price'],
                total_price=total_price,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address=address,
                city=city,
                postcode=postcode,
                state=state,
                country=country,
                order_status="Order Placed",
                payment_method=payment_method,
                total_amount_paid=total_amount_paid,
                payment_order_id=razorpay_order_id,
            )

        request.session['cart'] = {}

        return redirect('order_success')

    else:
        logger.info("Checkout view accessed via GET method")
        cart = request.session.get('cart', {})
        packing_cost = sum(i['packing_cost'] for i in cart.values() if i)
        tax = sum(i['tax'] for i in cart.values() if i)
        cart_total_amount = sum(i['price'] * i['quantity'] for i in cart.values() if i)

        
        coupon_discount = 0

        discounted_total = cart_total_amount * (1 - coupon_discount / 100) if coupon_discount else cart_total_amount

        if discounted_total > 1000:
            total_amount_paid = discounted_total + packing_cost + tax
        else:
            total_amount_paid = discounted_total + packing_cost + tax + 120

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment_order = client.order.create({
            'amount': total_amount_paid * 100,
            'currency': 'INR',
            'payment_capture': 1
        })
        print(payment_order)
        context = {
            'packing_cost': packing_cost,
            'tax': tax,
            'cart_total_amount': cart_total_amount,
            'coupon_discount': coupon_discount,
            'discounted_total': discounted_total,
            'total_amount_paid': total_amount_paid,
            'payment_order': payment_order,
        }
        return render(request, 'checkout/checkout.html', context)
    
def success(request):
    razorpay_payment_id = request.GET.get('razorpay_payment_id')
    razorpay_order_id = request.GET.get('razorpay_order_id')
    razorpay_signature = request.GET.get('razorpay_signature')

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
        
        return render(request, 'checkout/order_success.html')
    except razorpay.errors.SignatureVerificationError:
       
        return render(request, 'checkout/payment_failed.html')
    
    
def Payment(req):
    return render(req,'payment.html')


#Search_view


def search_view(req):
    query = req.GET.get('query', '')   
    main_category = Main_category.objects.all()
    category = Category.objects.all()
    sub_category = Sub_category.objects.all()

    min_price = Product.objects.all().aggregate(Min('price'))
    max_price = Product.objects.all().aggregate(Max('price'))
    
    ColourID = req.GET.getlist('colourID')
    FilterPrice = req.GET.get('FilterPrice')
    mainCategoryID = req.GET.get('mainCategoryID')
    categoryID = req.GET.get('categoryID')
    subCategoryID = req.GET.get('subCategoryID')
    BrandIDs = req.GET.getlist('brandID')

    products = Product.objects.filter(
        Q(product_name__icontains=query) |
        Q(tags__icontains=query)  
    )

   
    if subCategoryID:
        products = products.filter(categories_id=subCategoryID)

    if FilterPrice:
        products = products.filter(price__lte=int(FilterPrice))

    if ColourID:
        products = products.filter(colour_id__in=ColourID)

    if categoryID and not subCategoryID:
        sub_categories = Sub_category.objects.filter(category_id=categoryID)
        products = products.filter(categories__in=sub_categories)

    if mainCategoryID and not subCategoryID:
        categories = Category.objects.filter(main_category_id=mainCategoryID)
        sub_categories = Sub_category.objects.filter(category__in=categories)
        products = products.filter(categories__in=sub_categories)

    if BrandIDs:
        products = products.filter(brand_id__in=BrandIDs)

    colour = Colour.objects.filter(product__in=products).distinct()
    brand = Brand.objects.filter(product__in=products).distinct()

    items_per_page = int(req.GET.get('items_per_page', 10))

    paginator = Paginator(products, items_per_page)
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'current_page': 'product',
        'main_category': main_category,
        'category': category,
        'product': page_obj,
        'min_price': min_price,
        'max_price': max_price,
        'FilterPrice': FilterPrice,
        'colour': colour,
        'brand': brand,
        'BrandIDs': BrandIDs,
        'ColourID': ColourID,
        'subCategoryID': subCategoryID,
        'page_obj': page_obj,
        'no_products': not products.exists(), 
        'query': query,   
        'items_per_page': items_per_page, 
    }
    return render(req, 'search/search_results.html', context)

#Your_Order
@login_required
def Your_Order(request):
    uid = request.session.get('_auth_user_id')
    user = User.objects.get(pk=uid)
    order = Order.objects.filter(user=user)
    context = {
        'current_page': 'order',
        'order': order,
    }
    return render(request, 'order/order.html', context)


#Cancel Order
@login_required
def cancel_order(request, order_id):
    uid = request.session.get('_auth_user_id')
    user = get_object_or_404(User, pk=uid)
    order = get_object_or_404(Order, id=order_id, user=user)
    if request.method == 'POST':
        if 'confirm' in request.POST:
            try:
                product = Product.objects.get(product_name=order.product_name)
                product.availability += order.quantity
                product.save()
                order.delete()
            except Product.DoesNotExist:
                messages.error(request, 'Product does not exist.')
                return redirect('order')
            return redirect('order')
        else:
            return redirect('order')

    context = {
        'order': order,
    }
    return render(request, 'order/confirm_cancel.html', context)

#Admin
@login_required
@user_passes_test(is_admin)
def ADMIN_HOME(req):
    sliders = slider.objects.all().order_by('-id')
    banners = banner_area.objects.all().order_by('-id')

    
    main_category_query = req.GET.get('main_category_query', '')
    category_query = req.GET.get('category_query', '')
    sub_category_query = req.GET.get('sub_category_query', '')

    main_category = Main_category.objects.filter(name__icontains=main_category_query).order_by('-id')
    category = Category.objects.filter(
        Q(name__icontains=category_query) | 
        Q(main_category__name__icontains=category_query)
    )
    sub_category = Sub_category.objects.filter(
        Q(name__icontains=sub_category_query) | 
        Q(category__name__icontains=sub_category_query) | 
        Q(category__main_category__name__icontains=sub_category_query)
    )

    grouped_categories = {}
    for cat in category:
        main_cat_name = cat.main_category.name
        if main_cat_name not in grouped_categories:
            grouped_categories[main_cat_name] = []
        grouped_categories[main_cat_name].append(cat)

    grouped_sub_categories = {}
    for sub_cat in sub_category:
        main_cat_name = sub_cat.category.main_category.name
        cat_name = sub_cat.category.name
        if main_cat_name not in grouped_sub_categories:
            grouped_sub_categories[main_cat_name] = {}
        if cat_name not in grouped_sub_categories[main_cat_name]:
            grouped_sub_categories[main_cat_name][cat_name] = []
        grouped_sub_categories[main_cat_name][cat_name].append(sub_cat)

    product = Product.objects.filter(section__name='Top Deal of The Day')

    context = {
        'current_page': 'home',
        'sliders': sliders,
        'banners': banners,
        'main_category': main_category,
        'category': category,
        'grouped_categories': grouped_categories,
        'grouped_sub_categories': grouped_sub_categories,
        'product': product,
        'main_category_query': main_category_query,
        'category_query': category_query,
        'sub_category_query': sub_category_query,

    }
    return render(req, 'administrators/admin_home/admin_home.html', context)

#Slider
def add_slider(request):
    if request.method == 'POST':
        form = SliderForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_home')
    else:
        form = SliderForm()
    return render(request, 'administrators/admin_home/slider/add_slider.html', {'form': form})

def edit_slider(request, id):
    slider_instance = get_object_or_404(slider, id=id)
    if request.method == 'POST':
        form = SliderForm(request.POST, request.FILES, instance=slider_instance)
        if form.is_valid():
            form.save()
            return redirect('admin_home')
    else:
        form = SliderForm(instance=slider_instance)
    return render(request, 'administrators/admin_home/slider/edit_slider.html', {'form': form})

def delete_slider(request, id):
    slider_instance = get_object_or_404(slider, id=id)
    if request.method == 'POST':
        slider_instance.delete()
        return redirect('admin_home')
    return render(request, 'administrators/admin_home/slider/delete_slider.html', {'slider': slider_instance})

#banner
def manage_banners(request):
    banners = banner_area.objects.all()
    return render(request, 'administrators/admin_home/admin_home.html', {'banners': banners})

def add_banner(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manage_banners')
    else:
        form = BannerForm()
    return render(request, 'administrators/admin_home/banner/add_banner.html', {'form': form})

def edit_banner(request, pk):
    banner = get_object_or_404(banner_area, pk=pk)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            return redirect('manage_banners')
    else:
        form = BannerForm(instance=banner)
    return render(request, 'administrators/admin_home/banner/edit_banner.html', {'form': form})

def delete_banner(request, pk):
    banner = get_object_or_404(banner_area, pk=pk)
    if request.method == 'POST':
        banner.delete()
        return redirect('manage_banners')
    return render(request, 'administrators/admin_home/banner/delete_banner.html', {'banner': banner})

#Main category
def add_main_category(request):
    if request.method == 'POST':
        form = MainCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_home')
    else:
        form = MainCategoryForm()
    return render(request, 'administrators/admin_home/category/main_category/add_main_category.html', {'form': form})

def edit_main_category(request, pk):
    main_category = get_object_or_404(Main_category, pk=pk)
    if request.method == 'POST':
        form = MainCategoryForm(request.POST, instance=main_category)
        if form.is_valid():
            form.save()
            return redirect('admin_home')
    else:
        form = MainCategoryForm(instance=main_category)
    return render(request, 'administrators/admin_home/category/main_category/edit_main_category.html', {'form': form})

def delete_main_category(request, pk):
    main_category = get_object_or_404(Main_category, pk=pk)
    if request.method == 'POST':
        main_category.delete()
        return redirect('admin_home')
    return render(request, 'administrators/admin_home/category/main_category/delete_main_category.html', {'main_category': main_category})

#Category
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_home')
    else:
        form = CategoryForm()
    return render(request, 'administrators/admin_home/category/category/add_category.html', {'form': form})

def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('admin_home')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'administrators/admin_home/category/category/edit_category.html', {'form': form})

def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('admin_home')
    return render(request, 'administrators/admin_home/category/category/delete_category.html', {'category': category})

#Sub_Category
def add_sub_category(request):
    if request.method == 'POST':
        form = SubCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sub-category added successfully!')
            return redirect('add_sub_category')
    else:
        form = SubCategoryForm()
    return render(request, 'administrators/admin_home/category/sub_category/add_sub_category.html', {'form': form})


def edit_sub_category(request, pk):
    sub_category = get_object_or_404(Sub_category, pk=pk)
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, instance=sub_category)
        if form.is_valid():
            form.save()
            return redirect('admin_home')
    else:
        form = SubCategoryForm(instance=sub_category)
    return render(request, 'administrators/admin_home/category/sub_category/edit_sub_category.html', {'form': form})

def delete_sub_category(request, pk):
    sub_category = get_object_or_404(Sub_category, pk=pk)
    if request.method == 'POST':
        sub_category.delete()
        return redirect('admin_home')
    return render(request, 'administrators/admin_home/category/sub_category/delete_sub_category.html', {'sub_category': sub_category})


#Products
@login_required
@user_passes_test(is_admin)
def manage_products(request):
    sections = Section.objects.all()
    colours = Colour.objects.all()
    brands = Brand.objects.all()
    products = Product.objects.all()
    product_images = Product_Image.objects.all()
    additional_info_by_product = Additional_information.objects.select_related('product').all()

    additional_info_grouped = {}
    for info in additional_info_by_product:
        product_name = info.product.product_name
        if product_name not in additional_info_grouped:
            additional_info_grouped[product_name] = []
        additional_info_grouped[product_name].append(info)

    context = {
        'current_page': 'manage_products',
        'sections': sections,
        'colours': colours,
        'brands': brands,
        'products': products,
        'product_images': product_images,
        'additional_info_grouped': additional_info_grouped,
    }
    return render(request, 'administrators/products/manage_products.html', context)

#Section
@login_required
@user_passes_test(is_admin)
def add_section(req):
    if req.method == 'POST':
        form = SectionForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_products')
    else:
        form = SectionForm()
    return render(req, 'administrators/products/section/add_section.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def edit_section(req, id):
    section = get_object_or_404(Section, id=id)
    if req.method == 'POST':
        form = SectionForm(req.POST, instance=section)
        if form.is_valid():
            form.save()
            return redirect('manage_products')
    else:
        form = SectionForm(instance=section)
    return render(req, 'administrators/products/section/edit_section.html', {'form': form, 'section': section})

@login_required
@user_passes_test(is_admin)
def delete_section(req, id):
    section = get_object_or_404(Section, id=id)
    if req.method == 'POST':
        section.delete()
        return redirect('manage_products')
    return render(req, 'administrators/products/section/delete_section.html', {'section': section})

#Colour
@login_required
@user_passes_test(is_admin)
def add_colour(req):
    if req.method == 'POST':
        form = ColourForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_products')
    else:
        form = ColourForm()
    return render(req, 'administrators/products/colour/add_colour.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def edit_colour(req, id):
    colour = get_object_or_404(Colour, id=id)
    if req.method == 'POST':
        form = ColourForm(req.POST, instance=colour)
        if form.is_valid():
            form.save()
            return redirect('manage_products')
    else:
        form = ColourForm(instance=colour)
    return render(req, 'administrators/products/colour/edit_colour.html', {'form': form, 'colour': colour})

@login_required
@user_passes_test(is_admin)
def delete_colour(req, id):
    colour = get_object_or_404(Colour, id=id)
    if req.method == 'POST':
        colour.delete()
        return redirect('manage_products')
    return render(req, 'administrators/products/colour/delete_colour.html', {'colour': colour})

#Brand
@login_required
@user_passes_test(is_admin)
def add_brand(req):
    if req.method == 'POST':
        form = BrandForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_products')
    else:
        form = BrandForm()
    return render(req, 'administrators/products/brand/add_brand.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def edit_brand(req, id):
    brand = get_object_or_404(Brand, id=id)
    if req.method == 'POST':
        form = BrandForm(req.POST, instance=brand)
        if form.is_valid():
            form.save()
            return redirect('manage_products')
    else:
        form = BrandForm(instance=brand)
    return render(req, 'administrators/products/brand/edit_brand.html', {'form': form, 'brand': brand})

@login_required
@user_passes_test(is_admin)
def delete_brand(req, id):
    brand = get_object_or_404(Brand, id=id)
    if req.method == 'POST':
        brand.delete()
        return redirect('manage_products')
    return render(req, 'administrators/products/brand/delete_brand.html', {'brand': brand})


# Add Product
@login_required
@user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            product_form.save()
            return redirect('manage_products') 
    else:
        product_form = ProductForm()
    
    return render(request, 'administrators/products/product/add_product.html', {
        'product_form': product_form,
    })

@login_required
@user_passes_test(is_admin)
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        
        if product_form.is_valid():
            additional_stock = request.POST.get('additional_stock', 0)
            additional_stock = int(additional_stock)
            product = product_form.save(commit=False)
            product.total_quantity += additional_stock
            product.availability += additional_stock
            product.save()
            return redirect('manage_products') 
    else:
        product_form = ProductForm(instance=product)

    return render(request, 'administrators/products/product/edit_product.html', {
        'product_form': product_form,
    })



@login_required
@user_passes_test(is_admin)
def delete_product(req, id):
    product = get_object_or_404(Product, id=id)
    if req.method == 'POST':
        product.delete()
        return redirect('manage_products')
    return render(req, 'administrators/products/product/delete_product.html', {'product': product})


#Product Images
# add_product_image
@login_required
@user_passes_test(is_admin)
def add_product_image(request):
    if request.method == 'POST':
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manage_products')  
    else:
        form = ProductImageForm()
    
    return render(request, 'administrators/products/product_image/add_product_image.html', {'form': form})

#auto_complete
@login_required
@user_passes_test(is_admin)
def product_autocomplete(request):
    if 'term' in request.GET:
        term = request.GET['term']
        products = Product.objects.filter(product_name__icontains=term).values('id', 'product_name')
        return JsonResponse(list(products), safe=False)
    return JsonResponse([], safe=False)

# edit_product_image
@login_required
@user_passes_test(is_admin)
def edit_product_image(request, image_id):
    image = get_object_or_404(Product_Image, id=image_id)
    
    if request.method == 'POST':
        form = ProductImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            return redirect('manage_products')  
    else:
        form = ProductImageForm(instance=image)
    
    return render(request, 'administrators/products/product_image/edit_product_image.html', {'form': form})

#delete_product_image
@login_required
@user_passes_test(is_admin)
def delete_product_image(request, image_id):
    image = get_object_or_404(Product_Image, id=image_id)
    
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Product image deleted successfully.')
        return redirect('manage_products')
    
    return render(request, 'administrators/products/product_image/delete_product_image.html', {'image': image})

#addional information
@login_required
@user_passes_test(is_admin)
def add_additional_information(request):
    if request.method == 'POST':
        form = AdditionalInformationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_products')   
    else:
        form = AdditionalInformationForm()
    
    return render(request, 'administrators/products/additonal_information/add_additional_information.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def delete_additional_information(request, id):
    additional_info = get_object_or_404(Additional_information, id=id)
    if request.method == 'POST':
        additional_info.delete()
        return redirect('manage_products')  
    
    return render(request, 'administrators/products/additonal_information/delete_additional_information.html', {'additional_info': additional_info})

#Orders
@login_required
@user_passes_test(is_admin)
def all_Orders(request):
    orders = Order.objects.all()
    context = {
        'current_page': 'all_orders',
        'orders': orders
    }
    return render(request, 'administrators/orders/all_orders.html', context)

@login_required
@user_passes_test(is_admin)
def product_images(req):
   
    products_with_images = Product.objects.prefetch_related('product_image_set').all()
    context = {
        'products_with_images': products_with_images
    }
    return render(req, 'administrators/products/product_images/product_image.html', context)

def order_success(request):
    return render(request, 'checkout/order_success.html')

@login_required
def Delivery_orders(request):
    if not request.user.groups.filter(id=3).exists():
        return HttpResponseForbidden("You do not have permission to view this page.")
    
    postcode = request.GET.get('postcode')
    if postcode:
        orders = Order.objects.filter(
            postcode=postcode,
            order_status__in=["Order Out for Delivery", "Product Delivered"]
        )
    else:
        orders = Order.objects.filter(
            order_status__in=["Order Out for Delivery", "Product Delivered"]
        )
    
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'current_page': 'delivery_orders',
        'orders': orders,
        'postcode': postcode,
        'notifications': notifications,
    }
    return render(request, 'delivery/orders/delivery_orders.html', context)

@login_required
def deliver_order(request, order_id):
    if not request.user.groups.filter(id=3).exists():
        return HttpResponseForbidden("You do not have permission to perform this action.")
    
    order = get_object_or_404(Order, id=order_id)
    order.order_status = "Product Delivered"
    order.save()
    
   
    Notification.objects.create(
        user=request.user,
        message=f"Order ID {order_id} has been delivered. Check the delivery orders."
    )

    
    return redirect('delivery_orders')
    

@login_required
def sales_orders(request,):
    if not request.user.groups.filter(id=4).exists():
        return HttpResponseForbidden("You do not have permission to perform this action.")
    postcode = request.GET.get('postcode')
    if postcode:
        orders = Order.objects.filter(postcode=postcode)
    else:
        orders = Order.objects.all()
    context = {
        'current_page': 'sales_orders',
        'orders': orders,
        'postcode': postcode,
    }
    return render(request,'sales/sales_orders.html',context)

@login_required
def dispatch_order(request, order_id):
    if not request.user.groups.filter(id=4).exists():
        return HttpResponseForbidden("You do not have permission to perform this action.")
    
    order = get_object_or_404(Order, id=order_id)
    order.order_status = "Order Dispatched"
    order.save()
    return JsonResponse({'status': 'success'})

@login_required
def out_for_delivery_order(request, order_id):
    if not request.user.groups.filter(id=4).exists():
        return HttpResponseForbidden("You do not have permission to perform this action.")
    
    order = get_object_or_404(Order, id=order_id)
    order.order_status = "Order Out for Delivery"
    order.save()
    
   
    delivery_users = User.objects.filter(groups__id=3)  
    for user in delivery_users:
        Notification.objects.create(
            user=user,
            message=f"Order ID {order_id} is now Out for Delivery. Check the delivery orders."
        )
    
    return JsonResponse({'status': 'success'})

def mark_notifications_as_read(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    notifications.update(is_read=True)
    return redirect('delivery_orders')



@login_required
def Apply_job(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            job_application = form.save(commit=False)
            job_application.user = request.user
            job_application.save()
            
           
            admin_group = Group.objects.get(id=1)
            admin_users = User.objects.filter(groups=admin_group)
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    job_application=job_application,
                    message=f"The user {request.user.username} has sent a job application for {job_application.type_of_job}."
                )
            
            return redirect('success_page') 
        else:
            
            print(form.errors)
    else:
        form = JobApplicationForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'date_of_birth': '',
            'phone_number': '',
            'address': '',
            'educational_qualification': '',
            'type_of_job': '',
        })

    return render(request, 'apply_job.html', {'form': form})


@login_required
def job_application_detail(request, application_id):
    job_application = Job_application.objects.get(id=application_id)
    return render(request, 'job_application_detail.html', {'job_application': job_application})

@login_required
def accept_job_application(request, application_id):
    job_application = Job_application.objects.get(id=application_id)
    user = job_application.user
    if job_application.type_of_job == 'delivery':
        group = Group.objects.get(id=3)  
    elif job_application.type_of_job == 'sales':
        group = Group.objects.get(id=4)  
    
    user.groups.clear()
    user.groups.add(group)
    user.save()

    job_application.delete()  
    return redirect('admin_notification')

@login_required
def reject_job_application(request, application_id):
    job_application = Job_application.objects.get(id=application_id)
    job_application.delete()  
    return redirect('admin_notification')

@login_required
def success_page(request):
    return render(request, 'success.html')