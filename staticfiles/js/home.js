
var min_from_date = parseInt($('#min_from_date').val());

var start = new Date();
start.setDate(start.getDate() + min_from_date);

var end = new Date();
end.setDate(end.getDate() + min_from_date + 1);

var maxDate = new Date();
maxDate.setFullYear(maxDate.getFullYear() + 1);

var startString = start.getDate() + "." + (start.getMonth() + 1) + "." + start.getFullYear().toString().substr(-2);
var endString = end.getDate() + "." + (end.getMonth() + 1) + "." + end.getFullYear().toString().substr(-2);




$('#daterange-from-date').daterangepicker({
	singleDatePicker: true,
	opens: 'center',
	locale: {
		format: 'DD.MM.YY'
	},
	minDate: start,
	startDate: start,
	}, 
	function(start, end, label) {
		//NOTE: start and end parameters are the same
		start = new Date(start);
		start.setHours(0,0,0,0);
		//Check that to-date is after this date
		end = $('#daterange-to-date').data('startDate');
		end.setHours(0,0,0,0);
		if(start >= end)
		{
			//Set to-date after from-date
			end = new Date(start.setDate(start.getDate() + 1));
			$('#daterange-to-date').data('daterangepicker').setStartDate(end);
			$('#daterange-to-date').data('daterangepicker').setEndDate(end);
		}
	}
);


$('#daterange-to-date').daterangepicker({
	singleDatePicker: true,
	opens: 'center',
	locale: {
		format: 'DD.MM.YY'
	},
	minDate: end,
	startDate: end,
	}, 
	function(start, end, label) {
		//NOTE: start and end parameters are the same
		var to_date = new Date(end);
		to_date.setHours(0,0,0,0);
		//Check that to-date is after this date
		var from_date = moment($('#daterange-from-date').val(), 'DD.MM.YY').toDate();

		from_date.setHours(0,0,0,0);
		if(from_date >= to_date)
		{
			//Set from-date before to-date
			from_date = new Date(to_date.setDate(to_date.getDate() - 1));
			$('#daterange-from-date').data('daterangepicker').setStartDate(from_date);
			$('#daterange-from-date').data('daterangepicker').setEndDate(from_date);
		}
	}
);

function daterangeSetup(){
	
	if($('#id_from_date').length)
	{
		startString = $('#id_from_date').val();
	}

	if($('#id_to_date').length)
	{
		endString = $('#id_to_date').val();
	}

	if($('#daterange-from-date').length)
	{
		$('#daterange-from-date').data('daterangepicker').setStartDate(startString);
		$('#daterange-from-date').data('daterangepicker').setEndDate(startString);
	} 
	if($('#daterange-to-date').length)
	{
		$('#daterange-to-date').data('daterangepicker').setStartDate(endString);
		$('#daterange-to-date').data('daterangepicker').setEndDate(endString);
	}
}


function onPersonsClick(){
	var id = '#persons-input';
	if($(id).val() == "")
	{
		$(id).val("1");
	}
	$(id).select();
}


window.onload = daterangeSetup();