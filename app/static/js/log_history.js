function showdata()
{
    $("#completedview").css('display': 'grid');
    $("#emptyview").css('display': 'none');
    $("#loadingview").css('display': 'none');
    alert("abc");
}

function requestData(event)
{
    event.preventDefault();
    alert("abc");
    data1 = $.ajax ({
        method='POST',
        url= {{ url_for('log_history')|tojson }},
        data: $(this).serialize()
    }).done(showdata);
}

$("#dateform").on('submit', requestData);
