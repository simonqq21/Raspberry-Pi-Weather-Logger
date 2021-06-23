submitDate = function submitDate(e) {
	e.preventDefault();
	//~ get date and empty all fields
	date = $('#date').val();
	$("#reportfile iframe").attr("src", "");
	$("#imageplot img").attr("src", "");
	$("#exported").attr('href', "");
	$("#aggexported").attr('href', "");
	
	//~ check if date is not null
	if (date != "") {
		//~ disable submit button and display info message
		$("#datesubmit").attr('disabled', true);
		$("#info").text("please wait, exporting data.");
		//~ convert str to date to send to backend
		date = new Date(date);
		data = {date: date.toISOString()};
		//~ ajax call to get URLs and download links from backend
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
				//~ reenable submit button and clear info text
				$("#info").text("");
				$("#datesubmit").attr('disabled', false);
			}
		});
	}
}

$(document).ready(function() {
	//~ empty all fields when document loaded
	$('#date').val("");
	$("#reportfile iframe").attr("src", "");
	$("#imageplot img").attr("src", "");
	$("#exported").attr('href', "");
	$("#aggexported").attr('href', "");
	
	$('#datesubmit').click(submitDate);
});
