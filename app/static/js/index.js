//~ conversion functions

//~ C to F: F = C * 9/5 + 32
//~ C to K: K = C + 273.15 

//~ Pa to Psi: Psi = Pa / 6,894.75729
//~ Pa to mmHg: mmHg = Pa / 133.3223684

function CToF(CVal) {
	return roundNum(parseFloat(CVal)*9/5+32);
}

function CToK(CVal) {
	return roundNum(parseFloat(CVal)+273.15);
}

function PaToPsi(PaVal) {
	return roundNum(parseFloat(PaVal)/6894.7572931783);
}

function PaTommHg(PaVal) {
	return roundNum(parseFloat(PaVal)/133.322);
}

//~ round off numbers to 3 decimal places
function roundNum(num) {
	return (Math.round((num) * 1000) / 1000).toFixed(3);
}

//~ function to run either when units changed or data refreshed
function switchUnits() {
	//~ change displayed units
	$(".tempunit").text(tempunits);
	$(".presunit").text(presunits);
	
	//~ temperature units
	switch (tempunits) {
		case '°C': 
			$("#dhttemp_val .data").text(roundNum($("#dhttemp_val .datadefault").text()));
			$("#bmptemp_val .data").text(roundNum($("#bmptemp_val .datadefault").text()));
			break;
		case '°F': 
			$("#dhttemp_val .data").text(CToF($("#dhttemp_val .datadefault").text()));
			$("#bmptemp_val .data").text(CToF($("#bmptemp_val .datadefault").text()));
			break;
		case '°K': 
			$("#dhttemp_val .data").text(CToK($("#dhttemp_val .datadefault").text()));
			$("#bmptemp_val .data").text(CToK($("#bmptemp_val .datadefault").text()));
			break;
	}
	
	//~ pressure units
	switch (presunits) {
		case 'Pa': 
			$("#bmppres_val .data").text(roundNum($("#bmppres_val .datadefault").text()));
			break;
		case 'Psi': 
			$("#bmppres_val .data").text(PaToPsi($("#bmppres_val .datadefault").text()));
			break;
		case 'mmHg': 
			$("#bmppres_val .data").text(PaTommHg($("#bmppres_val .datadefault").text()));
			break;
	}
	//~ update humidity values
	$("#dhthumd_val .data").text(roundNum($("#dhthumd_val .datadefault").text()));
}

//~ ajax function to update values from db
function updateValues() {
	console.log("update!");
	$.get({
		url: "/getLatestData", 
		success: function(result, status, xhr) {
			date_ = new Date(result.datetime);
			dateStr = date_.getFullYear() + '/' + (date_.getMonth() + 1) + '/' + (date_.getDate())
			+ ' ' + date_.getHours() + ':' + date_.getMinutes();
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
	
	//~ refresh data every 2.5s
	setInterval(function() {updateValues();}, (1000 * 60 * 2.5));
	
	//~ check when unit selection changes
	$("#units").change(function() {
		tempunits = $("input[name='tempunits']:checked").val();
		presunits = $("input[name='presunits']:checked").val();
		switchUnits();
	});
});


