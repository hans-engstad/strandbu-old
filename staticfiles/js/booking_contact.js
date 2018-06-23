function select(id){
	 $(id).prevAll('input.select-dropdown').trigger('open');

	console.log("selecting " + id);
}