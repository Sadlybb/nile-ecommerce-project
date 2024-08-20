console.log('working fine................');

$("#commentForm").submit(function(element){
    element.preventDefault();

    $.ajax({
        data: $(this).serialize(),
        method: $(this).attr("method"),
        url: $(this).attr("action"),
        dataType: "json",
        success: function(response){
            console.log("comment saved to DB....");

            if(response.bool == true){
                $("#review-response").html("Review added successfully.");
                $(".hide-comment-form").hide();

                let _html = '<div class="single-comment justify-content-between d-flex mb-30">';
                _html += '<div class="user justify-content-between d-flex">';
                _html += '<div class="thumb text-center">';
                _html += '<a href="#" class="font-heading text-brand">'+ response.context.user +'</a>';
                _html += '</div>';

                _html += '<div class="desc">';
                _html += '<div class="d-flex justify-content-between mb-10">';
                _html += '<div class="d-flex align-items-center">';
                _html += '<span class="font-xs text-muted">added now</span>';
                _html += '</div>';
                    
                _html += '<div>';
                for(let i = 0; i < response.context.rating; i++ ){
                    _html += '<i class="fas fa-star text-warning"></i>';
                }
                _html += '</div>';

                _html += '</div>';
                _html += '<strong>'+ response.context.title +'</strong>';
                _html += '<hr>';

                _html += '<p class="mb-10">'+ response.context.description +'</p>';

                _html += '</div>';
                _html += '</div>';
                _html += '</div>';
                $(".comment-list").prepend(_html);
            }
        }
    });
});



function bindAddToCartButtons() {
    console.log("add button binded")
    $(".add-to-cart-btn").off("click").on("click", function() {
        let thisVal = $(this);
        let index = thisVal.attr("data-index");

        let quantity = $(".product-quantity-" + index).val();
        let productTitle = $(".product-title-" + index).val();
        let productId = $(".product-id-" + index).val();
        let productPrice = $(".current-product-price-" + index).text();
        let productImage = $(".product-image-" + index).val();

        $.ajax({
            url: '/add-to-cart',
            data: {
                'id': productId,
                'quantity': quantity,
                'title': productTitle,
                'price': productPrice,
                'image': productImage,
                'pk': productId,
            },
            dataType: 'json',
            beforeSend: function() {
                console.log("Adding product to cart...");
            },
            success: function(response) {
                thisVal.html("✔");
                console.log("Product added to cart");
                console.log("total amount: " + $(".cart-total-amount").text() );
                $(".cart-items-count").text(response.totalcartitems);
                $(".cart-total-amount").text(response.cart_total_amount);
                $("#cart-list-index ul").empty();

                response.cartitems.forEach(function(item) {
                    let truncatedTitle = item.title.length > 15 ? item.title.substring(0, 15) + "..." : item.title;

                    $("#cart-list-index ul").append(`
                        <li id="cart-item-${item.id}">
                            <div class="shopping-cart-img">
                                <a href="/products/${item.id}"><img alt="Nest" src="${item.image}" /></a>
                            </div>
                            <div class="shopping-cart-title">
                                <h4><a href="/products/${item.id}">${truncatedTitle}</a></h4>
                                <h3><span  id="item-quantity-${item.id}">${item.quantity} × </span>$${item.price}</h3>
                            </div>
                            <div class="shopping-cart-delete">
                                <a href="#" class="delete-cart-item" data-product="${item.id}"><i class="fi-rs-cross-small"></i></a>
                            </div>
                            
                        </li>
                        

                    `);
                  
                });

                bindDeleteCartButtons(); // Re-bind delete buttons
                bindUpdateCartButtons()
            },
        });
    });
}

function bindDeleteCartButtons() {
    console.log("delete binded");
    $(document).on("click", ".delete-cart-item", function() {
        let productId = $(this).attr("data-product");

        $.ajax({
            url: '/delete-from-cart',
            data: {
                'id': productId,
            },
            dataType: 'json',
            beforeSend: function() {
                console.log("Removing product from cart...");
            },
            success: function(response) {
                console.log("Product removed from cart");
                console.log("total amount: " + response.cart_total_amount );
                $(".cart-total-amount").text(response.cart_total_amount);
                $(".cart-items-count").text(response.totalcartitems);
                // Remove the item from the cart dropdown list
                $(`#cart-item-${productId}`).remove();
                $(`#cart-list-item-${productId}`).remove();
                $(`#checkout-item-${productId}`).remove();
                
                
                
                // Re-bind delete buttons after updating the cart
                bindDeleteCartButtons();
                bindUpdateCartButtons();
                bindAddToCartButtons();
            },
        });
    });
}

