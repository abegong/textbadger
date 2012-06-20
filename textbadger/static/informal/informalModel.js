var cbQuestion = function(question_type, var_name, params, targeted) {
    this.fillInMissingParams = function(){
        qA = codebookModel.questionArguments[this.question_type()];
        for( a in qA ){
            if( !(a in this.params) ){
                if( $.isArray(qA[a].default) ){    this.params[a] = ko.observableArray(qA[a].default); }
                else{    this.params[a] = ko.observable(qA[a].default); }
            }
        }
    }

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
        if( $.isArray(params[p]) ){ this.params[p] = ko.observableArray(params[p]); }
        else{ this.params[p] = ko.observable(params[p]); }
    };
    if( !("header_text" in params ) ) this.params["header_text"] = ko.observable(question_type);
    this.fillInMissingParams();

    if( typeof targeted == 'undefined' ){ this.targeted = ko.observable(false); }
    else{ this.targeted = ko.observable(true); }
};


var codebookModel = {
    questionTypes: ko.observableArray([
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
    ]),

    questionArguments: {
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
    },

    properties: {
        width: ko.observable(350)
    },

  questions: ko.observableArray([]),
    target_index: ko.observable(0),

    //These functions are used to modify the codebook

    //This is really messy.  Can probably redo with splice...?
    loadQuestions: function(Q){
        while( this.questions().length > 0 ){
            this.questions().pop();
        }

        for( q in Q ){
            this.questions.push( new cbQuestion(Q[q].question_type, Q[q].var_name, Q[q].params) );
        };
    },

    targetQuestion: function(i){
        this.questions()[this.target_index()].targeted(false);
        this.addStylesToQuestion($($(".questionBox")[this.target_index()]));
        this.target_index(i);
        this.questions()[this.target_index()].targeted(true);
    },

/*//NEW//
    questionTypeChanged: function(){
        q1 = ko.toJS( this.questions.slice( this.target_index() )[0] );
        q2 = new cbQuestion( q1.question_type, q1.var_name, q1.params, true );
        this.questions.splice( this.target_index(), 1, q2 );
        attachControlsToQuestion(this.target_index());
    },
*/
    changeQuestionType: function( T ){
        this.questions()[this.target_index()].changeQuestionType(T);
        attachControlsToQuestion(this.target_index());
    },

    addQuestion: function(){
        q1 = ko.toJS( this.questions.slice( this.target_index() )[0] );
        q2 = new cbQuestion( q1.question_type, q1.var_name, q1.params );
        this.questions.splice( this.target_index()+1, 0, q2 );
    },

    delQuestion: function(){
        i = this.target_index();
        if( i > 0 ){
            attachControlsToQuestion( i-1 ); 
            this.questions.splice( i, 1 );
        }
        else if( this.questions().length > 1 ){ 
            this.questions.splice( i, 1 );
            attachControlsToQuestion( 0 );
        }
    },

    moveQuestionUp: function(){
        i = this.target_index();
        if( i > 0 ){
            if( this.questions().length-i > 1 ){
                this.questions.splice( i, 0, this.questions.splice(i-1,1)[0] );
                attachControlsToQuestion(i-1);
            }
            else{
                q = this.questions().pop();
                this.questions.splice( i-1, 0, q );
                attachControlsToQuestion(i-1);
            }
        }
    },

    moveQuestionDown : function(){
        i = this.target_index();
        if( this.questions().length-i > 1 ){
            this.questions.splice( i+1, 0, this.questions().splice(i,1)[0] );
            attachControlsToQuestion(i+1);$('input',this).attr
        }
    },

    addStylesToQuestion : function(Q){
        $("input[type=radio],input[type=checkbox]",Q).parent()
            .click( function(){    x = $('input',this); x.attr('checked',!x.attr('checked'));    })
//            .mouseover( function(){ $(this).addClass('ui-state-hover'); })
//            .mouseout( function(){ $(this).removeClass('ui-state-hover'); });
            .mouseover( function(){ $(this).addClass('mouseoverCell'); })
            .mouseout( function(){ $(this).removeClass('mouseoverCell'); });

        Q
            .hover( 
//                function(){$(this).addClass('ui-state-error ui-corner-all');},
//                function(){$(this).removeClass('ui-widget-content');}
                function(){$(this).addClass('hoverQuestion');},
                function(){$(this).removeClass('hoverQuestion');}
            )
        .click( function(){attachControlsToQuestion( $(this).index(".questionBox")); } );
    },

    addStylesToCodebook: function(){
        $("div.questionBox").each(function(i,q){
            codebookModel.addStylesToQuestion($(q));
        })
    },

    getCodebookJson : function(){
        j = ko.toJSON({'questions':this.questions()});
        //! Remove "targeted" terms here
        //! Add name and description (maybe)
        return( j );
    }
};
