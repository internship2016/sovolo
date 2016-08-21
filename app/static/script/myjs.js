(function (window) {
  var $ = window.jQuery;
  var moment = window.moment;

  $('.dropdown-toggle').dropdown();

  moment.locale('ja', {week: {dow: 1}});

  var DateFormat = 'YYYY-MM-DD';
  $(function () {
    $('#searchform-date').datetimepicker({
      inline: true,
      locale: moment.locale('ja'),
      format: DateFormat
    });

    $('#order-results').change(function() {
      var Url = window.location.href;
      switch(this.value){
        case "開始日(昇順）":
          var desc = "asc";
          break;
        case "開始日(降順)":
          var desc = "desc";
          break;
        default:
          var desc = "";
          break;
      }
      var regex = /\b(order_by=start_time-)[^&]*/;
      if(regex.test(Url)){
        var newUrl = Url.replace(regex, '$1' + desc);
      } else{
        var newUrl = Url + "&order_by=start_time-" + desc;
      }
      newUrl = newUrl.replace(/\bpage=\d+/,"page=1");
      window.location.replace(newUrl);
    });

    $('#result-number').change(function() {
      var Url = window.location.href;
      num = this.value
      var regex = /\b(numperpage=)[^&]*/;
      if(regex.test(Url)){
        var newUrl = Url.replace(regex, '$1' + num);
      } else{
        var newUrl = Url + "&numperpage=" + num;
      }
      window.location.replace(newUrl)
    });
  });

})(this);
