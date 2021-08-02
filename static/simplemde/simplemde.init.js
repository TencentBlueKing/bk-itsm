var simplemdeJQuery = null;

if (typeof jQuery !== 'undefined') {
  simplemdeJQuery = jQuery;
} else if (typeof django !== 'undefined') {
  //use jQuery come with django admin
  simplemdeJQuery = django.jQuery
} else {
  console.error('cant find jQuery, please make sure your have jQuery imported before this script');
}

if (!!simplemdeJQuery) {
  simplemdeJQuery(function() {
    simplemdeJQuery.each(simplemdeJQuery('.simplemde-box'), function(i, elem) {
      var options = JSON.parse(simplemdeJQuery(elem).attr('data-simplemde-options'));
      options['element'] = elem;
      var simplemde = new SimpleMDE(options);
      elem.SimpleMDE = simplemde;
    });
  });
}