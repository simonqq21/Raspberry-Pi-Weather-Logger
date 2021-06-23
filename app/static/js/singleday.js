submitDate = function submitDate(e) {
	e.preventDefault();
	$("#reportfile iframe").attr("src", "");
	$("#imageplot img").attr("src", "");
	$("#exported").attr('href', "");
	$("#aggexported").attr('href', "");
			
	date = $('#date').val();
	date = new Date(date);
	data = {date: date.toISOString()};
	console.log(data);
	$.ajax({
		method: 'GET',
		url: '/getURLsWithDate',
		data: data,
		success: function (result, status, xhr) {
			$('#date').val(result.date);
			$("#reportfile iframe").attr("src", result.report_url);
			$("#imageplot img").attr("src", result.plot_url);
			$("#exported").attr('href', result.exported_data_url);
			$("#aggexported").attr('href', result.agg_exported_data_url);
			console.log(result);
		}
	});
}

$(document).ready(function() {
	$("#reportfile iframe").attr("src", "");
	$("#imageplot img").attr("src", "");
	$("#exported").attr('href', "");
	$("#aggexported").attr('href', "");
	
	$('#datesubmit').click(submitDate);
});
