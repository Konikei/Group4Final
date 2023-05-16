from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from mysite import settings
from django.core.mail import send_mail
from .models import *
from .models import User, Order

# Create your views here.
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
        
        if len(username)>10:
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
        
    return render(request, "authentication/signin.html")
           
def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('home')


def account(request):
    context = {}
    return render(request, 'authentication/account.html', context)

def shopnow(request):
    messages.success(request, "Shop now")
    return render(request, 'shoppingpage/store.html')

def store(request):
    products = Product.objects.all()
    context = {'products':products}
    return render(request, 'shoppingpage/store.html', context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer 
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
    context = {'items':items, 'order':order}
    return render(request, 'shoppingpage/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()

        if request.method == 'POST':
            payment_method = request.POST.get('payment_method')
            if payment_method == 'cash':
                cash_total = sum([item.get_total for item in items])
                if customer.cash_available >= cash_total:
                    customer.cash_available -= cash_total
                    customer.save()
                    messages.success(request, f'Payment of ${cash_total:.2f} successful.')
                else:
                    messages.error(request, 'Insufficient cash available for payment.')

            elif payment_method == 'points':
                points_total = sum([item.get_total for item in items if item.payment_method == 'points'])
                if customer.points >= points_total:
                    customer.points -= points_total
                    customer.save()
                    messages.success(request, f'Payment of {points_total} points successful.')
                else:
                    messages.error(request, 'Insufficient points available for payment.')

            order.complete = True
            order.save()
            return redirect('home')
        
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}

    context = {'items': items, 'order': order}
    return render(request, 'shoppingpage/checkout.html', context)

def credit(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            amount = request.POST.get('amount')
            
            try:
                amount = float(amount)
                if amount > 0:
                    customer = request.user.customer
                    
                    if customer.cash_available >= amount:
                        customer.cash_available -= amount
                        customer.save()
                        
                        messages.success(request, f"Successfully credited {amount} to your account!")
                        return redirect('account')
                    else:
                        messages.error(request, "Insufficient funds")
                else:
                    messages.error(request, "Invalid transaction amount!")
            except ValueError:
                messages.error(request, "Invalid transaction amount")
        
    else:
        return redirect('home')
    
    return render(request, 'shoppingpage/credit.html')

def point(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            quantity = request.POST.get('quantity')
            
            try:
                quantity = int(quantity)
                if quantity > 0:
                    customer = request.user.customer
                    
                    if customer.points >= quantity:
                        customer.points -= quantity
                        customer.save()
                        
                        messages.success(request, f"Successfully redeemed {quantity} points")
                        return redirect('account')
                    else:
                        messages.error(request, "Insufficient points")
                else:
                    messages.error(request, "Invalid transaction quantity")
            except ValueError:
                messages.error(request, "Invalid transaction quantity")
        
    else:
        return redirect('home')
    
    return render(request, 'shoppingpage/point.html')
