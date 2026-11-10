import os
import json
import urllib.request
import urllib.error
from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

# Create your views here.
from .forms import productForm
from .models import Product, AuditLog

def query_groq_chatbot(api_key, conversation_history, products_data):
    url = "https://api.groq.com/openai/v1/chat/completions"
    system_prompt = (
        "You are an AI assistant for this inventory management system.\n"
        "You have access ONLY to the following inventory data:\n"
        f"{json.dumps(products_data, indent=2)}\n\n"
        "STRICT INSTRUCTIONS:\n"
        "1. Answer natural questions about products, stock levels, suppliers, prices, quantities, and SKUs accurately based ONLY on the data above.\n"
        "2. For anything unrelated to the inventory, you MUST reply EXACTLY:\n"
        "\"I can only answer questions about your inventory.\"\n"
        "3. You are strictly read-only. You cannot and must not modify, add, or delete any data. If asked to modify, alter, or delete data, state that you are read-only.\n"
        "4. Be concise and direct."
    )

    api_messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "InventoryChatbot/1.0",
    }
    model = os.environ.get('GROQ_MODEL', 'openai/gpt-oss-120b').strip() or 'openai/gpt-oss-120b'
    payload = {
        "model": model,
        "messages": api_messages,
        "temperature": 0.1,
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip(), None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        return None, f"Groq API returned HTTP {e.code}: {error_body}"
    except urllib.error.URLError as e:
        return None, f"Network error contacting Groq API: {e.reason}"
    except Exception as e:
        return None, f"Error communicating with Groq API: {str(e)}"

def get_product_snapshot(product):
    return {
        'product_id': product.product_id,
        'name': product.name,
        'sku': product.sku,
        'price': float(product.price),
        'quantity': int(product.quantity),
        'supplier': product.supplier,
    }

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
            product = form.save()
            snapshot = get_product_snapshot(product)
            AuditLog.objects.create(
                action=AuditLog.ACTION_CREATE,
                product_id=product.product_id,
                product_name=product.name,
                user=request.user if request.user.is_authenticated else None,
                username=request.user.username if request.user.is_authenticated else 'Anonymous',
                changes={k: {'old': None, 'new': v} for k, v in snapshot.items() if k != 'product_id'},
                product_snapshot=snapshot,
            )
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
    product = Product.objects.get(product_id=product_id)
    form = productForm(instance=product)
    if request.method == "POST":
        old_snapshot = get_product_snapshot(product)
        form = productForm(request.POST, instance=product)
        if form.is_valid():
            updated_product = form.save()
            new_snapshot = get_product_snapshot(updated_product)
            changes = {}
            for field in ['name', 'sku', 'price', 'quantity', 'supplier']:
                if old_snapshot[field] != new_snapshot[field]:
                    changes[field] = {'old': old_snapshot[field], 'new': new_snapshot[field]}
            if changes:
                AuditLog.objects.create(
                    action=AuditLog.ACTION_UPDATE,
                    product_id=updated_product.product_id,
                    product_name=updated_product.name,
                    user=request.user if request.user.is_authenticated else None,
                    username=request.user.username if request.user.is_authenticated else 'Anonymous',
                    changes=changes,
                    product_snapshot=new_snapshot,
                )
            return redirect('product_list')

    return render(request, 'invapp/product_form.html', {'form':form})

#Delete View
@login_required
def product_delete_view(request, product_id):
    product = Product.objects.get(product_id=product_id)
    if request.method == 'POST':
        snapshot = get_product_snapshot(product)
        AuditLog.objects.create(
            action=AuditLog.ACTION_DELETE,
            product_id=product.product_id,
            product_name=product.name,
            user=request.user if request.user.is_authenticated else None,
            username=request.user.username if request.user.is_authenticated else 'Anonymous',
            changes={k: {'old': v, 'new': None} for k, v in snapshot.items() if k != 'product_id'},
            product_snapshot=snapshot,
        )
        product.delete()
        return redirect('product_list')
    return render(request, 'invapp/product_confirm_del.html', {'product': product})

#Audit History View
@login_required
def audit_history_view(request):
    logs = AuditLog.objects.all().order_by('-timestamp')
    paginator = Paginator(logs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'invapp/history.html', {'logs': page_obj})

# AI Inventory Chatbot Views
@login_required
def chatbot_view(request):
    chat_history = request.session.get('chat_history', [])
    error_message = None

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'clear':
            request.session['chat_history'] = []
            return redirect('chatbot')

        user_message = request.POST.get('message', '').strip()
        if user_message:
            api_key = os.environ.get('GROQ_API_KEY', '').strip()
            if not api_key:
                error_message = "Groq API key not configured. Please set the GROQ_API_KEY environment variable."
            else:
                products_data = list(
                    Product.objects.values('product_id', 'name', 'sku', 'price', 'quantity', 'supplier')
                )
                call_history = chat_history[-10:] + [{'role': 'user', 'content': user_message}]
                assistant_reply, err = query_groq_chatbot(api_key, call_history, products_data)
                if err:
                    error_message = err
                else:
                    chat_history.append({'role': 'user', 'content': user_message})
                    chat_history.append({'role': 'assistant', 'content': assistant_reply})
                    request.session['chat_history'] = chat_history[-10:]
                    return redirect('chatbot')

    return render(request, 'invapp/chatbot.html', {
        'chat_history': chat_history[-10:],
        'error_message': error_message,
    })

@login_required
def chatbot_clear_view(request):
    request.session['chat_history'] = []
    return redirect('chatbot')
