(function (global) {
  var $ = global.$;
  if (!$) { return true; }

  $.fn.extend({
    size: function () {
      return $(this).length;
    }
  })
})(this);
