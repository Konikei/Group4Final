from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Order, Product
from .forms import OrderForm, ShopForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse

def home(request):
    return render(request, 'authentication/home.html', {})

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username")
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request, "Email already registered!")
            return redirect('home')

        if len(username) > 10:
            messages.error(request, "Username must be under 10 charaters")

        if pass1 != pass2:
            messages.error(request, "Passwords did not match!")

        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric")
            return redirect('home')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname

        myuser.save()

        messages.success(request, "Your account has been successfully created")

        return redirect('signin')

    return render(request, "authentication/signup.html")


def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "authentication/home.html", {'fname': fname})
        else:
            messages.error(request, "Bad Credentials!")
            return redirect('home')

    return render(request, 'authentication/signin.html')


def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('home')

def store(request):
    products = Product.objects.all()
    context = {'products':products}
    return render(request, 'shoppingpage/store.html', context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        points_balance = request.user.profile.points
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
        points_balance = 0
    context = {'items':items, 'order':order, 'points_balance': points_balance}
    return render(request, 'shoppingpage/cart.html', context)


def update_cart(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            product_id = request.POST.get('productId')
            action = request.POST.get('action')

            # Retrieve the user's cart
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)

            if action == 'add':
                order.add_to_cart(product_id)
            elif action == 'remove':
                order.remove_from_cart(product_id)
            else:
                pass

            cart_total = order.get_cart_total()
            cart_items_count = order.get_cart_items_count()
            points_balance = request.user.profile.points

            data = {
                'message': 'Cart updated successfully.',
                'cart_total': cart_total,
                'cart_items_count': cart_items_count,
                'points_balance': points_balance,
            }
            return JsonResponse(data)
        else:
            pass

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()

        cash_spent = order.get_cart_total()

        if cash_spent < 20:
            points_earned = 10
        else:
            points_earned = 12

        user = request.user
        user.profile.points += points_earned
        user.profile.save()

        points_balance = user.profile.points

    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        points_balance = 0

    context = {'items': items, 'order': order, 'points_balance': points_balance}
    return render(request, 'shoppingpage/checkout.html', context)

def create_order(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.recipient = f"{request.user.last_name}, {request.user.first_name}"
            order.ordered_by = request.user
            order.save()
            messages.success(request, "Order created successfully!")
            return redirect('orders')
    else:
        form = OrderForm()
        context = {'form': form}
        return render(request, 'create_order.html', context)


def account(request):
    user = request.user
    context = {
        'username': user.username,
        'fname': user.first_name,
        'lname': user.last_name,
        'email': user.email,
        'cash_available': 50.00,
        'points': 0,
    }
    return render(request, 'authentication/account.html', context)
