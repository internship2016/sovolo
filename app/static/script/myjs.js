$('.dropdown-toggle').dropdown();

var DateFormat = 'YYYY-MM-DD';
$(function () {
    $('#searchform-date').datetimepicker({
        inline: true,
        locale: moment.locale('ja'),
        format: DateFormat
    });
});

