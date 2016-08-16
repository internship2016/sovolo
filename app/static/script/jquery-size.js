/**
 * jquery-size.js - jQuery3 polyfill for bootstrap-datetimepicker.js
 *
 * The `size` function has been removed from jQuery3
 * This scriopt ports the function back from old jQuery lib
 *
 * refs:
 *    - https://github.com/Eonasdan/bootstrap-datetimepicker/pull/1664
 *    - https://github.com/jquery/jquery/blob/055cb7534e2dcf7ee8ad145be83cb2d74b5331c7/test/data/jquery-1.9.1.js#L237-L240
 */

(function (global) {
  var $ = global.jQuery;
  if (!$) {
    return true;
  }

  $.fn.extend({
    size: function () {
      return this.length;
    }
  });
})(this);
