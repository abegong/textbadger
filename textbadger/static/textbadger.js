/*
Manager document-related data and DOM manipulation.
All pages that use documents should begin with a call to:
    DocManager.initialize(collection_id, csrf_token)

No other code is needed.
*/
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
                $("#doc-count").html(DocManager.doc_list.length);
            },
            'json'
        );
    },

    showDocument : function(index){
		//Update the index
		DocManager.doc_index = index;

        //Show the document
        $("#doc-box").html(DocManager.doc_list[index].content);

        //Update navigation
        $("#doc-index").val(index+1);

        if( DocManager.doc_index === 0 ){ $("#prev-doc-button").addClass("disabled"); }
        else{ $("#prev-doc-button").removeClass("disabled"); }

        if( DocManager.doc_index === DocManager.doc_list.length-1 ){ $("#next-doc-button").addClass("disabled"); }
        else{ $("#next-doc-button").removeClass("disabled"); }

        //Update metadata
        var M = DocManager.doc_list[index].metadata;
        var elements = 1;
        $("#doc-metadata").html("");
        for( m in M ){
            $("#doc-metadata").append("<dt>"+m+"</dt>");
            $("#doc-metadata").append("<dd>"+M[m]+"</dd>");

            $("#edit-metadata").append("<div id = \"" + elements + "\" class=\"control-group\"><input type=\"text\" class=\"input-xlarge\" name=\"label-"+elements+"\" placeholder='e.g. \"New York Times op-eds\"' value=\""+m+ "\"><div class=\"controls\"><textarea rows=\"3\" class=\"input-xlarge\" name=\"text-"+elements+"\" placeholder='e.g. \"New York Times op-eds\"'>"+M[m]+"</textarea><button id=\"delete-"+elements+"\"class=\"btn btn-mini delete\">&times;</button></div></div>");
            elements++;
        }
        $(name[value="meta-data-elements"]).val(elements);
         $(".delete").live('click',function () {
        //live is deprecated, using it for sake of expediancy, click doesn't work
               // $(this).parent().parent().remove();
                $(this).closest(".control-group").remove();
                elements--;
            });

         $("#add").on('click',function () {
                $("#edit-metadata").append("<div id = \"" + elements + "\" class=\"control-group\"><input type=\"text\" name =\"label-"+elements+"\"class=\"input-xlarge\"  placeholder='e.g. \"New York Times op-eds\"'><div class=\"controls\"><textarea rows=\"3\" class=\"input-xlarge\"  name=\"text-"+elements+"\" placeholder='e.g. \"New York Times op-eds\"'></textarea><button id=\"delete-"+elements+"\"class=\"btn btn-mini delete\">&times;</button></div></div>");
                elements++;
                $(name[value="meta-data-elements"]).val(elements);
            });

    },

    showDocumentForm : function(index){
		console.log(DocManager.doc_list[DocManager.doc_index]);
	},

    loadPrevDoc : function(){
        if( DocManager.doc_index > 0 ){
		    DocManager.showDocument( DocManager.doc_index-1 );
	    }
	    return( false );
    },

    loadNextDoc : function(){
	    if( DocManager.doc_index < DocManager.doc_list.length-1 ){
		    DocManager.showDocument( DocManager.doc_index+1 );
	    }
	    return( false );
    },

    initialize : function( collection_id, csrf_token ){
        $("#prev-doc-button").click( DocManager.loadPrevDoc );
        $("#next-doc-button").click( DocManager.loadNextDoc );
        $("#doc-index").change(function(){
            var x = $(this).val();
            //! Need to add input validation to this function

            DocManager.doc_index = x;
            DocManager.showDocument(x);
        });

        DocManager.loadDocList( collection_id, csrf_token );
    }
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
