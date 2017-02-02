
// function which retrieves a cookie based on its name
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


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

  $('#prefLabelEdit').click(activateEditing);
  $('#prefLabelSave').click(saveEditedField);

  function activateEditing(){
      var fieldName = $(this).data('type');
      var saveId = "#" + fieldName + "Save";
      var fieldElement =  "#" + fieldName;
      $(saveId).show();
      $(this).hide();
      var prefLabelValue = $(fieldElement).text()
      $(fieldElement).replaceWith('<input id="prefLabel" type="text" value="'
                                   + prefLabelValue + '" />')
  };

  function saveEditedField(){

      var fieldName = $(this).data('type')
      var editId = "#" + fieldName + "Edit";
      var fieldElementId =  "#" + fieldName

      $.ajax({
         type:"POST",
         url:"/edit_property/",
         data: {
                'concept': conceptCode,
                'lang': $('#js-change-language option:selected').val(),
                'value': $(fieldElementId).val(),
                'type': fieldName,
                'csrfmiddlewaretoken': getCookie('csrftoken'),
               },
         success: function(data){
             if(data['data']=='success'){
                var newElement = '<span id="' + fieldName +'">' +
                                 data['value'] + '</span>';
                $(fieldElementId).replaceWith(newElement);
             }
             else{
                var prefLabelValue = $(fieldElementId).text()
                var newElement = '<span id="' + fieldName + '">' +
                                 prefLabelValue + '</span>';
                $(fieldElementId).replaceWith(newElement)
             }
         }
      });

      $(this).hide();
      $(editId).show();
  }

});
