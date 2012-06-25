var DocManager = {
    doc_list : [],
    doc_index : 0,

    loadDocList : function( collection_id, csrf_token ){
        $.post(
            '/ajax/get-collection-docs/',
            {'id': collection_id, 'csrfmiddlewaretoken': csrf_token },
            function(data){
                DocManager.doc_list = data.documents;
                DocManager.showDocument(0);
                $("#doc_count").html(DocManager.doc_list.length);
            },
            'json'
        )
    },

    showDocument : function(index){
        //Show the document
        $("#doc-box").html(DocManager.doc_list[index].content);

        //Update navigation
        $("#doc_index").val(index+1);

        //Update metadata
        var M = DocManager.doc_list[index].metadata;
        $("#meta-data").html("");
        for( m in M ){
            $("#meta-data").append("<dt>"+m+"</dt>");
            $("#meta-data").append("<dd>"+M[m]+"</dd>");
        }
    },

    loadPrevDoc : function(){
	    if( DocManager.doc_index > 0 ){
		    DocManager.doc_index -= 1;

		    DocManager.showDocument( DocManager.doc_index );
		    if( DocManager.doc_index == 0 ){ $("#prevButton").addClass("ui-state-disabled"); }
		    $("#nextButton").removeClass("ui-state-disabled");
	    }
	    return( false );
    },

    loadNextDoc : function(){
	    if( DocManager.doc_index < DocManager.doc_list.length-1 ){
		    DocManager.doc_index += 1;

		    DocManager.showDocument( DocManager.doc_index );
		    if( DocManager.doc_index == DocManager.doc_list.length-1 ){ $("#nextButton").addClass("ui-state-disabled"); }
		    $("#prevButton").removeClass("ui-state-disabled");
	    }
	    return( false );
    },

    initialize : function(){
        $("#prevButton").click( DocManager.loadPrevDoc );
        $("#nextButton").click( DocManager.loadNextDoc );
        $("#doc_index").change(function(){
            var x = $(this).val();

            //! Need to add input validation to this function
            DocManager.doc_index = x;
            DocManager.showDocument(x)
        });
    }
}






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
