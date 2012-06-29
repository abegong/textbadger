var launchInformalEditor = function( codebook_json ){
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
        codebookModel.attachControlsToQuestion(0);
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
