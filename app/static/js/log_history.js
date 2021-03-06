// ajax function
function requestData(ev)
{
    ev.preventDefault();
    data1 = $.ajax ({
        method:'POST',
        url: '/history',
        data: $(this).serialize()
    }).done(showdata);
}

// function to fill up the values of the statistical tables
function get_statistics(data)
{
    for (x of weathervalues)
    {
        for (sd of statistical_data)
        {
            $('#'+x+sd).text(data[x][sd]);
        }
    }
}

// function to get the url of the plot image
function setplotimage(plot_url)
{
    console.log("/static/files/plots/" + plot_url);
    $("#weathergraph > img").attr("src", "/static/files/plots/" + plot_url);
}

function get_times(data)
{
    for (x of weathervalues)
    {
        for (m of ['min_times', 'max_times'])
        {
            console.log(data[x][m].toString().replace(/,/g, "\n"));
            $("#"+m+x+"time").text(data[x][m].toString().replace(/,/g, "\n"));
        }
    }
}

function createtimesfields()
{
    // get parent
    parent = document.getElementById("timesdiv");
    for (x of weathervalues)
    {
        columntime = document.createElement("div");
        columntime.classList.add("columntimes-flex-container");
        for (m of ['min_times', 'max_times'])
        {
            timecell = document.createElement("div");
            timecell.classList.add("columntime");
            pgraph = document.createElement("p");
            pgraph.appendChild(document.createTextNode(m + " " + x));
            pdata = document.createElement("p");
            pdata.classList.add("time");
            pdata.id = m+x+"time";
            pdata.appendChild(document.createTextNode("00:00"));
            timecell.appendChild(pgraph);
            timecell.appendChild(pdata);
            columntime.append(timecell);
        }
        parent.append(columntime);
    }

}

function showdata(requesteddata)
{
    weatherdata = requesteddata.data;
    plot_url = requesteddata.plot_url;

    get_statistics(weatherdata);
    setplotimage(plot_url);
    get_times(weatherdata);


    setview("complete");
}

// sets the main view to either empty, loading, or complete
function setview(status)
{
    $("#completedview").css({display: "none"});
    $("#emptyview").css({display: "none"});
    $("#loadingview").css({display: "none"});
    switch (status) {
        case "complete":
            $("#completedview").css({display: "grid"});
            break;
        case "loading":
            $("#loadingview").css({display: "block"});
            break;
        default:
            $("#emptyview").css({display: "block"});
    }
}

function createblankstattables(weathervalues, statistical_data)
{
    // create statistical tables with blank values
    // get the parent element
    parent = document.getElementById("stattables");
    parent.textContent = '';

    for (x of weathervalues)
    {
        // create header
        var header = document.createElement("h3");
        var headertext = document.createTextNode(x);
        header.appendChild(headertext);

        // create table
        var table = document.createElement("table");
        var tbody = document.createElement("tbody");

        // create new row header
        var newheader = document.createElement("tr");
        for (sd of statistical_data)
        {
            var newdata = document.createElement("th");
            var newdatatext = document.createTextNode(sd);
            newdata.appendChild(newdatatext);
            newheader.appendChild(newdata);
        }

        var statdatarow = document.createElement("tr");
        // add metrics
        for (sd of statistical_data)
        {
            var newdata = document.createElement("td");
            var newdatatext = document.createTextNode(" ");
            newdata.appendChild(newdatatext)
            console.log(x + sd);
            newdata.id = x + sd;
            statdatarow.appendChild(newdata);
        }

        tbody.appendChild(newheader);
        tbody.appendChild(statdatarow);
        table.appendChild(tbody);
        // append new table to parent
        parent.appendChild(header);
        parent.appendChild(table);
    }
}

// add event handler to date submit button
$("#dateform").on('submit', requestData);

weathervalues = ['Humidity', 'Temperature', 'BMP_temperature', 'Pressure'];
statistical_data = ['mean', 'std', 'min', 'max'];
createblankstattables(weathervalues, statistical_data);
createtimesfields();

function togglesize() {
    $(this).toggleClass("timesexpanded");
}
$(".time").click(togglesize);
