from django.shortcuts import render, redirect

# Create your views here.
from .forms import productForm
from .models import Product

#CRUD

#home view
def home_view(request):
    return render(request, 'invApp/home.html' )

#create view
def product_create_view(request):
    form = productForm()
    if request.method == 'POST':
        form = productForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')

    return render(request, 'invapp/product_form.html', {'form':form})

#Read view
def product_list_view(request):
    products = Product.objects.all()
    return render(request, 'invApp/product_list.html', {'products':products})

#Update view 
def product_update_view(request, product_id):
    product=Product.objects.get(product_id=product_id)
    form = productForm(instance=product)
    if request.method == "POST":
        form=productForm(request.POST, instance=product )
        if form.is_valid():
            form.save()
            return redirect('product_list')

    return render(request, 'invapp/product_form.html', {'form':form})

#Delete View
def product_delete_view(request, product_id):
    product = Product.objects.get(product_id = product_id)
   #The first url link will be GET from the list_section, then from del_confirmation page it will click POST request/
    if request.method == 'POST':
          product.delete()
          return redirect('product_list')
    return render(request, 'invApp/product_confirm_del.html', {'product': product})