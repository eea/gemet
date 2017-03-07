
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


$('.relations ul').filter(function(){return $(this).text().trim().length==0}).remove();

$('.expand-button').on('click', function(){
  $('.side-bar').toggleClass('expand')
})

});
/**
 *  BootTree Treeview plugin for Bootstrap.
 *
 *  Based on BootSnipp TreeView Example by Sean Wessell
 *  URL:  http://bootsnipp.com/snippets/featured/bootstrap-30-treeview
 *
 *  Revised code by Leo "LeoV117" Myers
 *
 */
$.fn.extend({
  treeview: function() {
    return this.each(function() {
      // Initialize the top levels;
      var tree = $(this);

      tree.addClass('treeview-tree');
      tree.find('li').each(function() {
        var stick = $(this);
      });
      tree.find('li').has("ul").each(function () {
        var branch = $(this); //li with children ul

        branch.prepend("<i class='tree-indicator glyphicon glyphicon-chevron-right'></i>");
        branch.addClass('tree-branch');
        branch.on('click', function (e) {
          if (this == e.target) {
            var icon = $(this).children('i:first');

            icon.toggleClass("glyphicon-chevron-down glyphicon-chevron-right");
            $(this).children().children().toggle();
          }
        })
        branch.children().children().toggle();

        /**
         *  The following snippet of code enables the treeview to
         *  function when a button, indicator or anchor is clicked.
         *
         *  It also prevents the default function of an anchor and
         *  a button from firing.
         */
        branch.children('.tree-indicator, button, a').click(function(e) {
          branch.click();

          e.preventDefault();
        });
      });
    });
  }
});

/**
 *  The following snippet of code automatically converst
 *  any '.treeview' DOM elements into a treeview component.
 */
$(window).on('load', function () {
  $('.treeview').each(function () {
    var tree = $(this);
    tree.treeview();
  })
})

