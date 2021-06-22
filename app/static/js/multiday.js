submitDate = function submitDate(e) {
	e.preventDefault();
	alert('submit!');
}

$(document).ready(function() {
	$('#datessubmit').click(submitDate);
});
