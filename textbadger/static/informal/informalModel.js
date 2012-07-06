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

        this.target_index(i);
        this.questions()[this.target_index()].targeted(true);

        this.addStylesToCodebook();
    },

    changeQuestionType: function( T ){
        this.questions()[this.target_index()].changeQuestionType(T);
        this.addStylesToCodebook();
    },

    addQuestion: function(){
        q1 = ko.toJS( this.questions.slice( this.target_index() )[0] );
        q2 = new cbQuestion( q1.question_type, q1.var_name, q1.params );
        this.questions.splice( this.target_index()+1, 0, q2 );
        this.addStylesToCodebook();
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
        this.addStylesToCodebook();
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
        this.addStylesToCodebook();
    },

    moveQuestionDown : function(){
        i = this.target_index();
        if( this.questions().length-i > 1 ){
            this.questions.splice( i+1, 0, this.questions().splice(i,1)[0] );
            this.attachControlsToQuestion(i+1);$('input',this).attr
        }
        this.addStylesToCodebook();
    },

    addEditorStylesToQuestion : function(Q){
		/*
        $("input[type=radio],input[type=checkbox]",Q).parent()
            .click( function(){    x = $('input',this); x.attr('checked',!x.attr('checked'));    })
            .mouseover( function(){ $(this).addClass('mouseoverCell'); })
            .mouseout( function(){ $(this).removeClass('mouseoverCell'); });
		*/
        Q
            .unbind('click mouseenter mouseleave')
            .hover( 
                function(){$(this).addClass('hoverQuestion');},
                function(){$(this).removeClass('hoverQuestion');}
            )
            .click( function(){
                codebookModel.attachControlsToQuestion( $(this).index(".questionBox") );
            });
    },

    addViewerStylesToQuestion : function(Q){
        $("input[type=radio],input[type=checkbox]",Q).parent()
            .click( function(){    x = $('input',this); x.attr('checked',!x.attr('checked'));    })
            .mouseover( function(){ $(this).addClass('mouseoverCell'); })
            .mouseout( function(){ $(this).removeClass('mouseoverCell'); });
    },

    addStylesToCodebook: function(){
		if( $("#codebook").attr("tb-codebook-mode") == 'viewer' ){
			$("div.questionBox").each(function(i,q){
				codebookModel.addViewerStylesToQuestion($(q));
			});
		}
		else if ( $("#codebook").attr("tb-codebook-mode") == 'editor' ){
			$("div.questionBox").each(function(i,q){
				codebookModel.addEditorStylesToQuestion($(q));
			});
		}

    },

    getCodebookJson : function(){
        j = ko.toJSON({'questions':this.questions()});
        //! Remove "targeted" terms here
        //!? Add name and description (maybe)
        return( j );
    },
    
    attachControlsToQuestion : function(i){
		//Change the targetQuestion in the model
		//console.log(i);
		codebookModel.targetQuestion(i);

		//Set index variables
		qB = $(".questionBox:eq("+i+")");        //The DOM object for the selected questionBox
		qC = $("#questionControls");             //The DOM object for the questionControls div
		qM = codebookModel.questions()[i];       //The question object in the knockout.js model
		qA = codebookModel.questionArguments[qM.question_type()];    //The questionArguments object in the knockout.js model

		//Add content within the control box: variable type and name
		qC
			.html( "Variable type<br/><select data-bind=\"options: questionTypes, value: questions()["+i+"].question_type, event: {change: function(event){codebookModel.changeQuestionType(event.target.value);}}\"></select><br/>" )
			.append( "Variable name<input type=\"text\" style=\"width:250px\" data-bind=\"value: questions()["+i+"].var_name, event: {change: function(event){codebookModel.questions()["+i+"].changeQuestionName(event.target.value);}}\"></input><br/>" );

		//Add content within the control box: variable parameters
		for( p in qA ){
			if( p in qM.params ){
	//            alert( p + ": " + qM.params[p]() );//+ "\n" + $.isArray( qM.params[p]() ) );// + ": " + $.isArray( qM.params[p]() );
				if( $.isArray( qM.params[p]() ) ){
					qC.append( qA[p].label + "<textarea rows=\"5\" style=\"width:250px\" data-bind=\"event: {change: function(event){codebookModel.questions()['"+i+"'].updateParams('"+p+"', event.target.value.split('\\n'));}}\">" + qM.params[p]().join('\n') + "</textarea><br/>" )
				}
				else{
					qC.append( qA[p].label +"<textarea rows=\"5\" style=\"width:250px\" data-bind=\"value: questions()["+i+"].params."+p+"\"></input><br/>" );
	//                qC.append( qA[p].label +"<input type=\"text\" style=\"width:250px\" data-bind=\"value: questions()["+i+"].params."+p+"\"></input><br/>" );
				}
			}
		}

		//Re-bind questionControls
		ko.applyBindings(codebookModel, qC[0]);
	},
    
    markupCodebook : function(labels){
        var labels = label_list[DocManager.doc_index];
        console.log("====================================================");
        console.log("label_list");
        console.log(label_list);
        console.log("DocManager.doc_index");
        console.log(DocManager.doc_index);
        console.log("labels");
        console.log(labels);

        //Markup
		$(".questionMarkupAnchor").each(function(i,d){
			var $d = $(d);

            //Remove any previous badges
            $('span.questionMarkup', $d.closest('.questionBox')).remove();

            //Add new badge
			var r = Math.random();
            var $badge = $('<span class="questionMarkup badge badge-warning"></span>')
                .append('<b>.'+Math.floor(r*1000)+'</b>')
                .prependTo($d.closest('.questionBox'));

            //Set badge location
			var offset = $d.offset();
			$badge.offset({ top: offset.top, left: offset.left-$badge.width()-22 });

            //Shim-graphs
            if( $d.hasClass("HAnchor") ){
                //Label inputs/old shim-graphs for removal
                $("#codebook input, div.shim-graph-h")
                    .addClass("old-codebook-obj");
                    
                $(".old-codebook-obj", $d).each(function(i,x){
                    //console.log(x);
                    //console.log(labels);
                    
                    //Find the appropriate label for this graph
                    //! This code is brittle because it depends on the sequences matching up exactly.
                    for( q in labels ){
                        if( q.match("Q"+i+"_")){
                            var question = q;
                            break;
                        }
                    }
                    console.log(question);
                    
                    //Create shimgraph
                    var $shimgraph = $('<div class="shim-graph-h"></div>');

                    if( typeof(question) != "undefined" ){
                        //console.log(labels);
                        //console.log(question);
                        
                        //Append shimgraph content
                        for( j in labels[question] ){
                            console.log("\t"+j+"\t:\t"+$(x).val()+"\t:\t"+labels[question][j]);
                            if( labels[question][j] == $(x).val() ){
                                $shimgraph.append('<img src="/static/tiny-shim-b.gif"></img>');
                            }
                        }

                        /*
                        for( j=0; j<Math.random()*20; j++ ){
                            $shimgraph.append('<img src="/static/tiny-shim-b.gif"></img>');
                        }
                        */
                    }

                    //Save the location of the input, before it gets replaced.
                    var offset = $(x).offset();

                    //Replace the input with the shimgraph
                    $(x).replaceWith($shimgraph);
                    //$shimgraph.hide();

                    //Position shimgraph, after all the images load
                    $shimgraph.imagesLoaded( function(){
                        $shimgraph
                            .fadeIn("fast")
                            .offset({ top: offset.top-5, left: offset.left-$shimgraph.width()-4 })

                    });
                });
            }else{
                $("input", $d).each(function(i,x){
                    //Create shimgraph and content
                    var $shimgraph = $('<div class="shim-graph-b"></div>');
                    for( j=0; j<Math.random()*20; j++ ){
                        $shimgraph.append('<img src="/static/tiny-shim-b.gif"></img>');
                    }

                    //Save the location of the input, before it gets replaced.
                    var offset = $(x).offset();

                    //Replace the input with the shim-graph
                    $(x).replaceWith($shimgraph);                    
                });
            }
		});
    }
};
