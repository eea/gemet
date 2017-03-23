$(document).ready(function() {
    // change language
    // bind change event to select

    $('#js-change-language').on('change', function() {
        var url = $(this).find(':selected').attr('href'); // get selected value
        if (url) { // require a URL
            window.location = url; // redirect
        }
        return false;
    });




    // $('.search_bar').on('mouseenter', function() {

    //     if ((window.location.href.indexOf("search") == -1)&&!($('.search-link').hasClass('active'))) {
    //         $(this).css('border-top-right-radius', '0')
    //             setTimeout(function(){ 
    //         $('.active').addClass('remove-active');
    //         $('.search-link').addClass('active');

    //          }, 200);
    //     }


    // });

    // $('.search_bar').on('mouseleave', function() {
    //     if (window.location.href.indexOf("search") == -1) {
    // $(this).css('border-top-right-radius', '6px')
    //       setTimeout(function(){ 
    //         $('.search-link').removeClass('active');
    //         $('.active').removeClass('remove-active');
    //       }, 200);
        

    //     }
    // });


    $('.search-link').on('click',function(){
      $('.search_bar input#id_query').trigger('focus');
      // if (window.location.href.indexOf("search") == -1) {
      //                 $('.search_bar').css('border-top-right-radius', '0')
      //     setTimeout(function(){ 

     
      //              $('.active').addClass('remove-active');
      //       $('.search-link').addClass('active');
      //     }, 200);
      //   }

    })




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



    // if (window.matchMedia("(min-width: 800px)").matches) {
    //     $first_menu_item = $('.gemet-menu a:first-of-type');
    //     $last_menu_item = $('.gemet-menu a:last-of-type');

    //     if ($first_menu_item.hasClass('active')) {
    //         $('.search_bar').css('border-top-left-radius', '0');
    //         console.log('first');
    //     }

    //     if ($last_menu_item.hasClass('active')) {
    //         $('.search_bar').css('border-top-right-radius', '0');
    //         console.log('last');
    //     }
    // }
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
