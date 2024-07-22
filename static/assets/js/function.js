console.log('working fine................')


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
                $("#review-response").html("Review added successfully.")
                $(".hide-comment-form").hide()

                let _html = '<div class="single-comment justify-content-between d-flex mb-30">'
                    _html += '<div class="user justify-content-between d-flex">'
                    _html += '<div class="thumb text-center">'
                    _html += '<a href="#" class="font-heading text-brand">'+ response.context.user +'</a>'
                    _html += '</div>'

                    _html += '<div class="desc">'
                    _html += '<div class="d-flex justify-content-between mb-10">'
                    _html += '<div class="d-flex align-items-center">'
                    _html += '<span class="font-xs text-muted">added now          </span>'
                    _html += '</div>'
                    
                    _html += '<div>'
                    for(let i = 0; i < response.context.rating; i++ ){
                        _html += '<i class="fas fa-star text-warning"></i>'
                        
                    }
                    _html += '</div>'

                    _html += '</div>'
                    _html += '<strong>'+ response.context.title +'</strong>'
                    _html += '<hr>'

                    _html += '<p class="mb-10">'+ response.context.description +'</p>'

                    _html += '</div>'
                    _html += '</div>'
                    _html += '</div>'
                    $(".comment-list").prepend(_html)
            }

        }
    })
})


$(document).ready(function(){
    $(".filter-checkbox, #price-filter-btn").on("click", function(){
        console.log("CheckBoxxx");

        let filter_object = {}

        let min_price = $("#max_discount_price").attr("min")
        let max_price = $("#max_discount_price").val()

        filter_object.min_price = min_price;
        filter_object.max_price = max_price;

        $(".filter-checkbox").each(function(){
            let filter_value = $(this).val()
            let filter_key = $(this).data("filter")

            filter_object[filter_key] = Array.from(document.querySelectorAll('input[data-filter='+ filter_key +']:checked')).map(function(element){
                return element.value
            })

            
        })
        
        console.log("filter object is:", filter_object );

        $.ajax({
            url: '/filter-products',
            data: filter_object,
            dataType: 'json',
            beforeSend: function(){
                console.log("trying to filter products ...")
            },
            success: function(response){
                console.log(response);
                console.log("product successfully filtered.");
                $("#filtered-products").html(response.data);
            },
        })
    })


    $("#max_discount_price").on("blur", function(){
        let min_price = $(this).attr("min")
        let max_price = $(this).attr("max")
        let current_price = $(this).val()


        if(current_price < parseInt(min_price) || current_price > parseInt(max_price)){
            console.log("price error");



            alert("Price must between $" + min_price + " and $" + max_price) 
            $(this).val(min_price)
            $("#range").val(min_price)

            $(this).focus()

            return false
        }
    })

    
    $(".add-to-cart-btn").on("click", function(){
    
        let this_val = $(this)
        let index = this_val.attr("data-index")
        
        let quantity = $(".product-quantity-" + index).val()
        let product_title = $(".product-title-" + index).val()
        let product_id = $(".product-id-" + index).val()
        let product_price = $(".current-product-price-" + index).text()
        let product_image = $(".product-image-" + index).val()
    

    
        $.ajax({
            url:'/add-to-cart',
            data:{
                'id':product_id,
                'quantity': quantity,
                'title': product_title,
                'price': product_price,
                'image': product_image,
                'pk': product_id,
            },
            dataType: 'json',
            beforeSend: function(){
                console.log("Adding product to cart...");
            },
    
            success: function(response){
                this_val.html("✔")
                console.log("Product added to cart");
                $(".cart-items-count").text(response.totalcartitems)
            },
        })
        
    })
    
    
    
  
})

$(document).on("click", '.delete-product', function(){
    
    let product_id = $(this).attr("data-product")
    let this_val = $(this)

    console.log("Product ID: ", product_id);

    $.ajax({
        url: "/delete-from-cart",
        data: {
            "id": product_id,
        },
        dataType: "json",

        beforeSend: function(response){
            this_val.hide()
        },

        success: function(response){
            this_val.show()
            $(".cart-items-count").text(response.totalcartitems)
            $("#cart-list").html(response.data)
        }

    })

})

  
$(document).on("click", '.update-product', function(){
    
    let product_id = $(this).attr("data-product")
    let product_quantity = $(".product-quantity-" + product_id).val()
    let this_val = $(this)
    

    console.log("Product ID: ", product_id);
    console.log("Product qty: ", product_quantity);

    $.ajax({
        url: "/update-cart",
        data: {
            "id": product_id,
            "quantity": product_quantity,
        },
        dataType: "json",

        beforeSend: function(response){
            this_val.hide()
        },

        success: function(response){
            this_val.show()
            $(".cart-items-count").text(response.totalcartitems)
            $("#cart-list").html(response.data)
        }

    })

})
