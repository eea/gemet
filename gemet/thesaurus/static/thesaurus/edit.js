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
  $('#prefLabelEdit').click(activateEditing);
  $('#prefLabelSave').click(saveEditedField);
  $('#scopeNoteEdit').click(activateEditing);
  $('#scopeNoteSave').click(saveEditedField);
  $('#definitionEdit').click(activateEditing);
  $('#definitionSave').click(saveEditedField);
  $('#sourceEdit').click(activateEditing);
  $('#sourceSave').click(saveEditedField);
  $('#otherAdd').click(activateOtherFieldAdd);
  $('#themeAdd').click(activateSelectEditing);
  $('#groupAdd').click(activateSelectEditing);
  $('#broaderAdd').click(activateSelectEditing);
  $('#relatedAdd').click(activateSelectEditing);
  $('#narrowerAdd').click(activateSelectEditing);
  $('#alternativeAdd').click(activateAlternativeAdd);
  $('.removeParent').click(removeParent);

  function prepareElements(fieldName){
    fields = {};
    fields['saveButton'] = "#" + fieldName + "Save";
    fields['fieldElement'] = "#" + fieldName;
    fields['inputTag'] = fieldName + "Input";
    fields['inputTagId'] = "#" + fieldName + "Input";
    fields['editButtonId'] = "#" + fieldName + "Edit";
    fields['emptyTagId'] = "#" + fieldName + "Empty";
    fields['addButtonId'] = "#" + fieldName + "Add";
    fields['cancelButtonId'] = "#" + fieldName + "Cancel";
    fields['fieldParent'] = "#parent-" + fieldName;
    return fields
  }

  /* prefLabel, definition, scopeNote, source cancel */
  function cancelEditing(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName);
    $(fields['saveButton']).hide();
    $(fields['fieldElement']).show();
    $(fields['fieldParent']).show();

    if ($(fields['fieldElement']).data('value') == ''){
        $(fields['emptyTagId']).show();
    }
    $(fields['inputTagId']).remove();
    $(this).hide()
    $(this).unbind('click', cancelEditing);
    $(fields['editButtonId']).show()
    $(fields['editButtonId']).bind('click', activateEditing);
  };

  /* alternatives cancel */
  function cancelAdd(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName);
    $(fields['saveButton']).hide();
    $(fields['saveButton']).unbind('click', saveProperty);
    $(fields['inputTagId']).remove();
    $(fields['addButtonId']).show();
    $(fields['addButtonId']).bind('click', activateAlternativeAdd);
    $(this).hide();
    $(this).unbind('click', cancelAdd);
  };

  /* themes group narrow broader related cancel */
  function cancelSelectEditing(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName);
    $(fields['saveButton']).hide();
    $(fields['saveButton']).unbind('click', saveConceptRelation);
    $(fields['inputTagId']).remove();
    $(fields['addButtonId']).show();
    $(fields['addButtonId']).bind('click', activateSelectEditing);
    $(this).hide();
    $(this).unbind('click', cancelSelectEditing);
    $(fields['fieldElement']).children('.removeParent').bind('click', removeParent);
    $(fields['fieldElement']).children('.removeParent').show();
  };

  /* other relations cancel */
  function cancelOtherRelationEditing(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName);
    $(fields['saveButton']).hide();
    $(fields['saveButton']).unbind('click', saveOtherRelation);
    $('.otherInput').hide();
    $('.otherInput').val('');
    $(fields['inputTagId']).remove();
    $(fields['addButtonId']).show();
    $(fields['addButtonId']).bind('click', activateOtherFieldAdd);
    $(this).hide();
    $(this).unbind('click', cancelOtherRelationEditing);
  };

  /* set all types of other relations */
  function setAllOtherConcepts(relation_types, elementId){
    for(index in relation_types){
      // creating options using received data
      var $option = $('<option value=' + relation_types[index]['id'] + '>'
                    + relation_types[index]['label'] + '</option>');
      var labelName = relation_types[index]['name'];
      $option.attr('data-label', labelName);
      $(elementId).append($option);
    }
    $(fields['inputTagId']).show();
  }

  /* set all concepts for relations (themes, groups, terms) */
  function getAllConcepts(url, elementId, type){
    $(elementId).empty(); // removes previous option elements from select
    $.ajax({ // ajax call to retrieve all concepts used as options
      type: "GET",
      url: url,
      error: function(e) {
      },
      success: function(data){
        if(type='other')
          setAllOtherConcepts(data['relation_types'], elementId);

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
        $(fields['inputTagId']).show();
      }
    });
  };

  /* prefLabel, definition, scopeNote, source enable editing */
  function activateEditing(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName);
    $(fields['saveButton']).show(); // Show save button
    $(fields['emptyTagId']).hide(); // Hide empty property warning
    $(fields['fieldParent']).hide();
    $('<' + $(this).data('html-tag') +' id="' + fields['inputTag']
      + '"/>').insertAfter(fields['fieldParent']);
    $(this).hide();
    $(this).unbind('click', activateEditing);
    $(fields['cancelButtonId']).show()
    $(fields['cancelButtonId']).bind('click', cancelEditing);
    $(fields['inputTagId']).val($(fields['fieldElement']).data('value'));
  };

  /* themes group narrow broader related enable editing */
  function activateSelectEditing(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName); //preparing selectors
    $(fields['saveButton']).show();
    $(fields['saveButton']).bind('click', saveConceptRelation);
    $(fields['cancelButtonId']).show();
    $(fields['cancelButtonId']).bind('click', cancelSelectEditing);
    $(this).hide();
    $(this).unbind('click', activateSelectEditing);
    url = $(this).data('href');
    $('<select id="' + fields['inputTag'] + '" hidden/>').
    insertBefore(fields['cancelButtonId']);
    getAllConcepts(url, fields['inputTagId'], fieldName);
    $(fields['fieldElement']).children('.removeParent').unbind('click', removeParent);
    $(fields['fieldElement']).children('.removeParent').hide();
  };

  /* alternatives enable editing */
  function activateAlternativeAdd(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName)
    $(fields['saveButton']).show();
    $(fields['saveButton']).bind('click', saveProperty);
    $(fields['cancelButtonId']).show();
    $(fields['cancelButtonId']).bind('click', cancelAdd);
    $(this).unbind('click', activateAlternativeAdd);
    $(this).hide();
    $('<input id="' + fields['inputTag'] + '"/>').
    insertBefore(fields['cancelButtonId']);
  };

  /* other relations enable editing */
  function activateOtherFieldAdd(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName); //preparing selectors
    $(fields['saveButton']).show();
    $(fields['saveButton']).bind('click', saveOtherRelation);
    $(fields['cancelButtonId']).show();
    $(fields['cancelButtonId']).bind('click', cancelOtherRelationEditing);
    $(this).hide();
    $(this).unbind('click', activateOtherFieldAdd);
    var url = $(this).data('href');
    $('<select id="' + fields['inputTag'] +
    '" hidden/>').insertBefore(fields['cancelButtonId']);
    $('.otherInput').show();
    getAllConcepts(url, fields['inputTagId'], fieldName);
  }

  /* append the new relation to html (themes, groups, related relations) */
  function addElement(parentId, parentText, url, fields, fieldName, conceptUrl){
    if (['broader', 'related', 'narrower'].includes(fieldName))
        parentText = "<a href='" + conceptUrl + "'>" + parentText + "</a></li>";
    var $newParent = $('<li id=' + fieldName + parentId +
                     " class=status-0" +
                     " value=" + parentId + ">" + parentText + "</li>");
    var $newParentDelete = $('<input>')
    $newParentDelete.addClass("removeParent");
    $newParentDelete.attr("type", "button");
    $newParentDelete.val("Delete");
    $newParentDelete.attr("data-field", fields['fieldElement'] + parentId);
    $newParentDelete.attr("data-href", url);
    $newParentDelete.attr("data-type", fieldName);
    $(fields['fieldElement']).append($newParent);
    $(fields['fieldElement']).append($newParentDelete);
  }

  /* prefLabel, definition, scopeNote, source save new property */
  function saveEditedField(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName);
    var url = $(fields['fieldParent']).data('href');
    var fieldStatus = $(fields['fieldElement']).data('status');
    $.ajax({
      type: "POST",
      url: url,
      data: {
             'value': $(fields['inputTagId']).val(),
             'csrfmiddlewaretoken': getCookie('csrftoken')
            },
      error: function(e) {
      },
      success: function(data){
        if (fieldStatus == 0) { // pending field
          $(fields['fieldElement']).text(data['value']);
          $(fields['fieldElement']).data('value', data['value']);
        }
        if (fieldStatus == 1){ // published field
          var oldField = $(fields['fieldElement']).clone();
          oldField.attr('class', 'status-3');
          oldField.removeAttr('data-status');
          oldField.removeAttr('id');
          oldField.removeAttr('data-value');
          oldField.removeAttr('data-href');
          $(fields['fieldElement']).attr('class', 'status-0');
          $(fields['fieldElement']).data('status', '0');
          $(fields['fieldElement']).text(data['value']);
          $(fields['fieldElement']).data('value', data['value']);
          $(fields['fieldElement']).before(oldField);
          $(fields['fieldElement']).before('<br>'); // TODO remove this once we have proper styling
        }
        if (fieldStatus == null){ // property not defined yet
          $newPropertyTag = $('<span>' + data['value'] + '</span>');
          $newPropertyTag.data('status', '0');
          $newPropertyTag.attr('id', fieldName);
          $newPropertyTag.data('value', data['value']);
          $newPropertyTag.attr('class', 'status-0');
          $(fields['fieldParent']).append($newPropertyTag);
        }
      }
    }).done(function() {
        $(fields['cancelButtonId']).click();
   });
  }

  /* themes group narrow broader related save new property */
  function saveConceptRelation(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName);
    // define a selector for all options of the targeted select
    var selector = fields['inputTagId'] + " option:selected";
    var parentId = $(selector).val();
    var parentText = $(selector).text();
    var addUrl = $(selector).data('href_add');
    var removeUrl = $(selector).data('href');
    var url = $(fields['addButtonId']).data('href');
    var conceptUrl = $(selector).data('href_concept');
    $.ajax({
       type: "POST",
       url: addUrl,
       data: {
              'csrfmiddlewaretoken': getCookie('csrftoken'),
             },
       error: function(e) {
       },
       success: function(data){
         addElement(parentId, parentText, removeUrl, fields, fieldName,
                    conceptUrl);
         $(fields['cancelButtonId']).click();
       }
    });
  }

  /* alternatives save new property */
  function saveProperty(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName)
    var url = $(fields['fieldElement']).data('href')
    $.ajax({
       type: "POST",
       url: url,
       data: {
              'value': $(fields['inputTagId']).val(),
              'csrfmiddlewaretoken': getCookie('csrftoken'),
             },
       error: function(e) {
       },
       success: function(data){
        $('#alternativeList').append("<i id='alternative" + data['id'] +
                                     "' data-value='" + data['value'] +
                                     "' class='status-" + data['status'] + "'>" +
                                     data['value'] + ";</i>");
        $deleteButton = $("<input class='removeParent' type='button' " +
                          "data-type='alternative' value='Delete' data-field-id='#alternative" + data['id'] +"' />");
        $deleteButton.attr('data-field', "#alternative" + data['id']);
        $deleteButton.bind('click', removeParent);
        $deleteButton.attr('data-href', data['url']);
        $('#alternativeList').append($deleteButton);
        $(fields['cancelButtonId']).click();
       }
    });
  }

  /* other relations save foreign relation */
  function saveOtherRelation(){
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName);
    var selector = fields['inputTagId'] + " option:selected";
    var propertyTypeId = $(selector).val();
    var propertyTypeName = $(selector).text();
    var propertyLabel = $(fields['fieldElement'] + "Value").val();
    var parentUrl = $(fields['fieldElement'] + "Url").val();
    var addUrl = $(this).data('href');
    $.ajax({
       type: "POST",
       url: addUrl,
       data: {
              'csrfmiddlewaretoken': getCookie('csrftoken'),
              'rel_type': propertyTypeId,
              'uri': parentUrl,
              'label': propertyLabel,
              'property_type': propertyTypeId,
             },
       error: function(e) {
       },
       success: function(data){
         var $elementType = $('#all-other div:contains("' + propertyTypeName + '")').parent();
         var relationWrapper = $("<div class='status-0'></div>");
         var relationField = "<div class='dd' id='other" + data['id'] + "'><a href=" +
         parentUrl + ">" + propertyLabel + "</a></div>"
         var $deleteButton = $('<input class="removeParent" type="button"' +
         'data-type="other" data-field="#other' + data['id'] +
         '" value="Delete"' + 'data-href="' + data['remove_url'] + '"/>');
         relationWrapper.append(relationField);
         relationWrapper.append($deleteButton);
         $deleteButton.bind('click', removeParent);
         if ($elementType.length){
           $elementType.append(relationWrapper);
         }
         else{
           var $newType = $("<li class=''>");
           var $newList = $("<div class='dt'>" +  propertyTypeName + "</div>");
           $newType.append($newList);
           $newType.append(relationWrapper);
           $("#all-other").append($newType);
         }
       }
    }).done(function() {
        $(fields['cancelButtonId']).click();
   });
  }
  /* remove concept, alternative or other relation */
  function removeParent(){
    var strconfirm = confirm("Are you sure you want to delete?");
    if (strconfirm == false) {
        return;
    }
    var fieldName = $(this).data('type');
    var fields = prepareElements(fieldName);
    var url = $(this).data('href');
    var deleteFieldId = $(this).data('field-id');
    var deleteButton = $(this);
    $.ajax({
       type: "POST",
       url: url,
       data: {
              'csrfmiddlewaretoken': getCookie('csrftoken'),
              'value': $(deleteFieldId).data('value'),
             },
       error: function(e) {
       },
       success: function(data){
         $(deleteFieldId).attr('class', 'status-3'); // Change status
         // TODO define delete behaviour deleteButton.remove(); // Remove delete button
       }
    });
  };

});
