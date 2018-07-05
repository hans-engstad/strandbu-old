

$('#daterange-picker').datepicker({
    format: 'dd.mm.yy',
    startDate: '+2d',
    weekStart: 1,
    maxViewMode: 0,
    orientation: 'bottom',
    container: '#daterange-picker'
});


/*//FROM DATE
$('#from-date-field').datepicker({
    format: 'dd.mm.yy',
    startDate: '+1d',
    weekStart: 1,
    maxViewMode: 0,
    orientation: 'bottom',
    container:'#from-date'
});

$('#from-date-field').datepicker().on('show', function(e){ onDatepickerShow(e.date, '#from-date-field'); });
$('#from-date-field').datepicker().on('changeDate', function(e){ onDatepickerChange(e.date, '#from-date-field-form'); });
$('#from-date-field').datepicker().on('hide', function(e){ onDatepickerHide(e.date, '#from-date-field'); });

$( "#from-date" ).click(function() {
	$('#from-date-field').data("datepicker").show();
});

//TO DATE
$('#to-date-field').datepicker({
    format: 'dd.mm.yy',
    startDate: '+2d',
    weekStart: 1,
    maxViewMode: 0,
    orientation: 'bottom',
    container: '#to-date'
});

$('#to-date-field').datepicker().on('show', function(e){ onDatepickerShow(e.date, '#to-date-field'); });
$('#to-date-field').datepicker().on('changeDate', function(e){ onDatepickerChange(e.date, '#to-date-field-form'); });
$('#to-date-field').datepicker().on('hide', function(e){ onDatepickerHide(e.date, '#to-date-field'); });

$( "#to-date" ).click(function() {
	$('#to-date-field').data("datepicker").show();
});

*/


$('#persons-input').click(function(){
	onPersonsClick();
});
$('#persons-header').click(function(){
	onPersonsClick();
});

function setup(){
	// datepickersSetup();
	// personAmountSetup();
}

function datepickersSetup(){

	var date = new Date();	//Current date

	date = new Date(date.getFullYear(), date.getMonth(), date.getDate() + 1);	//Tomorrow
	var dateString_from = convertDateToDisplay_num(date);

	date = new Date(date.getFullYear(), date.getMonth(), date.getDate() + 1);	//Day after tomorrow
	var dateString_to = convertDateToDisplay_num(date);
	
	//Set visual fields
	$('#from-date-field').attr("placeholder", dateString_from);
	$('#to-date-field').attr("placeholder", dateString_to);

	//Set form fields
	$('#from-date-field-form').val(dateString_from);
	$('#to-date-field-form').val(dateString_to);
}

function personAmountSetup(){
	$('#person-amount-form').val("1");
}

function onPersonsClick(){
	var id = '#persons-input';
	if($(id).val() == "")
	{
		$(id).val("1");
	}
	$(id).select();

	//Show popover
	//$(id).attr("data-content", "heisann")
	//$(id).popover();
}

function onDatepickerShow(date, field_id){
	
}

function onDatepickerHide(date, field_id){
	//field value will override date on datepicker
	var fieldValue = $(field_id).val();
}

function onDatepickerChange(date, form_id){
	//Update form fields
	$(form_id).val(convertDateToDisplay_num(date));
}





function updateDateTextFieldDisplayed(id, dateString){
	$(id).val(dateString);
}

function convertDateToDisplay_text(date){
	var daysOfWeek = ["søn", "man", "tir", "ons", "tor", "fre", "lør"];
	var months = ["jan", "feb", "mar", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "des"];

	var dateString = daysOfWeek[date.getDay()] + ". " + date.getDate() + "." + months[date.getMonth()];

	return dateString;
}

function convertDateToDisplay_num(date){
	var day = date.getDate();
	day = day < 10 ? "0" + day : day;

	var month = date.getMonth() + 1;
	month = month < 10 ? "0" + month : month;

	var year = date.getFullYear().toString().substr(2, 2);

	var dateString = day + "." + month + "." + year;

	return dateString;
}

function convertDateNumToDate(dateNum){
	if(dateNum.length != 8)
	{
		return null;
	}

	var currentDate = new Date();
	var yearStart = currentDate.getFullYear().toString().substr(0, 2);	//two first numbers in year. 2018 -> 20

	var day = dateNum.substr(0, 2);
	var month = dateNum.substr(3, 2);
	var year =  yearStart + dateNum.substr(6, 2);

	try{
		var monthIndex = parseInt(month) - 1;
		var chosenDate = new Date(year, monthIndex, day);

		return chosenDate;

	} catch(err) {
		console.log(err);
		return null;
	}

	



}

function submitSearch(){
	if($('#persons-input').val() == "")
	{
		$('#person-amount-form').val("1");
	}
	else
	{
		$('#person-amount-form').val($('#persons-input').val());
	}



	
	$('#search-cabin-form').submit();
}


setup();
