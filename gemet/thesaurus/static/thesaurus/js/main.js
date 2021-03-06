$(document).ready(function() {
    // change language
    // bind change event to select

    if (window.location.href.indexOf("search") > -1) {
        $('.search-button').css('display', 'inline-block');
        console.log('sfasfsa');
    }


    $('#js-change-language').on('change', function() {
        var url = $(this).find(':selected').attr('href'); // get selected value
        if (url) { // require a URL
            if ($('#id_query').val())  {
                if (url.indexOf('?') > -1)
                    url = url + "&query=" + $('#id_query').val();
                else
                    url = url + "?query=" + $('#id_query').val();

            }
            window.location = url; // redirect
        }
        return false;
    });

    $('.source.input-area').on('click', function() {
        var $textArea = $(this).siblings('.source.text-area').first();
        var $button = $(this)
        if ($button.text() === "Show source" &&
            !($textArea.hasClass('contains-sources'))) {
            var url = $(this).data('href');
            $.ajax({
                type: "GET",
                url: url,
                success: function(data) {
                    $textArea.html(data);
                }
            })
        }
        $textArea.toggle();
        $textArea.addClass('contains-sources');
        $button.text($button.text() === "Show source" ? "Hide source" : "Show source");
    });

    $('.history-details.input-area').on('click', function() {
        var $textArea = $(this).siblings('.history-details.text-area').first();
        var $button = $(this)
        if ($button.text() === "See details" &&
            !($textArea.hasClass('contains-details'))) {
            var url = $(this).data('href');
            $.ajax({
                type: "GET",
                url: url,
                success: function(data) {
                    $textArea.html(data);
                     $textArea.css('display','block');
                }
            })
        }
        $textArea.toggle();
        $textArea.addClass('contains-details');
        $button.text($button.text() === "See details" ? "Hide details" : "See details");
    });
    $('.relations ul').filter(function() {
        return $(this).text().trim().length == 0 }).remove();

    if (window.matchMedia("(max-width: 800px)").matches) {
        $('.expand-button').on('click', function() {
            $(this).parent().toggleClass('expand');
            $('body').toggleClass('sidebar-open');
        });

        $('.backdrop-site').on('click', function() {
            $('.gemet-menu').removeClass('expand');
            $('.side-bar').removeClass('expand');
            $('body').removeClass('sidebar-open');
        })

    }

    $('.toggle-list').on('click',function(){
        if($(this).hasClass('concept')) {
            $('.modified-list.concept').toggleClass('expand');
        }

    })



    if (window.matchMedia("(min-width: 800px)").matches) {
        $last_menu_item = $('.search-button');
        if ($last_menu_item.hasClass('active')) {
            $('.search_bar').css('border-top-right-radius', '0');

        }
    }
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
            tree.find('li').has("ul").each(function() {
                var branch = $(this); //li with children ul

                branch.prepend("<i class='tree-indicator glyphicon glyphicon-chevron-right'></i>");
                branch.addClass('tree-branch');
                branch.on('click', function(e) {
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
$(window).on('load', function() {
    $('.treeview').each(function() {
        var tree = $(this);
        tree.treeview();
    })
})
