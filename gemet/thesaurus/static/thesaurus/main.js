$(document).ready(function () {
	console.log("REAdy");
	// change language
	// bind change event to select
  $('#js-change-language').on('change', function () {
    var url = $(this).find(':selected').attr('href'); // get selected value
    console.log(url);
    if (url) { // require a URL
      window.location = url; // redirect
    }
    return false;
  });
});
