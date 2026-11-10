from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

# Create your views here.
from .forms import productForm
from .models import Product

# Auth views
def logout_view(request):
    logout(request)
    return redirect('login')

#CRUD

#home view
@login_required
def home_view(request):
    return render(request, 'invapp/home.html')

#create view
@login_required
def product_create_view(request):
    form = productForm()
    if request.method == 'POST':
        form = productForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')

    return render(request, 'invapp/product_form.html', {'form':form})

#Read view
@login_required
def product_list_view(request):
    products = Product.objects.all()

    # Search by name or SKU
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(sku__icontains=query))

    # Dropdown filter: Supplier
    selected_supplier = request.GET.get('supplier', '').strip()
    if selected_supplier:
        products = products.filter(supplier=selected_supplier)

    # Dropdown filter: Stock Status
    stock_filter = request.GET.get('stock', '').strip()
    if stock_filter == 'in_stock':
        products = products.filter(quantity__gt=0)
    elif stock_filter == 'out_of_stock':
        products = products.filter(quantity=0)

    # Sorting by price and quantity
    sort_by = request.GET.get('sort', '').strip()
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'quantity_asc':
        products = products.order_by('quantity')
    elif sort_by == 'quantity_desc':
        products = products.order_by('-quantity')
    else:
        products = products.order_by('product_id')

    suppliers = Product.objects.values_list('supplier', flat=True).distinct().order_by('supplier')

    # Pagination: 5 products per page
    paginator = Paginator(products, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Preserve GET parameters excluding page for pagination links
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'query': query,
        'selected_supplier': selected_supplier,
        'stock_filter': stock_filter,
        'sort_by': sort_by,
        'suppliers': suppliers,
        'querystring': querystring,
    }
    return render(request, 'invapp/product_list.html', context)

#Update view 
@login_required
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
@login_required
def product_delete_view(request, product_id):
    product = Product.objects.get(product_id = product_id)
   #The first url link will be GET from the list_section, then from del_confirmation page it will click POST request/
    if request.method == 'POST':
          product.delete()
          return redirect('product_list')
    return render(request, 'invApp/product_confirm_del.html', {'product': product})