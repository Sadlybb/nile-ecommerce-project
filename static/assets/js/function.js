console.log('working fine................')


$("#commentForm").submit(function(e){
    e.preventDefault();

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