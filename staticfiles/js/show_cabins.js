

var chosenCabin = -1;
function accordionClick(cabinNumber){

	if($('#content-' + cabinNumber).hasClass('collapsing'))
	{
		//in the process of collapsing, do nothing
		return;
	}



	//Show right arrow for all accordion elements
	$('.cabin-acc-right').removeClass("hide");
	$('.cabin-acc-down').addClass("hide");

	//Reset all colors
	$('.accordion-label-box').removeClass("accordion-label-selected");

	if(chosenCabin == cabinNumber)
	{
		chosenCabin = -1;
		return;
	}

	//Show down arrow for selected cabin
	$('#right-arrow-' + cabinNumber).addClass("hide");
	$('#down-arrow-' + cabinNumber).removeClass("hide");

	console.log("adding to label " + cabinNumber);

	console.log($('label-' + cabinNumber));

	$('#label-' + cabinNumber).addClass("accordion-label-selected");


	chosenCabin = cabinNumber;
}