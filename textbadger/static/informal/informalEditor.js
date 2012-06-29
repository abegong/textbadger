var attachControlsToQuestion = function(i){
    //Change the targetQuestion in the model
    console.log(i);
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
};

var launchInformalEditor = function( codebook_json ){
//  initControls();

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
  
    codebookModel.loadQuestions(codebook_json);
    
    //Load the template and knockout model dynamically.
    $.get("/static/informal/_informalTemplateKO.htm", function(template){
        $("body").append(template);
        ko.applyBindings(codebookModel);
        codebookModel.addStylesToCodebook();
        attachControlsToQuestion(0);
    }, "text");

};

var launchInformalViewer = function( codebook_json ){
    codebookModel.loadQuestions(codebook_json);
    
    //Load the template and knockout model dynamically.
    $.get("/static/informal/_informalTemplateKO.htm", function(template){
        $("body").append(template);
        ko.applyBindings(codebookModel);
//        codebookModel.addStylesToCodebook();
//        attachControlsToQuestion(0);
    }, "text");

};
