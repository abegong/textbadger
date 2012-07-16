Array.max = function( array ){
    return Math.max.apply( Math, array );
};

// Function to get the Min value in Array
Array.min = function( array ){
   return Math.min.apply( Math, array );
};


//This development snippet to autorefresh the page
function autoRefresh(interval) {
	setTimeout('location.reload(true);',interval);
}

$(function(){
    $('.modal').on('show', function(e) {
        var modal = $(this);
        modal.css({
            'position': 'fixed'
        });

 //       modal.click(function(){$(this).modal('hide')});
        return this;
    });
//    .hide();

    //.open-modal buttons open modal dialogs
    //The dialog must be the next element in the DOM after the button
    $(".open-modal").click(function(){
      $(this).next().modal({'backdrop': 'static'});
    });

    $("#sign-in-btn").click(function(){
      $("#sign-in-modal").modal({'backdrop': 'static'});
    });


    //"Cancel" buttons in modals
    $("button[type='cancel']").click(function(){
      //event.preventDefault();
      //Get the first ancsetor modal to this button, and hide it
      $(this).parents(".modal:first").modal('hide');
      return false;
    });

    $('form:not(.tb-basic)').submit(function() {
        //event.preventDefault();
        var form = $(this);
        //console.log(form.serializeArray());
        $.post(
            form.attr('tb-href'),
            form.serializeArray(),
            function(data){

                //If the AJAx call succeeded
                if( data.status == "success" ){

                  //...and the form has "tb-redirect"
                  if( form.attr("tb-redirect") ){
                    //Redirect to the designated url
                    location.href = form.attr("tb-redirect");

                  //...or if the AJAX response designates a redirect target URL
                  }else if( data.redirect ){
                    //Redirect to the designated url
                    location.href = data.redirect;
                  }

                //If the AJAX call failed
                }else{
                  //! Give some kind of alert
                  alert( data.msg );
                }
                //alert(JSON.stringify(data));
            },
            'json'
        );
        return false;
    });

    //Clickable table rows have "href" attributes
    $('tr[href]')
        .hover(function(){
            $(this).addClass("tb-hilight");
        }, function(){
            $(this).removeClass("tb-hilight");
        })
        .click(function(){
            location.href = $(this).attr('href');
        });


    //Add lorem ipsum to paragraphs
    $("p.lorem").each(function(){
        $(this).html(loremIpsumParagraph(20+Math.floor(Math.random()*20)));
    });

    //Automagically trigger "auto" actions
    $(".auto").click();

    //This development snippet autorefreshes the page every 2 seconds
//    autoRefresh(2000);

});
