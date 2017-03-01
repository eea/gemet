
$(document).ready(function () {
	// change language
	// bind change event to select

  $('#js-change-language').on('change', function () {
    var url = $(this).find(':selected').attr('href'); // get selected value
    if (url) { // require a URL
      window.location = url; // redirect
    }
    return false;
  });
});
