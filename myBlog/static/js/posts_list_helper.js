// https://stackoverflow.com/questions/6941533/get-protocol-domain-and-port-from-url


function getAllPosts(url) 
{
    $('.loadingIcon').show();
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
    .then($('.loadingIcon').hide())
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

function commentPost(id, post_host, user_id,displayName,user_github)
{
    var host = get_host();
    let commentForm =
    {
        "query": "addComment",
        "post":post_host+"posts/"+id,
        "comment":
        {
            "author":{
                "id":user_id,
                "host":host,
                "displayName":displayName,
                "url":host+'author/'+user_id,
                "github":user_github

            },
            "comment":"",
            "contentType":"text/plain"
        }
    };
    commentForm.comment.comment= document.getElementById("commentInput"+id).value;
    let body = JSON.stringify(commentForm);
    let commenturl =  "/posts/"+id+"/comments/";
    return fetch(commenturl, {
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
