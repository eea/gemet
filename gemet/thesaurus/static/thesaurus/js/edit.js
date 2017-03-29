function formatConcept (concept) {
  return concept.name;
}

function formatConceptSelection (concept) {
  var $selection = $("<div selected>" + concept.name + "</div>");
  $selection.attr('data-href', concept.delete_url);
  $selection.attr('data-href_add', concept.add_url);
  $selection.attr('data-href_concept', concept.concept_url);
  $selection.attr('value', concept.id);
  return $selection;
}

function createButton(href, type, bindFunc, cls, icon, text) {
  var $button = $("<button type='button'></button>");
  $button.attr('class', 'btng waves-effect waves-light btn');
  $button.addClass(cls);
  $button.attr("data-href", href);
  $button.attr("data-type", type);
  var $buttonStyle = $("<i class='fa fa-" + icon + "' aria-hidden='true'></i>");
  $button.append($buttonStyle);
  $button.append(" " + text);
  $button.bind('click', bindFunc);
  return $button;
}

function createDeleteButton(href, type){
  return createButton(href, type, deleteRelation, 'deleteRelation', 'times', 'Delete');
}

function createRestoreButton(href, type){
  return createButton(href, type, restoreRelation, 'restoreRelation', 'undo', 'Restore');
}

function errorMessage(message){
  var n = noty({
    text: message,
    layout: 'top',
    theme: 'bootstrapTheme', // or relax
    type: 'error',
    timeout: 2000,
    animation: {
      open: {height: 'toggle'},
      close: {height: 'toggle'},
      easing: 'swing',
      speed: 500 // opening & closing animation speed
    }
  });
}

