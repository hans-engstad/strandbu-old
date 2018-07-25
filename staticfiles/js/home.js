
var start = new Date();
start.setDate(start.getDate() + 1);

var end = new Date();
end.setDate(end.getDate() + 2);

var maxDate = new Date();
maxDate.setFullYear(maxDate.getFullYear() + 1);

var startString = start.getDate() + "." + start.getMonth() + "." + start.getFullYear().toString().substr(-2);
var endString = end.getDate() + "." + end.getMonth() + "." + end.getFullYear().toString().substr(-2);

$(function() {
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
});

$(function() {
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
			end = new Date(end);
			end.setHours(0,0,0,0);
			//Check that to-date is after this date
			_start = moment($('#daterange-from-date').val(), 'DD.MM.YY').toDate();
			_start.setHours(0,0,0,0);
			if(_start >= end)
			{
				//Set from-date before to-date
				start = new Date(end.setDate(end.getDate() - 1));
				$('#daterange-from-date').data('daterangepicker').setStartDate(start);
				$('#daterange-from-date').data('daterangepicker').setEndDate(start);
			}
		}
	);
});

$('#daterange-from-date').val(startString);
$('#daterange-to-date').val(endString);


function onPersonsClick(){
	var id = '#persons-input';
	if($(id).val() == "")
	{
		$(id).val("1");
	}
	$(id).select();
}
