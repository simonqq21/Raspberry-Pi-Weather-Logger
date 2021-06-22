// remove the active class from all navbar links
function removeAllActive() {
    for (url of urlIDs)
        $('#' + url).removeClass('active');
}

$(document).ready(function () {
    // list of link ids and urls
    urlIDs = ['index', 'history', 'trends', 'about'];

    removeAllActive();

    // get the URL of the current page
    activeurl = $(location).attr('href');
    // check if key urls exist in the active url
    // if url exists, set the link with the url id to the class active.
    for (url of urlIDs) {
        if (activeurl.search(url) != -1) {
            $("#" + url).addClass("active");
    }}
});
