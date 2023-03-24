from django.conf import settings
from django.shortcuts import render, redirect, reverse
from numpy import squeeze
from store.models import SubCategory, Product
from django.core.paginator import Paginator
from cart.cart import Cart
from store.forms import *
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from rest_framework import viewsets, permissions
from store.serializers import ProductSerializer
from urllib.parse import urlencode
import pandas as pd
import re
import os


# Create your views here.
def products_service(request):
    products = Product.objects.order_by('-public_day')
    result_list = list(products.values('name', 'price', 'image', 'public_day'))
    return JsonResponse(result_list, safe=False)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.order_by('-public_day')
    serializer_class = ProductSerializer
    # permission_classes = [permissions.IsAdminUser]  # Đọc / Ghi
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Chỉ đọc


def product_service(request, pk):
    products = Product.objects.filter(pk=pk).order_by('-public_day')
    result_list = list(products.values('name', 'price', 'image', 'public_day'))[0]
    return JsonResponse(result_list, safe=False)


def index(request):
    cart = Cart(request)

    # Thiết bị gia đình
    tbgd_subcategory = SubCategory.objects.filter(category=1).values_list('id')
    tbgd_list_subcategory = []
    for subcategory in tbgd_subcategory:
        tbgd_list_subcategory.append(subcategory[0])
    tbgd_products = Product.objects.filter(subcategory__in=tbgd_list_subcategory).order_by('-public_day')

    # Đồ dùng nhà bếp
    ddnb_subcategory = SubCategory.objects.filter(category=2).values_list('id')
    ddnb_list_subcategory = []
    for subcategory in ddnb_subcategory:
        ddnb_list_subcategory.append(subcategory[0])
    ddnb_products = Product.objects.filter(subcategory__in=ddnb_list_subcategory).order_by('-public_day')

    return render(request, 'store/index.html', {
        'tbgd_products': tbgd_products[:21],
        'ddnb_products': ddnb_products[:21],
        'cart': cart,
    })


def subcategory(request, pk):
    cart = Cart(request)

    # Đọc danh sách danh mục sản phẩm (subcategory list)
    list_subcategory = SubCategory.objects.order_by('name')
    
    # Đọc danh sách sản phẩm theo danh mục
    if pk == 0:
        products = Product.objects.order_by('-public_day')
        subcategory_name = 'Tất cả sản phẩm (' + str(len(products)) + ')'
    else:
        products = Product.objects.filter(subcategory=pk).order_by('-public_day')
        selected_subcategory = SubCategory.objects.get(pk=pk)
        subcategory_name = selected_subcategory.name + ' (' + str(len(products)) + ')'

    # Lọc giá
    from_price = ''
    to_price = ''
    product_name = ''
    if request.GET.get('from_price'):
        # Gán biến
        from_price = int(request.GET.get('from_price'))
        to_price = int(request.GET.get('to_price'))
        product_name = request.GET.get('product_name')

        if product_name != '':
            products = Product.objects.filter(name__contains=product_name).order_by('price')

        products = [product for product in products if from_price <= product.price <= to_price]  # List comprehension
        subcategory_name = '%i sản phẩm được tìm thấy trong khoảng %s - %s' % (len(products), "{:,}".format(from_price), "{:,}".format(to_price))


    # Phân trang
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 15)
    products_pager = paginator.page(page)

    return render(request, 'store/product-list.html', {
        'list_subcategory': list_subcategory,
        'products': products_pager,
        'subcategory_name': subcategory_name,
        'cart': cart,
        'from_price': from_price,
        'to_price': to_price,
        'product_name': product_name,
    })


