// ajax request function
function requestData(ev)
{
    // remove default page reloading behavior from the submit button
    ev.preventDefault();
    // set the view to loading view
    setview("loading");
    setGenerateView = setTimeout(function () {setview("generating");}, 1000);

    // AJAX request
    $.ajax ({
        method:'POST',
        url: '/history',
        data: $(this).serialize(),
        success: function(result, status, xhr) {
            clearTimeout(setGenerateView);
            showdata(result);
            // setTimeout(function() {showdata(result);}, 500);
        }
    });
}

// fill up the values of the statistical tables
function get_statistics(data)
{
    for (x of weathervalues) {
        for (sd of statistical_data) {
            $('#'+x+sd).text(data[x][sd]);
    }}
}

// set the url of the plot image in HTML
function setplotimage(plot_url)
{
    $("#weathergraph > img").attr("src", "/static/files/plots/" + plot_url);
}

// fill up the values of the extreme value time fields
function get_times(data)
{
    for (x of weathervalues) {
        for (m of ['min_times', 'max_times']) {
            // console.log(data[x][m].toString().replace(/,/g, "\n"));
            $("#"+m+x+"time").text(data[x][m].toString().replace(/,/g, "\n"));
        }}
}

// create blank time fields that will contain the times when extreme values occured for
// each weather data column
function createtimesfields() {
    // get parent to attach the time fields to
    parent = document.getElementById("timesdiv");
    // create a flex container for each weather column value
    for (x of weathervalues) {
        columntime = document.createElement("div");
        // container for all times per weather data column
        columntime.classList.add("columntimes-flex-container");
        // create a time cell for the minimum and maximum value
        for (m of ['min_times', 'max_times']) {
            // container for label and time
            timecell = document.createElement("div");
            // label
            pheader = document.createElement("p");
            pheader.appendChild(document.createTextNode(m + " " + x));
            // time
            pdata = document.createElement("p");
            pdata.classList.add("time");
            pdata.id = m+x+"time";
            pdata.appendChild(document.createTextNode("00:00"));
            timecell.appendChild(pheader);
            timecell.appendChild(pdata);
            columntime.append(timecell);
        }
        // append each weather time container to the parent
        parent.append(columntime);
    }
}

// show the results of the AJAX query
function showdata(result, status, xhr) {
    // get weather data JSON object
    weatherdata = result.data;
    // get weather data graph URL
    plot_url = result.plot_url;

    if (jQuery.isEmptyObject(weatherdata)) {

    }
    // if the weather data is not empty, display completed view with the data
    else {
        get_statistics(weatherdata);
        setplotimage(plot_url);
        get_times(weatherdata);

        setview("complete");
    }
}

// sets the main view to either empty, loading, or complete
function setview(status) {
    $("#completedview").css({display: "none"});
    $("#emptyview").css({display: "none"});
    $("#loadingview").css({display: "none"});
    $("#generatingview").css({display: "none"});
    switch (status) {
        case "complete":
            $("#completedview").css({display: "grid"});
            break;
        case "loading":
            $("#loadingview").css({display: "block"});
            break;
        case "generating":
            $("#generatingview").css({display: "block"});
            break;
        default:
            $("#emptyview").css({display: "block"});
    }
}

// function to create blank statistical tables, which will be filled with information on
// data load
function createblankstattables()
{
    // get the parent element, where the tables will be added to
    parent = document.getElementById("stattables");

    // for each weather data column
    for (x of weathervalues)
    {
        // header
        var header = document.createElement("h3");
        var headertext = document.createTextNode(x);
        header.appendChild(headertext);

        // table and table body
        var table = document.createElement("table");
        table.classList.add("stattable");
        var tbody = document.createElement("tbody");

        // table header
        var newheader = document.createElement("tr");
        for (sd of statistical_data)
        {
            var newdata = document.createElement("th");
            var newdatatext = document.createTextNode(sd);
            newdata.appendChild(newdatatext);
            newheader.appendChild(newdata);
        }

        // table data
        var statdatarow = document.createElement("tr");
        for (sd of statistical_data)
        {
            var newdata = document.createElement("td");
            var newdatatext = document.createTextNode(" ");
            newdata.appendChild(newdatatext)
            newdata.id = x + sd;
            statdatarow.appendChild(newdata);
        }
        // append data to table
        tbody.appendChild(newheader);
        tbody.appendChild(statdatarow);
        table.appendChild(tbody);
        // append new table to parent
        parent.appendChild(header);
        parent.appendChild(table);
    }
}

// run when document ready
$(document).ready(function() {
    // add event handler to data load button
    $("#dateform").on('submit', requestData);

    // download buttons
    $("reportdlbtn").click();
    $("datadlbtn").click();

    // define weather data columns and statistical values
    weathervalues = ['Humidity', 'Temperature', 'BMP_temperature', 'Pressure'];
    statistical_data = ['mean', 'std', 'min', 'max'];

    // create blank tables that will contain weather data statistics for each weather data column
    createblankstattables();
    // create blank time fields that will contain the times when extreme values occured for
    // each weather data column
    createtimesfields();
});