function bindUpdateCartButtons() {
    console.log("add button binded")
    
    $(document).on("click", '.update-product', function() {
        let productId = $(this).attr("data-product");
        let productQuantity = $(".product-quantity-" + productId).val();
        let thisVal = $(this);
        let productPrice = $(".current-product-price-" + productId).text();

        $.ajax({
            url: "/update-cart",
            data: {
                "id": productId,
                "quantity": productQuantity,
            },
            dataType: "json",
            beforeSend: function() {
                console.log("Updating product quantity...");
                
            },
            success: function(response) {
                console.log("Product quantity updated");
                console.log("total amount: " + response.cart_total_amount );
                $(".cart-items-count").text(response.totalcartitems);

                $(`.cart-item-subtotal-${productId}`).text((productPrice * productQuantity).toFixed(2))
                $(`#item-quantity-${productId}`).text(productQuantity + " × ");
                $(".cart-total-amount").text(response.cart_total_amount);
                
                
                bindDeleteCartButtons();
                bindUpdateCartButtons();
                bindAddToCartButtons();
            }
        });
    });
}

$(document).ready(function() {
    bindUpdateCartButtons()
    bindDeleteCartButtons(); // Initial bind
    bindAddToCartButtons(); // Initial bind

    
    $(".filter-checkbox, #price-filter-btn").on("click", function() {
        let filterObject = {};

        let minPrice = $("#max_discount_price").attr("min");
        let maxPrice = $("#max_discount_price").val();

        filterObject.min_price = minPrice;
        filterObject.max_price = maxPrice;

        $(".filter-checkbox").each(function() {
            let filterValue = $(this).val();
            let filterKey = $(this).data("filter");

            filterObject[filterKey] = Array.from(
                document.querySelectorAll(`input[data-filter=${filterKey}]:checked`)
            ).map(element => element.value);
        });

        $.ajax({
            url: '/filter-products',
            data: filterObject,
            dataType: 'json',
            beforeSend: function() {
                console.log("Filtering products...");
            },
            success: function(response) {
                console.log("Products successfully filtered.");
                $("#filtered-products").html(response.data);

                bindAddToCartButtons(); // Re-bind after filtering
            },
        });
    });

    $("#max_discount_price").on("blur", function() {
        let minPrice = $(this).attr("min");
        let maxPrice = $(this).attr("max");
        let currentPrice = $(this).val();

        if (currentPrice < parseInt(minPrice) || currentPrice > parseInt(maxPrice)) {
            alert(`Price must be between $${minPrice} and $${maxPrice}`);
            $(this).val(minPrice);
            $("#range").val(minPrice);
            $(this).focus();
            return false;
        }
    });


    $(".make-default-address").on("click", function(){
        let id = $(this).attr("data-address-id")
        let this_val = $(this)

        console.log("id is: " + id)


        $.ajax ({
            url: "/set-default-address",
            data:{
                "id": id,
            },
            dataType: "json",

            success: function(response){
                console.log("Setting address default  ....")

                if (response.boolean == true){

                    $(".check").hide()
                    $(".action_btn").show()

                    $(".check"+id).show()
                    $(".button"+id).hide()
                }
            }

        })
    })


    $(".address-delete-btn").on("click", function(){
        let id = $(this).attr("data-address-delete")

        $.ajax ({
            url: "/delete-address",
            data: {
                "id": id,
            },
            dataType: "json",

            success: function(response){
                console.log("Deleting address number: "+ id)    
                $("#card-address-"+id).remove()
            }
        })
    })

    $(".add-to-wishlist").on("click", function(){
        let product_id = $(this).attr("data-product-item")
        let this_val = $(this)

        $.ajax ({
            url: "/add-to-wishlist",
            data:{
                "product_id": product_id,
            },
            dataType: "json",

            beforeSend: function(){
                console.log("Sending to wishlist id: " + product_id)
            },
                
            
            success:function(response){
                console.log("Product ID: " + product_id + " successfuly added to wishlist")
                this_val.html("✔")
                $(".wishlist-count").text(response.wishlist_count)

            }
        })
    })

    $(".delete-from-wishlist").on("click", function () {
        let product_id = $(this).attr("data-product-item")
        
        $.ajax({
            url: "/delete-from-wishlist",
            data:{
                "product_id": product_id,
            },
            dataType: "json",

            beforeSend: function(){
                console.log("Product ID: " + product_id + "---> Send to delete.")
            },

            success: function(response){
                console.log("Item Deleted from wishlist")
                $("#wishlist-item-"+product_id).remove()
                $(".wishlist-count").text(response.wishlist_count)
            }
        })
    })

});