$(document).ready(function () {
  // select 2 infinite scroll
  $(".select-ajax").each(function() {
      $(this).select2({
      ajax: {
        url: $(this).data('href'),
        dataType: 'json',
        delay: 250,
        data: function (params) {
          return {
            q: params.term, // search term
            page: params.page
          };
        },
        processResults: function (data, params) {
          params.page = params.page || 1;

          return {
            results: data.items,
            pagination: {
              more: (params.page * 30) < data.total_count
            }
          };
        },
        cache: true
      },
      escapeMarkup: function (markup) { return markup; },
      templateResult: formatConcept,
      templateSelection: formatConceptSelection
    });
  });

  $('[data-edit-type="property"]').click(editProperty); // binds every edit button for edit property
  $('[data-save-type="property"]').click(saveProperty); // binds every save button for save property
  $('[data-save-type="concept"]').click(saveConceptRelation); // binds every save button for save relation
  $('#alternativeSave').click(saveAlternativeProperty);
  $('#otherSave').click(saveOtherRelation);
  $('.deleteRelation').click(deleteRelation);
  $('.restoreRelation').click(restoreRelation);
});

  $('.btng.edit, .btng.add').on('click', function(){
    $(this).parent().addClass('visible'); //show cancel and save buttons
    $(this).addClass('hidden'); // hide edit/add button
    $(this).parent().siblings('.input-area').addClass('visible'); // show input area
    $(this).parent().siblings('.text-field').addClass('hidden'); // hide text-area (if necessary)
  });

  $('.btng.save, .btng.cancel').on('click', function(){
    $(this).parent().removeClass('visible'); // hide cancel and save buttons
    $(this).parent().siblings('.input-area').removeClass('visible'); // hide input area
    $(this).parent().siblings('.text-field').removeClass('hidden'); // show text-area (if necessary)
    $('.btng.edit, .btng.add').removeClass('hidden'); // show edit/delete button
  });

  /* prefLabel, definition, scopeNote, source enable editing */
  function editProperty(){
    var inputId = $(this).data('input-id'); //get input id from data
    var textId = $(this).data('text-id'); // get text id from data
    var $inputElement = $(inputId) // get input element
    var $textElement = $(textId) // get text element
    $inputElement.val($textElement.data('value')); // copy text from text tag to input
  };

 /* prefLabel, definition, scopeNote, source save new property */
  function saveProperty(){
    var $inputElement = $($(this).data('input-id')) // get input element
    var $textElement = $( $(this).data('text-id')) // get text element
    var $textList = $($(this).data('parent-id')); // parent element
    var fieldName = $(this).data('type'); // type of property sent to request
    var url = $(this).data('href'); // url for editing
    var fieldStatus = $textElement.data('status'); // status of property edited
    $.ajax({
      type: "POST",
      url: url,
      data: {
             'value': $inputElement.val(),
             'csrfmiddlewaretoken': Cookies.get('csrftoken')
            },
      error: function(e) {
        errorMessage(e.responseJSON.message)
      },
      success: function(data){
        if (fieldStatus == 0) { // pending field
          $textElement.text(data['value']);
          $textElement.data('value', data['value']);
        }
        if (fieldStatus == 1){ // published field
          var oldField = $textElement.clone();
          oldField.attr('class', DELETED_PENDING_CLASS);
          oldField.removeAttr('data-status');
          oldField.removeAttr('id');
          oldField.removeAttr('data-value');
          oldField.removeAttr('data-href');
          $textElement.attr('class', PENDING_CLASS);
          $textElement.data('status', '0');
          $textElement.text(data['value']);
          $textElement.data('value', data['value']);
          $textElement.before(oldField);
        }
        if (fieldStatus == null){ // property not defined yet
          $newPropertyTag = $('<span>' + data['value'] + '</span>');
          $newPropertyTag.data('status', '0');
          $newPropertyTag.attr('id', fieldName);
          $newPropertyTag.data('value', data['value']);
          $newPropertyTag.attr('class', PENDING_CLASS);
          $textList.append($newPropertyTag);
        }
      }
    })
  }

  /* append the new relation to html (themes, groups, related relations) */
  function addElement(fieldId, parentId, parentText, url, fieldName, conceptUrl, link_tag){
    if (link_tag == true) // make field link if necessary
        parentText = "<a href='" + conceptUrl + "'> " + parentText + "</a></li>";
    var $newParent = $('<li class="' + PENDING_CLASS + '"value="' + parentId + '">'
                    + parentText + '</li>');
    var $DeleteButton = createDeleteButton(url, fieldName);
    $($newParent).append($DeleteButton);
    $(fieldId).append($newParent);
  }

  /* themes group narrow broader related save new property */
  function saveConceptRelation(){
    // define a selector for all options of the targeted select
    var selector = $(this).data('input-id') + " div";
    var fieldId = $(this).data('field-id');
    var parentId = $(selector).attr('value');
    var parentText = $(selector).text();
    var addUrl = $(selector).data('href_add');
    var deleteUrl = $(selector).data('href');
    var fieldName = $(this).data('type');
    var url = $(this).data('href');
    var link_tag = $(this).data('link');
    var conceptUrl = $(selector).data('href_concept');

    $.ajax({
       type: "POST",
       url: addUrl,
       data: {
              'csrfmiddlewaretoken': Cookies.get('csrftoken'),
             },
       error: function(e) {
         errorMessage(e.responseJSON.message)
       },
       success: function(data){
         addElement(fieldId, parentId, parentText, deleteUrl, fieldName,
                    conceptUrl, link_tag);
       }
    });
  }

  /* alternatives save new property */
  function saveAlternativeProperty(){
    var fieldName = $(this).data('type');
    var $inputElement = $($(this).data('input-id')) // get input element
    var $textList = $($(this).data('parent-id')); // parent element
    var url = $(this).data('href')
    $.ajax({
       type: "POST",
       url: url,
       data: {
              'value': $inputElement.val(),
              'csrfmiddlewaretoken': Cookies.get('csrftoken'),
             },
       error: function(e) {
         errorMessage(e.responseJSON.message)
         $inputElement.val('');
       },
       success: function(data){
        $alternativeWrapper = $("<div class='alternative-item'></div>");
        $alternative = $("<i data-value='" + data['value'] +
         "' class='status-" + data['status'] + "'>" + data['value'] + ";</i>");
        $deleteButton = createDeleteButton(data['url'], fieldName)
        $alternative.append($deleteButton);
        $alternativeWrapper.append($alternative);
        $textList.append($alternativeWrapper);
        $inputElement.val('');
    }
  });
 };

  /* other relations save foreign relation */
  function saveOtherRelation(){
    var selectId = $(this).data('select-id');
    var selector = selectId + " option:selected";
    var propertyTypeId = $(selector).val();
    var propertyTypeName = $(selector).text();
    var propertyLabel = $($(this).data('value-input-id')).val();
    var parentUrl = $($(this).data('url-input-id')).val();
    var addUrl = $(this).data('href');
    var $fieldList  = $($(this).data('field-id')).find("[data-value='" +
    propertyTypeName + "']").find('.foreign-elements').first();
    var fieldId = $(this).data('field-id');
    $.ajax({
       type: "POST",
       url: addUrl,
       data: {
              'csrfmiddlewaretoken': Cookies.get('csrftoken'),
              'rel_type': propertyTypeId,
              'uri': parentUrl,
              'label': propertyLabel,
              'property_type': propertyTypeId,
             },
       error: function(e) {
         errorMessage(e.responseJSON.message)
       },
       success: function(data) {
         var $relationField = $("<div class='" + PENDING_CLASS + " other-item' id='other" +
         data['id'] + "'><a href=" + parentUrl + ">" + propertyLabel + "</a></div>")
         var $deleteButton = createDeleteButton(data['delete_url'], 'other');
         $relationField.append($deleteButton);
         if ($fieldList.length) {
           $fieldList.append($relationField);
         }
         else {
           var $newTypeContainer = $("<div class='foreign-relation' data-value='" +
           propertyTypeName + "'></div>");
           var $newType = $("<li><span>" + propertyTypeName + "</span></li>");
           var $newList = $("<div class='foreign-elements'></div>");
           $newTypeContainer.append($newType);
           $newType.append($newList);
           $newList.append($relationField);
           $(fieldId).append($newTypeContainer);
         }
       }
    })
  }

  /* remove concept, alternative or other relation */
  function deleteRelation(){
    var strconfirm = confirm("Are you sure you want to delete this object?");
    if (strconfirm == false) {
        return;
    }
    var url = $(this).data('href');
    var relationType = $(this).data('type');
    var deleteFieldId = $(this).parent(); // the field to delete is the parent of the button
    var deleteButton = $(this);
    $.ajax({
       type: "POST",
       url: url,
       data: {
              'csrfmiddlewaretoken': Cookies.get('csrftoken'),
              'value': $(deleteFieldId).data('value'),
             },
       error: function(e) {
         errorMessage(e.responseJSON.message)
       },
       success: function(data){

         if ($(deleteFieldId).hasClass(PENDING_CLASS)){ // if pending hard delete
            $(deleteFieldId).remove();
         }
         // else it is just marked as deleted pending
         $(deleteFieldId).attr('class', DELETED_PENDING_CLASS); // Change status
         $(deleteButton).remove();
         var $restoreButton = createRestoreButton(data['restore_url'], relationType);
         deleteFieldId.append($restoreButton);
       }
    });
  };

  /* restore concept, alternative or other relation */
  function restoreRelation(){
    var strconfirm = confirm("Are you sure you want to restore this object?");
    if (strconfirm == false) {
        return;
    }
    var restoreButton = $(this);
    var url = $(this).data('href');
    var relationType = $(this).data('type');
    var relationDiv = $(this).parent(); // the field to restore is the parent of the button
    $.ajax({
       type: "POST",
       url: url,
       data: {
              'csrfmiddlewaretoken': Cookies.get('csrftoken'),
              'value': $(relationDiv).data('value'),
             },
       error: function(e) {
         errorMessage(e.responseJSON.message)
       },
       success: function(data){
         $(relationDiv).attr('class', PUBLISHED_CLASS); // Change status
         $(restoreButton).remove();
         var $deleteButton = createDeleteButton(data['delete_url'], relationType);
         relationDiv.append($deleteButton);
       }
    });
  };
