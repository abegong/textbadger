var attachControlsToQuestion = function(i){
	//Change the targetQuestion in the model
	codebookModel.targetQuestion(i);

	//Set index variables
	qB = $(".questionBox:eq("+i+")");		//The DOM object for the selected questionBox
	qC = $("#questionControls");				//The DOM object for the questionControls div
	qM = codebookModel.questions()[i];	//The question object in the knockout.js model
	qA = codebookModel.questionArguments[qM.question_type()];	//The questionArguments object in the knockout.js model
/*	alert( ko.toJSON(qA) + "\n" +
		qB + "\n" + 
		qC + "\n" + 
		ko.toJSON(qM.params)
	);
*/

	//Move the control box next to the target question
/*//NEW//
	controlBox = $("#controlBox");
	offset = qB.offset();
	offset.left = controlBox.offset().left;
	controlBox.offset(offset);
*/

	//Add content within the control box: variable type and name
	qC
		.html("<hr/>")
		.append( "Variable type<br/><select data-bind=\"options: questionTypes, value: questions()["+i+"].question_type, event: {change: function(event){codebookModel.questions()['"+i+"'].changeQuestionType(event.target.value);codebookModel.questionTypeChanged();}}\"></select><br/>" )
		.append( "Variable name<input type=\"text\" style=\"width:250px\" data-bind=\"value: questions()["+i+"].var_name, event: {change: function(event){codebookModel.questions()["+i+"].changeQuestionName(event.target.value);}}\"></input><br/>" );

	//Add content within the control box: variable parameters
	for( p in qA ){
		if( p in qM.params ){
//			alert( p + ": " + qM.params[p]() );//+ "\n" + $.isArray( qM.params[p]() ) );// + ": " + $.isArray( qM.params[p]() );
			if( $.isArray( qM.params[p]() ) ){
				qC.append( qA[p].label + "<textarea rows=\"5\" style=\"width:250px\" data-bind=\"event: {change: function(event){codebookModel.questions()['"+i+"'].updateParams('"+p+"', event.target.value.split('\\n'));}}\">" + qM.params[p]().join('\n') + "</textarea><br/>" )
			}
			else{
				qC.append( qA[p].label +"<input type=\"text\" style=\"width:250px\" data-bind=\"value: questions()["+i+"].params."+p+"\"></input><br/>" );
			}
		}
	}

	//Re-bind questionControls
	ko.applyBindings(codebookModel, qC[0]);
};

var initControls = function(){
	//Bring controls online
	/*
	$('#loadJsonButton')
		.after("<textarea id=\"loadJsonInput\" rows=\"30\" cols=\"33\" style=\"postion:absolute; float:left; display:none;\">asdfasdf</textarea>")
		.click(function(){$("#loadJsonInput").show();});

	$('#loadJsonInput')
		.change(function(event){
			try{
				Q = $.parseJSON(event.target.value);
				//This is kind of a hack. KO gets mad is I completely empty an observableArray, so I drop all the items but one, then drop the last one after loading the new questions.
				codebookModel.questions.splice(0,codebookModel.questions().length-1);
				for( q in Q ){ 
					codebookModel.questions.push( new cbQuestion(Q[q].question_type, Q[q].var_name, Q[q].params) );
				}
				codebookModel.questions.splice(0,1);
				$(this).hide();
				attachControlsToQuestion(0);
			}
			catch(err){ alert("JSON is not well formed, or something."); }
		});

	$('#exportJsonButton').click( function(){
		var generator = window.open('', 'exported ', 'height=400,width=600');
		generator.document.write('<html><head><title>CSV</title></head><body><textarea rows="40" cols="80">');
		generator.document.write(ko.toJSON(codebookModel.questions));
		generator.document.write('</textarea></body></html>');
		generator.document.close();
	});
  */
  
	$('#add_control').click( function(){ codebookModel.addQuestion(); } );
	$('#del_control').click( function(){ codebookModel.delQuestion(); } );
	$('#up_control').click( function(){ codebookModel.moveQuestionUp(); } );
	$('#down_control').click( function(){ codebookModel.moveQuestionDown(); } );
};

/*
var loadCodebookModel = function(json){
	try{
		//This is kind of a hack. KO gets mad if I completely empty an observableArray, so I drop all the items but one, then drop the last one after loading the new questions.
		codebookModel.questions.splice(0,codebookModel.questions().length-1);
		//Iterate over questions in the json
		for( q in json ){ 
			codebookModel.questions.push( new cbQuestion(json[q].question_type, json[q].var_name, json[q].params) );
		}
		codebookModel.questions.splice(0,1);
		$(this).hide();
		attachControlsToQuestion(0);
	}
	catch(err){ alert("JSON is not well formed, or something."); }
};
*/

var launchInformalEditor = function( initial_codebook_model ){
  initControls();
  /*
  //Create the default question
	codebookModel.questions([
		new cbQuestion("Static text", "", {} ),
		new cbQuestion("Multiple choice", "", {} ),
		new cbQuestion("Check all that apply", "", {} ),
		new cbQuestion("Two-way scale", "", {} ),
		new cbQuestion("Radio matrix", "", {} ),
		new cbQuestion("Checkbox matrix", "", {} ),
		new cbQuestion("Two-way matrix", "", {} ),
		new cbQuestion("Text box", "", {} ),
		new cbQuestion("Short essay", "", {} ),
		new cbQuestion("Text matrix", "", {} )
	]);
  */
  
  /*
  codebookModel.questions([
		new cbQuestion("Static text", "default_question", {"header_text":"<b>Empty codebook</b><br/><p>Use the control panel on the right to edit this codebook. You can add questions, change question types, and edit question text.</p>"} )
	]);
	*/
//	loadCodebookModel( initial_codebook_model );

    //Add questions to codebookModel
    json = initial_codebook_model;
	for( q in json ){ 
		codebookModel.questions.push( new cbQuestion(json[q].question_type, json[q].var_name, json[q].params) );
	}

	//Load the template and knockout model dynamically.
	$.get("/static/informal/_informalTemplateKO.htm", function(template){
		$("body").append(template);
		ko.applyBindings(codebookModel);
		attachControlsToQuestion(0);
        codebookModel.addCodebookStyles();
/*//NEW//
		$("#controlAccordion").accordion({ event: "mouseover", autoHeight:true });
		//Hack to resize accordion dynamically http://jqueryui.com/demos/accordion/#option-autoHeight
		var autoHeight = $("#controlAccordion").accordion( "option", "autoHeight" );
  	$("#controlAccordion").accordion( "option", "autoHeight", false );
*/
	}, "text");

};

var getInformalJson = function(){
  return( ko.toJSON({'questions':codebookModel.questions()}) );
//  return( ko.toJSON(codebookModel) );
};
