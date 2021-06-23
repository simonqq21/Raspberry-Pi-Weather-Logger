submitDate = function submitDate(e) {
	e.preventDefault();
	//~ get date and empty all fields
	datestartstr = $('#datestart').val();
	dateendstr = $('#dateend').val();
	$("#reportfile iframe").attr("src", "");
	$("#imageplot img").attr("src", "");
	$("#exported").attr('href', "");
	$("#aggexported").attr('href', "");
	
	//~ check if dates are not null
	if (datestartstr != "" && dateendstr != "") {
		//~ disable submit button and display info message
		$("#datessubmit").attr('disabled', true);
		$("#info").text("please wait, exporting data and generating plots.");
		//~ convert str to date to send to backend
		datestart = new Date(datestartstr);
		dateend = new Date(dateendstr);
		data = {datestart: datestart.toISOString(), dateend: dateend.toISOString()};
		console.log(data);
		//~ ajax call to get URLs and download links from backend
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
				//~ reenable submit button and clear info text
				$("#info").text("");
				$("#datessubmit").attr('disabled', false);
			}
		});
	}
}

$(document).ready(function() {
	//~ empty all fields when document loaded
	$('#datestart').val("");
	$('#dateend').val("");
	$("#reportfile iframe").attr("src", "");
	$("#imageplot img").attr("src", "");
	$("#exported").attr('href', "");
	$("#aggexported").attr('href', "");
	
	$('#datessubmit').click(submitDate);
});
