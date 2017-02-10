
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

  $('#themeAdd').click(activateSelectEditing);
  $('#groupAdd').click(activateSelectEditing);
  $('#broaderAdd').click(activateSelectEditing);
  $('#relatedAdd').click(activateSelectEditing);
  $('#narrowerAdd').click(activateSelectEditing);
  $('.removeParent').click(removeParent);

  function prepareElements(fieldName){
    fields = {};
    fields['saveId'] = "#" + fieldName + "Save";
    fields['fieldElement'] = "#" + fieldName;
    fields['inputElement'] = fieldName + "Input";
    fields['inputId'] = "#" + fieldName + "Input";
    fields['editId'] = "#" + fieldName + "Edit";
    fields['emptyId'] = "#" + fieldName + "Empty";
    fields['fieldAdd'] = "#" + fieldName + "Add";
    fields['fieldCancel'] = "#" + fieldName + "Cancel";
    return fields
  }

  function cancelEditing(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName)
    $(fields['saveId']).hide();
    $(fields['fieldElement']).show();
    if ($(fields['fieldElement']).data('value') == ''){
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
    $('<' + $(this).data('html-tag') +' id="' + fields['inputElement']
                    + '"/>').insertBefore(fields['fieldElement']);
    $(fields['inputId']).val($(fields['fieldElement']).data('value'));
  };

  function saveEditedField(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName)
    var url = $(fields['fieldElement']).data('href')
    $.ajax({
       type: "POST",
       url: url,
       data: {
              'value': $(fields['inputId']).val(),
              'csrfmiddlewaretoken': getCookie('csrftoken'),
             },
       error: function(e) {
       },
       success: function(data){
          $(fields['fieldElement']).text(data['value']);
          $(fields['fieldElement']).data('value', data['value']);

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

  function getAllConcepts(url, elementId, type){
    $(elementId).empty(); // removes previous option elements from select
    $.ajax({ // ajax call to retrieve all concepts used as options
      type: "GET",
      url: url,
      data: {
        'type': type,
      },
      error: function(e) {
      },
      success: function(data){
        list_concepts = data['parents'];
        for(index in list_concepts){
          // creating options using received data
          var $option = $('<option value=' + list_concepts[index]['id'] + '>'
                        + list_concepts[index]['name'] + '</option>');
          var remove_url = list_concepts[index]['href'];
          var add_url = list_concepts[index]['href_add'];
          var concept_url = list_concepts[index]['href_concept']
          $option.attr('data-href', remove_url);// get url to remove the relation
          $option.attr('data-href_add', add_url);// get url to add the relation
          $option.attr('data-href_concept', concept_url);
          $(elementId).append($option);
        }
        $(fields['inputId']).show();
      }
    });
  };

  function cancelSelectEditing(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName)
    $(fields['saveId']).hide();
    $(fields['saveId']).unbind('click', saveConceptRelation);
    $(fields['inputId']).remove();
    $(fields['fieldAdd']).show();
    $(fields['fieldAdd']).bind('click', activateSelectEditing);
    $(this).hide();
    $(this).unbind('click', cancelSelectEditing);
  };

  function activateSelectEditing(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName); //preparing selectors
    $(fields['saveId']).show();
    $(fields['saveId']).bind('click', saveConceptRelation);
    $(fields['fieldCancel']).show();
    $(fields['fieldCancel']).bind('click', cancelSelectEditing);
    $(this).hide();
    $(this).unbind('click', activateSelectEditing);
    url = $(this).data('href');
    $('<select id="' + fields['inputElement'] + '" hidden/>').insertBefore(fields['fieldCancel']);
    getAllConcepts(url, fields['inputId'], fieldName);
  };

  function removeParent(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName);
    var url = $(this).data('href');
    var deleteFieldId = $(this).data('field');
    var deleteButton = $(this);
    $.ajax({
       type: "POST",
       url: url,
       data: {
              'csrfmiddlewaretoken': getCookie('csrftoken'),
              'type': fieldName,
             },
       error: function(e) {
        if ($(fields['inputId']).length)
          getAllConcepts(url, fields['inputId'], fieldName);
       },
       success: function(data){
         $(deleteFieldId).remove();
         deleteButton.remove(); // remove both element and its delete button
         // change options based on database changes
         var url = $(fields['fieldAdd']).data('href')
         if ($(fields['inputId']).length)
           getAllConcepts(url, fields['inputId'], fieldName);
       }
    });
  };

  function addElement(parentId, parentText, url, fields, fieldName, conceptUrl){
    if (['broader', 'related', 'narrower'].includes(fieldName))
        parentText = "<a href='" + conceptUrl + "'>" + parentText + "</a></li>";
    var $newParent = $('<li id=' + fieldName + parentId + " value=" +
                     parentId + ">" + parentText + "</li>");
    var $newParentDelete = $('<input>')
    $newParentDelete.addClass("removeParent");
    $newParentDelete.attr("type", "button");
    $newParentDelete.val("Delete");
    $newParentDelete.attr("data-field", fields['fieldElement'] + parentId);
    $newParentDelete.attr("data-href", url);
    $newParentDelete.attr("data-type", fieldName);
    $newParentDelete.bind('click', removeParent);
    $(fields['fieldElement']).append($newParent);
    $(fields['fieldElement']).append($newParentDelete);
  }

  function saveConceptRelation(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName);
    // define a selector for all options of the targeted select
    var selector = fields['inputId'] + " option:selected";
    var parentId = $(selector).val();
    var parentText = $(selector).text();
    var addUrl = $(selector).data('href_add');
    var removeUrl = $(selector).data('href');
    var url = $(fields['fieldAdd']).data('href');
    var conceptUrl = $(selector).data('href_concept');
    $.ajax({
       type: "POST",
       url: addUrl,
       data: {
              'csrfmiddlewaretoken': getCookie('csrftoken'),
              'type': fieldName,
             },
       error: function(e) {
         if ($(fields['inputId']).length)
           getAllConcepts(url, fields['inputId'], fieldName);
       },
       success: function(data){
         addElement(parentId, parentText, removeUrl, fields, fieldName,
                    conceptUrl);
         if ($(fields['inputId']).length)
            getAllConcepts(url, fields['inputId'], fieldName);
       }
    });
  }
});