submitDate = function submitDate(e) {
	e.preventDefault();
	date = $('#date').val();
	date = new Date(date);
	data = {date: date.toISOString()};
	console.log(data);
	$.ajax({
		method: 'GET',
		url: '/getURLsWithDate',
		data: data,
		success: function (result, status, xhr) {
			
		}
	});
	
}

$(document).ready(function() {
	$('#datesubmit').click(submitDate);
});
