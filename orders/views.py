import simplejson as json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

from accounts.utils import send_notification_email
from marketplace import context_processors as market_context_processors
from marketplace import models as market_models
from orders import forms as orders_forms
from orders import models as orders_models
from orders.utils import generate_order_number

import simplejson as json

# Create your views here.


@login_required(login_url="login")
def place_order(request):
    cart_items = market_models.Cart.objects.filter(user=request.user)
    if cart_items.count() <= 0:
        return redirect("marketplace")

    sub_total = market_context_processors.get_cart_amounts(request)["sub_total"]
    tax_data = market_context_processors.get_cart_amounts(request)["tax_dict"]
    total_tax = market_context_processors.get_cart_amounts(request)["tax"]
    grand_total = market_context_processors.get_cart_amounts(request)["grand_total"]

    form = orders_forms.OrderForm()

    if request.method == "POST":
        form = orders_forms.OrderForm(request.POST)
        if form.is_valid():
            order = orders_models.Order()
            order.user = request.user
            order.first_name = form.cleaned_data["first_name"]
            order.last_name = form.cleaned_data["last_name"]
            order.phone = form.cleaned_data["phone"]
            order.email = form.cleaned_data["email"]
            order.address = form.cleaned_data["address"]
            order.country = form.cleaned_data["country"]
            order.state = form.cleaned_data["state"]
            order.city = form.cleaned_data["city"]
            order.pin_code = form.cleaned_data["pin_code"]
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_tax = total_tax
            order.payment_method = request.POST.get("payment_method")
            order.save()
            order.order_number = generate_order_number(order.id)
            order.save()

            context = {"order": order, "cart_items": cart_items, "sub_total": sub_total}
            return render(request, "orders/place_order.html", context)

    return render(request, "orders/place_order.html")


@login_required(login_url="login")
def payment(request):
    if (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        and request.method == "POST"
    ):
        order_number = request.POST.get("order_number")
        transaction_id = request.POST.get("transaction_id")
        payment_method = request.POST.get("payment_method")
        status = request.POST.get("status")

        order = orders_models.Order.objects.get(
            user=request.user, order_number=order_number
        )
        # create the payment
        payment = orders_models.Payment.objects.create(
            user=request.user,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=order.total,
            status=status,
        )
        payment.save()

        # add payment to order instance
        order.payment = payment
        order.is_ordered = True
        order.save()

        # move the cart items to ordered food model
        cart_items = market_models.Cart.objects.filter(user=request.user)
        for cart_item in cart_items:
            ordered_food = orders_models.OrderedFood.objects.create(
                order=order,
                payment=payment,
                user=request.user,
                food_item=cart_item.food_item,
                quantity=cart_item.quantity,
                price=cart_item.food_item.price,
                amount=cart_item.food_item.price * cart_item.quantity,
            )
            ordered_food.save()

        # send notification email to the customer
        mail_subject = "Thank you for ordering with us."
        email_template = "emails/order_confirmation_email.html"

        context = {"user": request.user, "order": order, "to_email": order.email}

        send_notification_email(
            mail_subject=mail_subject, email_template=email_template, context=context
        )

        # send notification email to vendors
        mail_subject = "You have received a new order."
        email_template = "emails/new_order_received.html"

        to_email = []
        for cart_item in cart_items:
            if cart_item.food_item.vendor.user.email not in to_email:
                to_email.append(cart_item.food_item.vendor.user.email)

        context = {"order": order, "to_email": to_email}

        send_notification_email(
            mail_subject=mail_subject, email_template=email_template, context=context
        )

        # delete the cart item if the payment is successful
        cart_items.delete()

        response = {
            'order_number': order_number,
            'transaction_id': transaction_id,
        }

        return JsonResponse(response)


def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('tx_id')

    try:
        order = orders_models.Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = orders_models.OrderedFood.objects.filter(order=order)

        sub_total = 0
        for item in ordered_food:
            sub_total += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)

        context = {
            'order': order,
            'ordered_food': ordered_food,
            'sub_total': sub_total,
            'tax_data': tax_data
        }

        return render(request, 'orders/order_complete.html', context)

    except orders_models.Order.DoesNotExist:
        return redirect('index')

