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

    this.loadDocList = function( collection_id, csrf_token, seq_list ){
        var self = this;
        $.post(
            '/ajax/get-collection-docs/',
            {'id': collection_id, 'csrfmiddlewaretoken': csrf_token },
            function(data){
                self.doc_list = data.documents;
                if(seq_list){
                    self.seq_list = seq_list;
                }else{
                    //If seq_list isn't specified, create an array of indexes in boring counting order
                    self.seq_list = new Array(self.doc_list.length);
                    for( var i=0; i<self.doc_list.length; i++ ){
                        self.seq_list[i] = i;
                    }
                }

                self.initControls();
                self.showDocument(0);
            },
            'json'
        );
    };

    this.showDocument = function(seq_index){
		//Update both indexes
		this.seq_index = seq_index;
        this.doc_index = this.seq_list[seq_index];

        //Show the document
        $("#doc-box").html(this.doc_list[this.doc_index].content);

        //Update navigation
        this.updateControls();
    };

/*
    this.showDocumentForm = function(index){
		console.log(this.doc_list[this.doc_index]);
	};
*/

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
        this.loadDocList( collection_id, csrf_token, seq_list );
    };
    
    //Overwrite these functions...
    this.initControls = function(){
        //Called once at startup
    };
    
    this.updateControls = function(){
        //Called after a new document is loaded
    };
};
