// Add async to this function during compile time.
function changeFloatForm(a){
	// FloatString is for jQuery querying. FloatForm is for normal Javascript manipulation of element.
	// Milliseconds is milliseconds to fade, fademode is mode to fade.
	var floatString = "#floatform",floatForm = document.getElementById('floatform'), milliseconds = 400, fademode = "swing";
	$(floatString).fadeOut(milliseconds,fademode,function(){
		floatForm.src=a; floatForm.onload = function() {
			$(floatString).fadeIn(milliseconds,fademode);
		}
	});
}