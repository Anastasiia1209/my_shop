from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from orders.models import OrderItem
from reviews.forms import ReviewForm
from reviews.models import Review

from .models import Category, Product

SORT_OPTIONS = {
    "price_asc": "price",
    "price_desc": "-price",
    "newest": "-created_at",
    "popular": "-review_count",
}

PURCHASED_STATUSES = ["paid", "shipped", "delivered"]


def catalog(request: HttpRequest) -> HttpResponse:
    products = Product.objects.active().select_related("category").with_rating()

    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    category_slug = request.GET.get("category")
    if category_slug:
        products = products.filter(category__slug=category_slug)

    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort = request.GET.get("sort", "newest")
    products = products.order_by(SORT_OPTIONS.get(sort, "-created_at"))

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "categories": Category.objects.filter(parent__isnull=True).prefetch_related("children"),
        "query": query,
        "sort": sort,
        "selected_category": category_slug,
        "min_price": min_price or "",
        "max_price": max_price or "",
    }
    return render(request, "products/catalog.html", context)


def product_detail(request: HttpRequest, slug: str) -> HttpResponse:
    product = get_object_or_404(
        Product.objects.select_related("category").with_rating(), slug=slug, is_active=True
    )
    reviews = product.reviews.select_related("user").all()

    can_review = False
    already_reviewed = False
    if request.user.is_authenticated:
        can_review = OrderItem.objects.filter(
            order__user=request.user, product=product, order__status__in=PURCHASED_STATUSES
        ).exists()
        already_reviewed = Review.objects.filter(product=product, user=request.user).exists()

    review_form = ReviewForm() if (can_review and not already_reviewed) else None

    context = {
        "product": product,
        "reviews": reviews,
        "can_review": can_review and not already_reviewed,
        "already_reviewed": already_reviewed,
        "review_form": review_form,
    }
    return render(request, "products/detail.html", context)


@login_required
def add_review(request: HttpRequest, slug: str) -> HttpResponse:
    product = get_object_or_404(Product, slug=slug)
    purchased = OrderItem.objects.filter(
        order__user=request.user, product=product, order__status__in=PURCHASED_STATUSES
    ).exists()

    if not purchased:
        messages.error(request, "Залишити відгук можна лише після покупки товару.")
        return redirect(product.get_absolute_url())

    if Review.objects.filter(product=product, user=request.user).exists():
        messages.info(request, "Ви вже залишили відгук на цей товар.")
        return redirect(product.get_absolute_url())

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Дякуємо за ваш відгук!")
        else:
            messages.error(request, "Перевірте правильність заповнення форми.")
    return redirect(product.get_absolute_url())
