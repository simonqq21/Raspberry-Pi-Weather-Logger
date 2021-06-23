submitDate = function submitDate(e) {
	e.preventDefault();
	$("#reportfile iframe").attr("src", "");
	$("#imageplot img").attr("src", "");
	$("#exported").attr('href', "");
	$("#aggexported").attr('href', "");
			
	datestartstr = $('#datestart').val();
	dateendstr = $('#dateend').val();
	datestart = new Date(datestartstr);
	dateend = new Date(dateendstr);
	data = {datestart: datestart.toISOString(), dateend: dateend.toISOString()};
	console.log(data);
	$.ajax({
		method: 'GET',
		url: '/getURLsWithDateRange',
		data: data,
		success: function (result, status, xhr) {
			$('#datestart').val(result.datestart);
			$('#dateend').val(result.dateend);
			$("#reportfile iframe").attr("src", result.report_url);
			$("#imageplot img").attr("src", result.plot_url);
			$("#exported").attr('href', result.exported_data_url);
			$("#aggexported").attr('href', result.agg_exported_data_url);
			console.log(result);
		}
	});
}

$(document).ready(function() {
	$('#datestart').val("");
	$('#dateend').val("");
	$("#reportfile iframe").attr("src", "");
	$("#imageplot img").attr("src", "");
	$("#exported").attr('href', "");
	$("#aggexported").attr('href', "");
	
	$('#datessubmit').click(submitDate);
});
