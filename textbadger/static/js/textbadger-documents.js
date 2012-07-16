/*
Manager document-related data and DOM manipulation.
All pages that use documents should begin with a call to:
    DocManager.initialize(collection_id, csrf_token, seq_list)

No other code is needed.
*/
var DocManager = {
    doc_list : [],  //Array of documents containing {content, metadata}
    seq_list : [],   //Array of document indexes, e.g. [8,5,3,2].  May be shuffled and incomplete.
    doc_index : 0,  //Index of the currently visible document
    seq_index : 0,  //Current index in the sequence array

    loadDocList : function( collection_id, csrf_token, seq_list ){
        $.post(
            '/ajax/get-collection-docs/',
            {'id': collection_id, 'csrfmiddlewaretoken': csrf_token },
            function(data){
                DocManager.doc_list = data.documents;
                if(seq_list){
                    DocManager.seq_list = seq_list;
                }else{
                    //If seq_list isn't specified, create an array of indexes in boring counting order
                    DocManager.seq_list = new Array(DocManager.doc_list.length);
                    for( var i=0; i<DocManager.doc_list.length; i++ ){
                        DocManager.seq_list[i] = i;
                    }
                }

                DocManager.showDocument(0);
                console.log(DocManager.seq_list.length);
                $("#doc-count").html(DocManager.seq_list.length);
            },
            'json'
        );
    },

    showDocument : function(seq_index){
		//Update both indexes
		DocManager.seq_index = seq_index;
        DocManager.doc_index = DocManager.seq_list[seq_index];

        //Show the document
        $("#doc-box").html(DocManager.doc_list[DocManager.doc_index].content);

        //Update navigation
        $("#doc-index").val(DocManager.doc_index+1);
        $("#docs-remaining").html(DocManager.seq_list.length-DocManager.seq_index);

	    if( DocManager.seq_index == 0 ){ $("#prev-doc-button").addClass("disabled"); }
	    else{ $("#prev-doc-button").removeClass("disabled"); }

	    if( DocManager.seq_index == DocManager.doc_list.length-1 ){ $("#next-doc-button").addClass("disabled"); }
	    else{ $("#next-doc-button").removeClass("disabled"); }

        //Update hidden field
        $("#doc-index-hidden").val(DocManager.doc_index);

        //Update codebook markup
        //codebookModel.markupCodebook();

        //Update metadata
        var M = DocManager.doc_list[DocManager.doc_index].metadata;
        var elements = 1;
        $("#doc-metadata").html("");
        for( m in M ){
            $("#doc-metadata").append("<dt>"+m+"</dt>");
            $("#doc-metadata").append("<dd>"+M[m]+"</dd>");

            $("#edit-metadata").append("<div id = \"" + elements + "\" class=\"control-group\"><input type=\"text\" class=\"input-xlarge\" name=\"key\" placeholder='e.g. \"New York Times op-eds\"' value=\""+m+ "\"><div class=\"controls\"><textarea rows=\"3\" class=\"input-xlarge\" name=\"value\" placeholder='e.g. \"New York Times op-eds\"'>"+M[m]+"</textarea><button id=\"delete-"+elements+"\"class=\"btn btn-mini delete\">&times;</button></div></div>");
            elements++;
        }
        console.log(M)
        if (!M) {
            console.log("empty");
            $("#edit-metadata").append("<div id = \"" + elements + "\" class=\"control-group\"><input type=\"text\" class=\"input-xlarge\" name=\"key\" placeholder='e.g. \"New York Times op-eds\"' value=\""+m+ "\"><div class=\"controls\"><textarea rows=\"3\" class=\"input-xlarge\" name=\"value\" placeholder='e.g. \"New York Times op-eds\"'>"+M[m]+"</textarea><button id=\"delete-"+elements+"\"class=\"btn btn-mini delete\">&times;</button></div></div>");
        }


        $(name[value="meta-data-elements"]).val(elements);
         $(".delete").live('click',function () {
        //live is deprecated, using it for sake of expediancy, click doesn't work
               // $(this).parent().parent().remove();
                $(this).closest(".control-group").remove();
                elements--;
            });

         $("#add").on('click',function () {
                $("#edit-metadata").append("<div id = \"" + elements + "\" class=\"control-group\"><input type=\"text\" name =\"key\"class=\"input-xlarge\"  placeholder='e.g. \"New York Times op-eds\"'><div class=\"controls\"><textarea rows=\"3\" class=\"input-xlarge\"  name=\"value\" placeholder='e.g. \"New York Times op-eds\"'></textarea><button id=\"delete-"+elements+"\"class=\"btn btn-mini delete\">&times;</button></div></div>");
                elements++;
                //this is likely unnecessary now, as well as the the entire idea of tracking the number of elements
                $(name[value="meta-data-elements"]).val(elements);
            });
    },

    showDocumentForm : function(index){
		console.log(DocManager.doc_list[DocManager.doc_index]);
	},

    loadPrevDoc : function(){
	    if( DocManager.seq_index > 0 ){
		    DocManager.showDocument( DocManager.seq_index-1 );
	    }
	    return( false );
    },

    loadNextDoc : function(){
	    if( DocManager.seq_index < DocManager.seq_list.length-1 ){
		    DocManager.showDocument( DocManager.seq_index+1 );
	    }
	    return( false );
    },

    initialize : function( collection_id, csrf_token, seq_list ){
        $("#prev-doc-button").click( DocManager.loadPrevDoc );
        $("#next-doc-button").click( DocManager.loadNextDoc );
        $("#doc-index").change(function(){
            var x = $(this).val();
            //! Need to add input validation to this function

            DocManager.seq_index = x;
            DocManager.showDocument(x)
        });

        DocManager.loadDocList( collection_id, csrf_token, seq_list );
    }
};
