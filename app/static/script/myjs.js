$('.dropdown-toggle').dropdown();

moment.locale('ja', { week: { dow: 1 } });

var DateFormat = 'YYYY-MM-DD';
$(function () {
    $('#searchform-date').datetimepicker({
        inline: true,
        locale: moment.locale('ja'),
        format: DateFormat
    });

    $('#order-results').change(function() {
        var Url = window.location.href;
        console.log(this.value)
        switch(this.value){
            case "開始日(昇順）":
                var desc = "off";
                break;
            case "開始日(降順)":
                var desc = "on";
                break;
            default:
                var desc = "";
                break;
        }
        var regex = /\b(desc=)[^&]*/;
        console.log(Url.match(regex));
        if(regex.test(Url)){
            var newUrl = Url.replace(regex, '$1' + desc);
        } else{
            var newUrl = Url + "&desc=" + desc;
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

