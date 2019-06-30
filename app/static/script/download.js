$(document).ready(function () {
    $('#download').click(function (e) { 
        e.preventDefault();
        startDownload()
    });   
function startDownload(){
    div = $('<div class="progress"><div></div><div>0%</div><div>...</div><div>&nbsp;</div></div><hr>');
        $('#progress').append(div);

        var nanobar = new Nanobar({
            bg: '#44f',
            target: div[0].childNodes[0]
        });

        $.ajax({
            type: "get",
            url: "/downloadallpost",
            success: function(data, status, request) {
                status_url = request.getResponseHeader('Location');
                update_progress(status_url, nanobar, div[0]);
            },
            error: function() {
                alert('Unexpected error');
            }
        });
}

function update_progress(status_url, nanobar, status_div) {
    // send GET request to status URL
    $.ajax({
        type: "GET",
        url: status_url,
        success: function (data) {
        percent = parseInt(data['current'] * 100 / data['total']);
        nanobar.go(percent);
        $(status_div.childNodes[1]).text(percent + '%');
        $(status_div.childNodes[2]).text(data['status']);
    if(data['state']!=undefined)
    {
        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if ('result' in data) {
                // show result
                $(status_div.childNodes[3]).text('Result: ' + data['result']);
                console.log("complete")
                anchor = $('<a style="display:none" href="http://localhost:5000/downloadpostsfile"><a>')
                $('#progress').append(anchor);
                $('#progress a')[0].click()
            }
            else {
                // something unexpected happened
                $(status_div.childNodes[3]).text('Result: ' + data['state']);
            }
        }
        else {
            // rerun in 2 seconds
            setTimeout(function() {
                update_progress(status_url, nanobar, status_div);
            }, 2000);
        }
    }
    else{
        
    }

        }

    });

    // $.getJson(status_url, function(data) {
    //     // update UI
    //     percent = parseInt(data['current'] * 100 / data['total']);
    //     nanobar.go(percent);
    //     $(status_div.childNodes[1]).text(percent + '%');
    //     $(status_div.childNodes[2]).text(data['status']);
    // if(data['state']!=undefined)
    // {
    //     if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
    //         if ('result' in data) {
    //             // show result
    //             $(status_div.childNodes[3]).text('Result: ' + data['result']);
    //         }
    //         else {
    //             // something unexpected happened
    //             $(status_div.childNodes[3]).text('Result: ' + data['state']);
    //         }
    //     }
    //     else {
    //         // rerun in 2 seconds
    //         setTimeout(function() {
    //             update_progress(status_url, nanobar, status_div);
    //         }, 2000);
    //     }
    // }
    // else{
    //     console.log("complete")

    // }

    // });
}
 
});