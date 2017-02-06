
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
  $('#scopeNoteEdit').click(activateEditing);
  $('#scopeNoteSave').click(saveEditedField);
  $('#definitionEdit').click(activateEditing);
  $('#definitionSave').click(saveEditedField);
  $('#sourceEdit').click(activateEditing);
  $('#sourceSave').click(saveEditedField);

  function prepareElements(fieldName){
    fields = {};
    fields['saveId'] = "#" + fieldName + "Save";
    fields['fieldElement'] = "#" + fieldName;
    fields['inputElement'] = fieldName + "Input";
    fields['inputId'] = "#" + fieldName + "Input";
    fields['editId'] = "#" + fieldName + "Edit";
    fields['emptyId'] = "#" + fieldName + "Empty";

    return fields
  }

  function cancelEditing(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName)
    $(fields['saveId']).hide();
    $(fields['fieldElement']).show();
    if (concept[fieldName] == ''){
        $(fields['emptyId']).show();
    }
    $(fields['inputId']).remove();
    $(this).val('Edit');
    $(this).unbind('click', cancelEditing);
    $(this).bind('click', activateEditing);

  };

  function activateEditing(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName)
    $(fields['saveId']).show();
    $(fields['emptyId']).hide();
    $(fields['fieldElement']).hide();
    $(this).val('Cancel');
    $(this).unbind('click', activateEditing);
    $(this).bind('click', cancelEditing);
    var prefLabelValue = $(fields['fieldElement']).text()
    $('<' + $(this).data('html-tag') +' id="' + fields['inputElement']
                    + '"/>').insertBefore(fields['fieldElement']);
    $(fields['inputId']).val(concept[fieldName]);
  };

  function saveEditedField(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName)

    $.ajax({
       type:"POST",
       url:"/edit_property/",
       data: {
              'concept': conceptCode,
              'language': $('#js-change-language option:selected').val(),
              'value': $(fields['inputId']).val(),
              'name': fieldName,
              'csrfmiddlewaretoken': getCookie('csrftoken'),
             },
       error: function(e) {
       },
       success: function(data){
          $(fields['fieldElement']).text(data['value']);
          concept[fieldName] = data['value'];

       }
    });

    $(fields['fieldElement']).show();
    $(fields['inputId']).remove();
    $(this).hide();
    $(fields['editId']).val('Edit');
    $(fields['editId']).bind('click', activateEditing);
    $(fields['editId']).unbind('click', cancelEditing);
    $(fields['editId']).show();
  }

});
