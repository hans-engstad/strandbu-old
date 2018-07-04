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