/*
* Manager document-related data and DOM manipulation.
*
* Usage: TBD...
*/
var DocumentManager = function(){
    this.doc_list = [];  //Array of documents containing {content, metadata}
    this.seq_list = [];  //Array of document indexes, e.g. [8,5,3,2].  May be shuffled and incomplete.
    this.doc_index = 0;  //Index of the currently visible document
    this.seq_index = 0;  //Current index in the sequence array
    this.url_regex = /^([a-z]([a-z]|\d|\+|-|\.)*):(\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?((\[(|(v[\da-f]{1,}\.(([a-z]|\d|-|\.|_|~)|[!\$&'\(\)\*\+,;=]|:)+))\])|((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=])*)(:\d*)?)(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*|(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)|((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)|((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)){0})(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(\#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i

    this.loadDocList = function( collection_id, csrf_token, seq_list ){
        var self = this;
        $.post(
            '/ajax/get-collection-docs/',
            {'id': collection_id, 'csrfmiddlewaretoken': csrf_token },
            function(data){

                self.doc_list = data.documents;
                self.initSeqList( seq_list );
                self.initControls();
                self.showDocument(0);

            },
            'json'
        );
    };

    this.initSeqList = function( seq_list ){
        if(seq_list){
            this.seq_list = seq_list;
        }else{
            //If seq_list isn't specified, create an array of indexes in boring counting order
            this.seq_list = new Array(this.doc_list.length);
            for( var i=0; i < this.doc_list.length; i++ ){
                this.seq_list[i] = i;
            }
        }
    };

    this.showDocument = function(seq_index){
		//Update both indexes
		this.seq_index = seq_index;
        this.doc_index = this.seq_list[seq_index];


        var content = this.doc_list[this.doc_index].content;
        
        //Show the document
        if(this.url_regex.test(content)) {
            $("#doc-box").html('<iframe id="doc-frame" src="'+content+'"></iframe>');
            $("#doc-frame").height($(window).height()-180);
//            var self = this;
//            $("#doc-frame").load(function(event){ self.autoResize("doc-frame") });
//            $("#doc-frame").ready(function(event){ jQuery('iframe').iframeAutoHeight(); });
        } else {
            $("#doc-box").html(content);
        }
        
        //Update navigation
        this.updateControls();

    };

    this.loadPrevDoc = function(){
        if( this.seq_index > 0 ){
            this.showDocument( this.seq_index-1 );
        }
        return( false );
    };

    this.loadNextDoc = function(){
        if( this.seq_index < this.seq_list.length-1 ){
            this.showDocument( this.seq_index+1 );
        }
        return( false );
    };

    this.init = function( collection_id, csrf_token, seq_list ){
        //On the collections and review pages, seq_list is null
        //On the assignments page, seq_list is an array containing the indexes of documents to be coded.

        //Check to see if the seq_list is present, but empty
        if(seq_list){
            if( !seq_list.length ){
                //If so, exit without initializing
                alert("You have already completed this assignment. There is nothing to do here.  Please go to the batch page to review results.");
                return false;
            }
        }
        
        //Otherwise, initialize the document list
        this.loadDocList( collection_id, csrf_token, seq_list );
    };

/*    
    //Resize iframe to get rid of scroll bar
    this.autoResize = function(id){
        var newheight;
        var newwidth;

        if(document.getElementById){
            newheight=document.getElementById(id).contentWindow.document.body.scrollHeight;
            newwidth=document.getElementById(id).contentWindow.document.body.scrollWidth;
        }

        document.getElementById(id).height= (newheight) + "px";
        document.getElementById(id).width= (newwidth) + "px";
    };
*/

    //Overwrite these functions...
    this.initControls = function(){
        //Called once at startup
    };

    this.updateControls = function(){
        //Called after a new document is loaded
    };

    this.initDefaultNavControls = function(){
        var self = this;
        $("#prev-doc-button").click(function(){
            self.loadPrevDoc();
            return false;
        });
        $("#next-doc-button").click(function(){
            self.loadNextDoc();
            return false;
        });
        $("#doc-index").change(function(){
            var x = $(this).val();
            //! Need to add input validation

            self.seq_index = x;
            self.showDocument(x)

        });

        $("#doc-count").html(self.seq_list.length);

    };

    this.updateDefaultNavControls = function(){
        $("#doc-index").val(this.seq_index+1);

        if( this.seq_index == 0 ){ $("#prev-doc-button").addClass("disabled"); }
        else{ $("#prev-doc-button").removeClass("disabled"); }

        if( this.seq_index == this.doc_list.length-1 ){ $("#next-doc-button").addClass("disabled"); }
        else{ $("#next-doc-button").removeClass("disabled"); }

    };
};
