//An individual question within the codebooks
var CodebookQuestion = function(question_type, var_name, params, targeted) {
    //Hardcoded question info.  This is easier than subclassing, even tho it's a bit messy.
    this.questionArguments = {
        "Static text" : {"header_text":{"label":"Header text", "default":"Header text"}},
        "Multiple choice" : {"header_text":{"label":"Header text", "default":"Header text"}, "answer_array":{"label":"Answer categories", "default":["Answer 1","Answer 2"]}},
        "Check all that apply" : {"header_text":{"label":"Header text", "default":"Header text"}, "answer_array":{"label":"Answer categories", "default":["Answer 1","Answer 2"]}},
        "Two-way scale" : {"header_text":{"label":"Header text", "default":"Header text"}, "answer_array":{"label":"Answer categories", "default":["Answer 1","Answer 2"]}, "left_statement":{"label":"Left statement", "default":"Left statement"}, "right_statement":{"label":"Right statement", "default":"Right statement"}},
        "Radio matrix" : {"header_text":{"label":"Header text", "default":"Header text"}, "answer_array":{"label":"Answer categories", "default":["Answer 1","Answer 2"]}, "question_array":{"label":"Questions", "default":["Question 1", "Question 2"]}},
        "Checkbox matrix" : {"header_text":{"label":"Header text", "default":"Header text"}, "answer_array":{"label":"Answer categories", "default":["Answer 1","Answer 2"]}, "question_array":{"label":"Questions", "default":["Question 1", "Question 2"]}},
        "Two-way matrix" : {"header_text":{"label":"Header text", "default":"Header text"}, "answer_array":{"label":"Answer categories", "default":["Answer 1","Answer 2"]}, "left_statements":{"label":"Left statements", "default":["Statement 1", "Statement 2"]}, "right_statements":{"label":"Right statements", "default":["Statement 1", "Statement 2"]}},
        "Text box" : {"header_text":{"label":"Header text", "default":"Header text"}, "cols":{"label":"Columns","default":20}},
        "Short essay" : {"header_text":{"label":"Header text", "default":"Header text"}, "cols":{"label":"Columns","default":30}, "rows":{"label":"Rows","default":5}},
        "Text matrix" : {"header_text":{"label":"Header text", "default":"Header text"}, "answer_array":{"label":"Answer categories", "default":["Answer 1","Answer 2"]}, "cols":{"label":"Columns","default":20}}
    };
    
    this.fillInMissingParams = function(){
        qA = this.questionArguments[this.question_type()];
        for( a in qA ){
            if( !(a in this.params) ){
                if( $.isArray(qA[a].default) ){
                    this.params[a] = ko.observableArray(qA[a].default);
                }else{
                    this.params[a] = ko.observable(qA[a].default);
                }
            }
        }
    };

    this.changeQuestionType = function( T ){
        this.question_type(T);
        this.fillInMissingParams();
    };

    this.changeQuestionName = function( N ){
        this.var_name( N.replace(/\W+/g,'') );
    };

    this.updateParams = function( p, A ){ this.params[p]( A ); };

    //Initialize
    this.question_type = ko.observable(question_type);
    this.var_name = ko.observable(var_name);
    this.params = {};
    for( p in params ){
        if( $.isArray(params[p]) ){
            this.params[p] = ko.observableArray(params[p]);
        }else{
            this.params[p] = ko.observable(params[p]);
        }
    };
    if( !("header_text" in params ) ) this.params["header_text"] = ko.observable(question_type);
    this.fillInMissingParams();

    if( typeof targeted == 'undefined' ){
        this.targeted = ko.observable(false);
    }else{
        this.targeted = ko.observable(true);
    }
};

