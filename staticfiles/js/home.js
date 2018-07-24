
var start = new Date();
start.setDate(start.getDate() + 1);

var end = new Date();
end.setDate(end.getDate() + 2);

var maxDate = new Date();
maxDate.setFullYear(maxDate.getFullYear() + 1);

var startString = start.getDate() + "." + start.getMonth() + "." + start.getFullYear().toString().substr(-2);
var endString = end.getDate() + "." + end.getMonth() + "." + end.getFullYear().toString().substr(-2);

$('#daterange-picker').daterangepicker({
    // autoApply: true,
    opens: 'center',
    parentEl: "#daterange-picker",
    locale: {
    	format: 'DD.MM.YY'
    },
    startDate: start,
    endDate: end,
    minDate: start,
    maxDate: maxDate,
}, function(start, end, label) {
  console.log('New date range selected: ' + start.format('YYYY-MM-DD') + ' to ' + end.format('YYYY-MM-DD') + ' (predefined range: ' + label + ')');
});

$('#from-date-field').val(startString);
$('#to-date-field').val(endString);


function setup(){
	datepickersSetup();
}

function datepickersSetup(){

	console.log("Setup");

	var date = new Date();	//Current date

	console.log(date);

	date = new Date(date.getFullYear(), date.getMonth(), date.getDate() + 1);	//Tomorrow
	console.log(date);
	var from_date = date;

	date = new Date(date.getFullYear(), date.getMonth(), date.getDate() + 1);	//Day after tomorrow
	var to_date = date;
	


	//Set visual fields
	// $('#from-date-field').val(from_date.getDate() + "." + from_date.getMonth() + "." + from_date.getYear());
	// $('#to-date-field').val(to_date.getDate() + "." + to_date.getMonth() + "." + to_date.getYear());
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
}

setup();
