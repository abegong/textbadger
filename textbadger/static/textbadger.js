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
        alert("hi");
        //event.preventDefault();
        var form = $(this);
        //console.log(form.serializeArray());
        $.post(
            form.attr('tb-href'),
            form.serializeArray(),
            function(data){

                if( data.status == "success" ){
                  //console.log(data);
                  if( form.attr("tb-redirect") ){
                    location.href = form.attr("tb-redirect");
                  }else if( data.redirect ){
                    location.href = data.redirect;
                  }

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

    //Add lorem ipsum to paragraphs
    $("p.lorem").each(function(){
        $(this).html(loremIpsumParagraph(20+Math.floor(Math.random()*20)));
    });

    //Automagically trigger "auto" actions
    $(".auto").click();

    //This development snippet autorefreshes the page every 2 seconds
//    autoRefresh(2000);
});
