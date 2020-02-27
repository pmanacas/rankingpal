//we need this custom function because jQuery.unique can't handle strings, only DOM elements
function unique(arr){
    return jQuery.grep(arr,function(v,k){
                return jQuery.inArray(v,arr) === k;
            });
}
jQuery.fn.focusNextInputField = function() {
    return this.each(function() {
        var fields = jQuery(this).parents('form:eq(0),body').find('input');
        var index = fields.index( this );
        if ( index > -1 && ( index + 1 ) < fields.length ) {
            fields.eq( index + 2 ).focus();
        }
        return false;
    });
};

//form validation funtion
function checkForm(){

    //disable submit button
    jQuery('#submit-btn').attr('disabled', 'disabled');

    //check sum zero
        pontos1 = jQuery("#entry_5").val();
        pontos2 = jQuery("#entry_6").val();
        pontos3 = jQuery("#entry_7").val();
        pontos4 = jQuery("#entry_8").val();
        var sum = (pontos1-0) + (pontos2-0) + (pontos3-0) + (pontos4-0);
        if(sum!=0) {
            alert("A soma não deu zero.");
            jQuery('#submit-btn').attr('disabled', '');
            return false;
        }

    //load names
        selectedNames = [];
        nome1 = jQuery("#entry_1").val();
        nome2 = jQuery("#entry_2").val();
        nome3 = jQuery("#entry_3").val();
        nome4 = jQuery("#entry_4").val();
        selectedNames = [nome1,nome2,nome3,nome4];


    //check empty
        if(nome1=="" || nome2=="" || nome3=="" || nome4=="" || pontos1=="" || pontos2=="" || pontos3=="" || pontos4==""){
            alert("É pá vê lá se preencheste tudo.");
            jQuery('#submit-btn').attr('disabled', '');
            return false;
        }
    
    //check values against name_list
        submit_error = 0;
        jQuery.each(selectedNames, function(index, value) {
            if(jQuery.inArray(value, name_list)==-1) {
                submit_error = submit_error + 1;
            }
        });
        if(submit_error != 0) {
            alert("Um dos nomes está errado. Escreve as primeiras letras e escolhe um dos nomes sugeridos.");
            jQuery('#submit-btn').attr('disabled', '');
            return false;
        }

    //check duplicate names
        uniqueSelectedNames = [];
        uniqueSelectedNames = unique(selectedNames);
        if(uniqueSelectedNames.length != 4) {
            alert("Nomes repetidos.");
            jQuery('#submit-btn').attr('disabled', '');
            return false;
        }
    jQuery("#wait").append("<p>A calcular...</p>");
    return true;
}
//end form validation funtion


//init some vars
var name_list = []; //array to store list of values for autocomplete
var keys_list = []; //array to store list of values for autocomplete
var selectedNames =[];
var nome1 = "";
var nome2 = "";
var nome3 = "";
var nome4 = "";
var pontos1 = 0;
var pontos2 = 0;
var pontos3 = 0;
var pontos4 = 0;
var dif = 0;
var submit_error = 0;

//update pts label
function updatePts(element){
				var v = jQuery(element).attr("value");
				var t = jQuery(element).parent().next().children("label").children("span").text(v);
                var key = keys_list[jQuery.inArray(element.value, name_list)];
                jQuery(element).next().val(key);
                jQuery(element).focusNextInputField();
}

//load the data into an array
function loadWorksheet(data){
	for (var i = 0; i < data.length; i++) {
		var name = data[i].label;
		var key = data[i].value;
        name_list.push(name);
        keys_list.push(key);
        }


//setup the scriptaculous autocomplete text fields
	new Autocompleter.Local('entry_1', 'list1', name_list, {partialChars:1,frequency:0.001,
							afterUpdateElement:function(element,selectedElement){
								updatePts(element);
							}
							}
	);
	new Autocompleter.Local('entry_2', 'list2', name_list, {partialChars:1,frequency:0.001,
							afterUpdateElement:function(element,selectedElement){
								updatePts(element);
							}
							}
	);
	new Autocompleter.Local('entry_3', 'list3', name_list, {partialChars:1,frequency:0.001,
							afterUpdateElement:function(element,selectedElement){
								updatePts(element);
							}
							}
	);
	new Autocompleter.Local('entry_4', 'list4', name_list, {partialChars:1,frequency:0.001,
							afterUpdateElement:function(element,selectedElement){
								updatePts(element);
							}
							}
	);


//enable form inputs
jQuery('input').attr('disabled', '');

//reset form
document.getElementById("ss-form").reset();

//set focus to 1st field
jQuery("input:text:visible:first").focus();

}//end of function loadWorksheet

// *** CODE TO EXECUTE ON LOAD BELOW ***
jQuery(document).ready(function(){

// //Retrieve the data

	var script = document.createElement('script');
	script.setAttribute('src', '/playerlist');
	script.setAttribute('id', 'dataScript');
	script.setAttribute('type', 'text/javascript');
	document.documentElement.firstChild.appendChild(script);

//bind function to update last score box to give sum zero
jQuery("#entry_5,#entry_6,#entry_7").keyup(function() {
	pontos1 = jQuery("#entry_5").val();
	pontos2 = jQuery("#entry_6").val();
	pontos3 = jQuery("#entry_7").val();
	pontos4 = jQuery("#entry_8").val();
	var dif = 0 - (parseInt(pontos1) + parseInt(pontos2) + parseInt(pontos3));
	jQuery("#entry_8").val(dif);
});

//bind function to prevent form submit when hitting enter on Pts fields
jQuery('#entry_5,#entry_6,#entry_7').keydown(function(e) {
	code = e.keyCode ? e.keyCode : e.which;
	if(code.toString() == 13) {
		jQuery(e.currentTarget).focusNextTabIndex();
		return false;
	}
});


});//end of code to execute on load