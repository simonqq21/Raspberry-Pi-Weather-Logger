//~ conversion

//~ C to F: F = C * 9/5 + 32
//~ C to K: K = C + 273.15 

//~ Pa to Psi: Psi = Pa / 6,894.75729
//~ Pa to mmHg: mmHg = Pa / 133.3223684

function CToF(CVal) {
	return (parseFloat(CVal)*9/5+32);
}

function CToK(CVal) {
	return (parseFloat(CVal)+273.15);
}

function PaToPsi(PaVal) {
	return (parseFloat(PaVal)/6894.7572931783);
}

function PaTommHg(PaVal) {
	return (parseFloat(PaVal)/133.322);
}

function switchUnits() {
	$(".tempunit").text(tempunits);
	$(".presunit").text(presunits);
	
	switch (tempunits) {
		case '°C': 
			$("#dhttemp_val .data").text($("#dhttemp_val .datadefault").text());
			$("#bmptemp_val .data").text($("#bmptemp_val .datadefault").text());
			console.log('C'); 
			break;
		case '°F': 
			$("#dhttemp_val .data").text(CToF($("#dhttemp_val .datadefault").text()));
			$("#bmptemp_val .data").text(CToF($("#bmptemp_val .datadefault").text()));
			console.log('F'); break;
		case '°K': 
			$("#dhttemp_val .data").text(CToK($("#dhttemp_val .datadefault").text()));
			$("#bmptemp_val .data").text(CToK($("#bmptemp_val .datadefault").text()));
			console.log('K'); break;
	}
	
	switch (presunits) {
		case 'Pa': 
			$("#bmppres_val .data").text($("#bmppres_val .datadefault").text());
			console.log('Pa'); break;
		case 'Psi': 
			$("#bmppres_val .data").text(PaToPsi($("#bmppres_val .datadefault").text()));
			console.log('Psi'); break;
		case 'mmHg': 
			$("#bmppres_val .data").text(PaTommHg($("#bmppres_val .datadefault").text()));
			console.log('mmHg'); break;
	}
}
function updateValues() {
	console.log("update!");
	$.get({
		url: "/getLatestData", 
		success: function(result, status, xhr) {
			date_ = new Date(result.datetime);
			dateStr = date_.getFullYear() + '/' + (date_.getMonth() + 1) + '/' + (date_.getDate())
			+ ' ' + date_.getHours() + ':' + date_.getMinutes();
			console.log(dateStr);
			data = {}
	
			data["dhttemp_val"] = result.dhttemp;
			data["dhthumd_val"] = result.dhthumd;
			data["bmptemp_val"] = result.bmptemp;
			data["bmppres_val"] = result.bmppres;		
			$("#datetime").text(dateStr);
			for (var d in data) {
				$("#" + d + " .datadefault").text(data[d]);
			}
			switchUnits();
		}
	});
}

$(document).ready(function() {
	updateValues();
	tempunits = $("input[name='tempunits']:checked").val();
	presunits = $("input[name='presunits']:checked").val();
	
	
	setInterval(function() {updateValues();}, (1000 * 60 * 2.5));
	
	$("#units").change(function() {
		tempunits = $("input[name='tempunits']:checked").val();
		presunits = $("input[name='presunits']:checked").val();
		switchUnits();
	});
});


