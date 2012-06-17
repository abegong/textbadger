function addCodebookStyles(Q){
	$("input[type=radio]",Q).parent()
    .click( function(event){ if(event.target.type != 'radio' ) { $("input:radio", this).click(); }	})
		.mouseover( function(){ $(this).addClass('mouseoverCell'); })
		.mouseout( function(){ $(this).removeClass('mouseoverCell'); });
	$("input[type=checkbox]",Q).parent()
    .click( function(event){ if(event.target.type != 'checkbox' ) { $("input:checkbox", this).click(); }	})
		.mouseover( function(){ $(this).addClass('mouseoverCell'); })
		.mouseout( function(){ $(this).removeClass('mouseoverCell'); });
}
