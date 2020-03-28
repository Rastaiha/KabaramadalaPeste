var didSet = false;
setInterval(
	function() {
		(function($) {
			$(document).ready(function(){
				if (!didSet) {
				    $('#judgeablesubmit_form').submit(function() {
				        var c = confirm("Continue Submitting? After changing status to Correct/Wrong you can't change it anyway.");
				        return c;
				    });
				    didSet = true;
				}
			})
		})(django.jQuery)
	}, 400
)