var CodebookManager = function(){
    
    //--- Main KO observable objects ----------------------------------------//
    this.questionTypes = ko.observableArray([
        "Static text",
        "Multiple choice",
        "Check all that apply",
        "Two-way scale",
        "Radio matrix",
        "Checkbox matrix",
        "Two-way matrix",
        "Text box",
        "Short essay",
        "Text matrix"
    ]);
    
    this.properties = {
        width: ko.observable(350)
    };
    this.questions = ko.observableArray([]);
    this.target_index = ko.observable(0);

    //--- Supporting methods ------------------------------------------------//
    
    this.loadQuestions = function(Q){
        this.clearQuestions();
        
        for( q in Q ){
            this.questions.push( new CodebookQuestion(Q[q].question_type, Q[q].var_name, Q[q].params) );
        };
    };

    //Create the default question
    this.initDefaultQuestions = function(){
        this.loadQuestions([
            {question_type:"Static text", var_name:"", params:{} },
            {question_type:"Multiple choice", var_name:"", params:{} },
            {question_type:"Check all that apply", var_name:"", params:{} },
            {question_type:"Two-way scale", var_name:"", params:{} },
            {question_type:"Radio matrix", var_name:"", params:{} },
            {question_type:"Checkbox matrix", var_name:"", params:{} },
            {question_type:"Two-way matrix", var_name:"", params:{} },
            {question_type:"Text box", var_name:"", params:{} },
            {question_type:"Short essay", var_name:"", params:{} },
            {question_type:"Text matrix", var_name:"", params:{} }
        ]);
    };

    this.getCodebookJson = function(){
        j = ko.toJSON({'questions':this.questions()});
        //! Remove "targeted" terms here
        //!? Add name and description (maybe)
        return( j );
    };

    this.targetQuestion = function(i){
        this.questions()[this.target_index()].targeted(false);

        this.target_index(i);
        this.questions()[this.target_index()].targeted(true);

        this.addStyles();
    };

    this.changeQuestionType = function( T ){
        this.questions()[this.target_index()].changeQuestionType(T);
        this.addStyles();
    };
    
    this.addQuestion = function(){
        q1 = ko.toJS( this.questions.slice( this.target_index() )[0] );
        q2 = new CodebookQuestion( q1.question_type, q1.var_name, q1.params );
        this.questions.splice( this.target_index()+1, 0, q2 );
        this.addStyles();
    };

    this.delQuestion = function(){
        i = this.target_index();
        if( i > 0 ){
            this.attachControlsToQuestion( i-1 ); 
            this.questions.splice( i, 1 );
        }
        else if( this.questions().length > 1 ){ 
            this.questions.splice( i, 1 );
            this.attachControlsToQuestion( 0 );
        }
        this.addStyles();
    };

    this.moveQuestionUp = function(){
        i = this.target_index();
        if( i > 0 ){
            if( this.questions().length-i > 1 ){
                this.questions.splice( i, 0, this.questions.splice(i-1,1)[0] );
                this.attachControlsToQuestion(i-1);
            }
            else{
                q = this.questions().pop();
                this.questions.splice( i-1, 0, q );
                this.attachControlsToQuestion(i-1);
            }
        }
        this.addStyles();
    };

    this.moveQuestionDown = function(){
        i = this.target_index();
        if( this.questions().length-i > 1 ){
            this.questions.splice( i+1, 0, this.questions().splice(i,1)[0] );
            this.attachControlsToQuestion(i+1);$('input',this).attr
        }
        this.addStyles();
    };

    this.clearQuestions = function(){
        while( this.questions().length > 0 ){
            this.questions().pop();
        }
    };

    this.init = function( codebook_id, csrf_token ){
        var codebookManager = this;
        this.initControls();

        //Load the template and knockout model dynamically.
        var callback_a = $.get("/static/_codebookKnockoutTemplate.htm", function(template){
            $("body").append(template);
        }, "text");

        //Load the codebook dynamically
        var callback_b = $.post("/ajax/get-codebook/",
            {'id': codebook_id, 'csrfmiddlewaretoken': csrf_token },
            function(response){
                if( response.status=="success" ){                
                    codebookManager.loadQuestions(response.codebook.questions);

                    //! For easy debugging:
                    //codebookManager.initDefaultQuestions(response.codebook.questions);
                }else{
                    alert( response.msg );
                    //! Need error checking for failed responses.
                }
            }
        );

        // This should resolve a possible race condition for loading the codebook.
        $.when(callback_a, callback_b).then(function(){
            ko.applyBindings(codebookManager);
            codebookManager.addStyles();
            codebookManager.attachControlsToQuestion(0);        
        });
    };

    this.addStyles = function(){
        var codebookManager = this;
        $("div.questionBox").each(function(i,q){
            codebookManager.addStylesToQuestion($(q));
        });
    };
    
    //Overwrite this method in subclasses!
    this.initControls = function(){};

    //Overwrite this method in subclasses!
    this.addStylesToQuestion = function(Q){};

    //! This method should be moved out to a subclass
    this.markupCodebook = function(labels){
        var labels = label_list[DocManager.doc_index];
        /*
        console.log("====================================================");
        console.log("label_list");
        console.log(label_list);
        console.log("DocManager.doc_index");
        console.log(DocManager.doc_index);
        console.log("labels");
        console.log(labels);
        */
        
        //Markup
        $(".questionMarkupAnchor").each(function(i,d){
            var $d = $(d),
                show_badges = false;

            //Create and show badges
            if( show_badges ){
                //Remove any previous badges
                //$('span.questionMarkup', $d.closest('.questionBox')).remove();
                $('span.questionMarkup', $d).remove();

                //Add new badge
                var r = Math.random();
                var $badge = $('<span class="questionMarkup badge badge-warning"></span>')
                    .append('<b>.'+Math.floor(r*1000)+'</b>')
                    .prependTo($d.closest('.questionBox'));
                    //.prependTo($d);

                //Set badge location
                var offset = $d.offset();
                $badge.offset({ top: offset.top, left: offset.left-$badge.width()-22 });
            }
            
            //Create and show shim-graphs
            $(".shim-graph", $d).each(function(i,g){
                var var_name = $(this).next().attr("name"),
                    $shimgraph = $(g),
                    val = $shimgraph.next().val();
                
                if( var_name in labels ){
                    for( j in labels[var_name] ){
                        //console.log(var_name+"\t"+j+"\t:\t"+val+"\t:\t"+labels[var_name][j]);
                        if( labels[var_name][j] == val ){
                            $shimgraph.append('<img src="/static/tiny-shim-b.gif"></img>');
                        }
                    }
                }
                $(this)
                    .data("var_name", var_name)
                    .next().hide();
            });
        });
    };

};
