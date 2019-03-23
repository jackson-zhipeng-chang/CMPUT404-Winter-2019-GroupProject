// https://stackoverflow.com/questions/6941533/get-protocol-domain-and-port-from-url
function get_host()
{
    console.log('get_host');
    var url = window.location.href;
    var arr = url.split("/");
    var result = arr[0] + "//" + arr[2];
    return result
}

function getAllPosts(url)
{
    return fetch(url, {
        method: "GET",
        mode: "cors",
        cache: "no-cache",
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json"
        },
        redirect: "follow",
        referrer: "no-referrer",
    })
    .then(response => response.json());
}

function deletePost(id)
{
    let url = "/service/posts/"+id;
    return fetch(url, {
        method: "DELETE",
        mode: "cors",
        cache: "no-cache",
        credentials: "same-origin",
        headers: {
            "x-csrftoken": csrf_token
        },
        redirect: "follow",
        referrer: "no-referrer",
    })
    .then(response => {
        if (response.status === 204)
        {
            alert("Successfully deleted!");
            document.location.reload(true); //https://stackoverflow.com/questions/3715047/how-to-reload-a-page-using-javascript
        }
        else
        {
            alert("Something went wrong: " +  response.status);
        }
    });
}

function commentPost(id,user_id,displayName,github_url){
    //TODO : another comment contenttype?
    let host = get_host();
    let commentForm =
    {
        "query": "addComment",
        "post":host+"myBlog/"+user_id,
        "comment": {
            "author":{
                "id":user_id,
                "host":host,
                "displayName":displayName,
                "url":host+user_id,
                "github":github_url
            },
            "comment":"",
            "contentType":"text/plain"
        }
    };
    console.log(commentForm);
    commentForm.comment.comment= document.getElementById("commentInput"+id).value;
    let body = JSON.stringify(commentForm);
    let url = post_host+"service/posts/"+id+"/comments/";
    return fetch(url, {
        method: "POST",
        mode: "cors",
        cache: "no-cache",
        credentials: "same-origin",
        body: body,
        headers: {
            "Content-Type": 'application/json',
            "Accept": 'application/json',
            "x-csrftoken": csrf_token
        },
        redirect: "follow",
        referrer: "no-referrer",
    })
    .then(response => {
        if (response.status === 200)
        {
            document.location.reload(true);
        }
        else
        {
            alert("Something went wrong: " +  response.status);
        }
    });
}
