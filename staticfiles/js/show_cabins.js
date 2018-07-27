function showCabin(number){
	//Reset all 
	$('.cabin-result-img').addClass("hide");
	$('.cabin-result-label').removeClass("hide");
	$('.cabin-result-content').addClass("hide");

	//Show selected cabin
	$('#cabin-result-img-' + number).removeClass("hide");
	$('#cabin-result-label-' + number).addClass("hide");
	$('#cabin-result-content-' + number).removeClass("hide");
}

function ChangeSearchShow(){
	$('#search-box').removeClass("hide");
	$('#change-search-link').html("Skjul endre søk")
	$('#change-search-link').attr("onClick", 'ChangeSearchHide()');
}

function ChangeSearchHide(){
	$('#search-box').addClass("hide");
	$('#change-search-link').html("Endre søk")
	$('#change-search-link').attr("onClick", 'ChangeSearchShow()');
}

function BackToOverview(){
	console.log("Submitting");
	$('#back-to-overview-form').submit();
}