def product_detail(request, pk):
    cart = Cart(request)

    # Đọc danh sách danh mục sản phẩm (subcategory list)
    list_subcategory = SubCategory.objects.order_by('name')

    # Sản phẩm
    product = Product.objects.get(pk=pk)

    # Subcategory
    subcategoryid = product.subcategory_id
    related_products = Product.objects.filter(subcategory=subcategoryid).exclude(id=pk).order_by('public_day')

    # Subcategory name
    subcategoryname = SubCategory.objects.get(pk=subcategoryid)

    # Rules
    rules = pd.read_csv(os.path.join(settings.MEDIA_ROOT, 'analysis/rules.csv'), squeeze=True, index_col=0)
    lst = rules.values.tolist()
    
    list_rules = []
    for item in lst:
        if str(pk) in re.findall('\d+[, \d+]*', item[0])[0].split(','):
            list_rules = re.findall('\d+[, \d+]*', item[1])[0].split(',')
    list_asc_products = []
    for i in list_rules:
        list_asc_products.append(Product.objects.get(pk=int(i)))

    return render(request, 'store/product-detail.html', {
        'cart': cart,
        'list_subcategory': list_subcategory,
        'product': product,
        'related_products': related_products,
        'subcategoryid': subcategoryid,
        'subcategoryname': subcategoryname,
        'list_asc_products': list_asc_products,
    })


def contact(request):
    cart = Cart(request)

    return render(request, 'store/contact.html', {
        'cart': cart,
    })


def demo_user(request):
    cart = Cart(request)
    frm_user = FormUser()
    frm_profile = FormUserProfileInfo()
    chuoi_kq_dang_ky = ''
    if request.POST.get('btnDangKy'):
        frm_user = FormUser(request.POST)
        frm_profile = FormUserProfileInfo(request.POST, request.FILES)
        if frm_user.is_valid() and frm_profile.is_valid():
            if frm_user.cleaned_data['password'] == frm_user.cleaned_data['confirm_password']:
                # Ghi vào CSDL
                # User
                user = frm_user.save()
                user.set_password(user.password)
                user.save()

                # UserProfileInfo
                profile = frm_profile.save(commit=False)
                profile.user = user
                profile.save()

                chuoi_kq_dang_ky = '''
                    <div class="alert alert-success alert-dismissible fade show" role="alert">
                        Đã đăng ký thông tin thành công.
                        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                '''

    if request.POST.get('btnDangNhap'):
        # Gán biến
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('store:user')


    return render(request, 'store/user.html', {
        'cart': cart,
        'frm_user': frm_user,
        'frm_profile': frm_profile,
        'chuoi_kq_dang_ky': chuoi_kq_dang_ky,
    })


def logout_user(request):
    logout(request)
    return redirect('store:user')


def search(request):
    cart = Cart(request)

    # Đọc danh sách danh mục sản phẩm (subcategory list)
    list_subcategory = SubCategory.objects.order_by('name')

    # Tìm kiếm
    products = []
    keyword = ''
    result_search = ''
    if request.GET.get('product_name'):
        keyword = request.GET.get('product_name').strip()
        products = Product.objects.filter(name__contains=keyword).order_by('-public_day')
        result_search = '%i sản phẩm với từ khóa "%s"' % (len(products), keyword)

        # Phân trang
        page = request.GET.get('page', 1)
        paginator = Paginator(products, 15)
        products_pager = paginator.page(page)

    # Lọc giá
    from_price = ''
    to_price = ''
    if request.GET.get('from_price'):
        # Gán biến
        from_price = int(request.GET.get('from_price'))
        to_price = int(request.GET.get('to_price'))

        # Chuyển trang về subcategory (id: 0)
        base_url = reverse('store:subcategory', kwargs={'pk': 0})  # <a href="{% url 'store:subcategory' 0 %}"></a>
        query_string = urlencode({
            'from_price': from_price,
            'to_price': to_price,
            'product_name': keyword,
        })
        url = '%s?%s' % (base_url, query_string)
        return redirect(url)


    return render(request, 'store/product-list.html', {
        'products': products_pager,
        'list_subcategory': list_subcategory,
        'cart': cart,
        'subcategory_name': result_search,
        'product_name': keyword,
    })
