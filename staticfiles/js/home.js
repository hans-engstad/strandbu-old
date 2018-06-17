//FROM DATE
$('#from-date-field').datepicker({
    format: 'dd/mm/yy',
    startDate: '+1d',
    weekStart: 1,
    maxViewMode: 0,
});

$('#from-date-field').datepicker().on('changeDate', function(e){ updateDateTextField(e.date, '#from-date-field', '#from-date-field-form'); });
$('#from-date-field').datepicker().on('hide', function(e){ updateDateTextField(e.date, '#from-date-field', '#from-date-field-form'); });

$( "#from-date" ).click(function() {
	$('#from-date-field').data("datepicker").show();
});

//TO DATE
$('#to-date-field').datepicker({
    format: 'dd/mm/yy',
    startDate: '+2d',
    weekStart: 1,
    maxViewMode: 0,
});

$('#to-date-field').datepicker().on('changeDate', function(e){ updateDateTextField(e.date, '#to-date-field', '#to-date-field-form'); });
$('#to-date-field').datepicker().on('hide', function(e){ updateDateTextField(e.date, '#to-date-field', '#to-date-field-form'); });

$( "#to-date" ).click(function() {
	$('#to-date-field').data("datepicker").show();
});


function updateDateTextField(date, id, form_id){
	if(date != undefined)
	{
		var daysOfWeek = ["søn", "man", "tir", "ons", "tor", "fre", "lør"];
		var months = ["jan", "feb", "mar", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "des"];

		var dateString = daysOfWeek[date.getDay()] + ". " + date.getDate() + "." + months[date.getMonth()];
		
		$(id).val(dateString);
		$(form_id).val(date.toUTCString());
	}
}

function submitSearch(){
	console.log("submitting");
	$('#search-cabin-form').submit();
}