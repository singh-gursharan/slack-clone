var lastTimestamp = $("#message_list table").last().attr('timestamp');
var channel_id = $('#look-post').attr('channel-id');
(function main() {
    $("#submit").click(function (e) {
        e.preventDefault()
        var post = $('#post').val();
        console.log(post)
        let form = $('.form')
        console.log(form.serialize())
        if ("true") {
            $.ajax({
                type: "POST",
                url: "",
                data: form.serialize(),
                dataType: "json",
            }).done(function (data) {
                console.log(data)
                username = data['username']
                img_url = data['img_url']
                timestamp = data['timestamp']
                utctimestr = data['utctimestr']
                addpost(post, img_url, timestamp, username,utctimestr)
            }).fail(function (jqXHR, status, error) {
                console.log(jqXHR)
                alert(status)
                console.log()
                console.log("hello")
            })
        }
    });
    messageList = $('#message_list')
    if (messageList) {
        ajaxPool()
    }
})();

function addpost(post, img_url, timestamp, username, utctimestr) {
    postnode = createPostNode(post, img_url, timestamp, username, utctimestr)
    document.getElementById('message_list').appendChild(postnode)
    lastTimestamp = $("#message_list table").last().attr('timestamp');
}

function createPostNode(post, img_url, timestamp, username, utctimestr) {
    table = document.createElement("table")
    table.classList.add('table')
    table.classList.add('table_hover')
    table.setAttribute('id', 'posts')
    table.setAttribute('timestamp', `${utctimestr}`)
    let moment_timestamp = moment(timestamp).fromNow()
    //let moment_timestamp = moment(timestamp).fromNow()
    console.log(moment_timestamp)
    table.innerHTML = `<tr><col width="80"><td>
    <img src="${img_url}">
    </td><td>${username}
     said ${moment_timestamp}:
     <br>${post}</td></tr>`
    return table
}

function ajaxPool() {
    function ajaxCall() {
        $.ajax({
            type: "GET",
            url: "/sendposts.json",
            data: {
                'timestamp': lastTimestamp,
                'channel_id': channel_id
            },
            dataType: "json",
        }).done(function (data) {
            console.log(data)
            if (data['is_available']) {
                latest_posts = data
                addLatestPosts(latest_posts['post_list'])
            }
            ajaxPool()
        }).fail(function (jqXHR, status, error) {
            console.log(jqXHR)
            console.log()
            console.log("hello")
        })
    }
    setTimeout(ajaxCall, 3000)
}

function addLatestPosts(latest_posts) {
    console.log("lstest_post")
    console.log(latest_posts)
    for (var post in latest_posts) {
        console.log(latest_posts[post])
        console.log("post body")
        console.log(latest_posts[post].body)
        console.log(latest_posts[post].timestamp)
        console.log(latest_posts[post].utctimestr)
        addpost(latest_posts[post].body, latest_posts[post].img_url, latest_posts[post].timestamp, latest_posts[post].username,latest_posts[post].utctimestr)
    }
}