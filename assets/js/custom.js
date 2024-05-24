let autocomplete;

function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
        types: ['geocode', 'establishment'],
        //default in this app is "IN" - add your country code
        componentRestrictions: {'country': ['in']},
    })
// function to specify what should happen when the prediction is clicked
autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged (){
    var place = autocomplete.getPlace();

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    else{
        // console.log('place name=>', place.name)
    }

    // get the address components and assign them to the fields
    // console.log(place);
    var geocoder = new google.maps.Geocoder()
    var address = document.getElementById('id_address').value

    geocoder.geocode({'address': address}, function(results, status){

        if(status == google.maps.GeocoderStatus.OK){
            var latitude = results[0].geometry.location.lat();
            var longitude = results[0].geometry.location.lng();

            $('#id_latitude').val(latitude);
            $('#id_longitude').val(longitude);

            $('#id_address').val(address);
        }
    });

    // loop through the address components and assign other address data
    console.log(place.address_components);
    for(var i=0; i<place.address_components.length; i++){
        for(var j=0; j<place.address_components[i].types.length; j++){
            // get country
            if(place.address_components[i].types[j] == 'country'){
                $('#id_country').val(place.address_components[i].long_name);
            }
            // get state
            if(place.address_components[i].types[j] == 'administrative_area_level_1'){
                $('#id_state').val(place.address_components[i].long_name);
            }
            // get city
            if(place.address_components[i].types[j] == 'locality'){
                $('#id_city').val(place.address_components[i].long_name);
            }
            // get pincode
            if(place.address_components[i].types[j] == 'postal_code'){
                $('#id_pin_code').val(place.address_components[i].long_name);
            }else{
                $('#id_pin_code').val("");
            }
        }
    }
}

$(document).ready(function() {

    // delete the cart element if the qty is 0
    function removeCartItem(cartItemQty, cartId) {
        if (cartItemQty <= 0) {
            document.getElementById(`cart-item-${cartId}`).remove();
        }
    }

    function checkCartCounter() {
        const cartCounter = document.getElementById('cart-counter').innerHTML;
        console.log(cartCounter)

        if (cartCounter == 0) {
            document.getElementById('empty-cart').style.display = 'block';
        }
    }

    function applyCartAmounts(sub_total, tax, grant_total) {
        $("#sub_total").html(sub_total);
        $("#tax").html(tax);
        $("#grand_total").html(grant_total);

    }

    $('.item-qty').each(function() {
        const id = $(this).attr('id');
        const qty = $(this).attr('data-qty');
        $(`#${id}`).html(qty);
    })

    $('.add-to-cart').on('click', function(e) {
        e.preventDefault();

        const food_id = $(this).attr('data-id');
        const url = $(this).attr('data-url');

        const data = {
            'food_id': food_id,
        }

        $.ajax({
            type: 'GET',
            url: url,
            data: data,
            success: function (response) {
                console.log(response);
                if (response.status === 'success') {
                    $("#cart-counter").html(response.cart_counter["cart_counter"]);
                    $(`#qty-${food_id}`).html(response.qty);
                    applyCartAmounts(response.cart_amounts["sub_total"], response.cart_amounts["tax"], response.cart_amounts["grand_total"]);
                } else if (response.status === 'failed') {
                    Swal.fire({
                        title: 'Failure',
                        text: response.message,
                        icon: 'error'
                    });
                } else {
                    Swal.fire({
                        title: 'Login',
                        text: response.message,
                        icon: 'warning'
                    }).then(function () {
                        window.location = '/accounts/login';
                    });
                }
            }
        })
    })
    $('.decrease-from-cart').on('click', function(e) {
        e.preventDefault();

        const food_id = $(this).attr('data-id');
        const cart_id = $(this).attr('cart-id');
        const url = $(this).attr('data-url');

        const data = {
            'food_id': food_id,
        }

        $.ajax({
            type: 'GET',
            url: url,
            data: data,
            success: function(response) {
                if (response.status === 'success') {
                    $(`#qty-${food_id}`).html(response.qty);
                    $("#cart-counter").html(response.cart_counter["cart_counter"]);
                    removeCartItem(response.qty, cart_id);
                    checkCartCounter();
                    applyCartAmounts(response.cart_amounts["sub_total"], response.cart_amounts["tax"], response.cart_amounts["grand_total"]);
                } else if (response.status === 'failed') {
                    Swal.fire({
                        title: 'Failure',
                        text: response.message,
                        icon: 'error'
                    });
                } else {
                    Swal.fire({
                        title: 'Login',
                        text: response.message,
                        icon: 'warning'
                    }).then(function () {
                        window.location = '/accounts/login';
                    });
                }
            }

        })
    })
    $(".delete-cart").on('click', function(e) {
        e.preventDefault();

        const cart_id = $(this).attr('data-id');
        const url = $(this).attr('data-url');

        const data = {
            'cart_id': cart_id,
        }

        $.ajax({
            type: "GET",
            url: url,
            data: data,
            success: function(response) {
                if (response.status === 'success') {
                    Swal.fire({
                        title: response.status,
                        text: response.message,
                        icon: 'success'
                    });

                    $("#cart-counter").html(response.cart_counter["cart_counter"]);
                    removeCartItem(0, cart_id);
                    checkCartCounter();
                    applyCartAmounts(response.cart_amounts["sub_total"], response.cart_amounts["tax"], response.cart_amounts["grand_total"]);
                } else if (response.status === 'failed') {
                    Swal.fire({
                        title: "Failure",
                        text: response.message,
                        icon: "error"
                    });
                }
            }
        })
    })
})