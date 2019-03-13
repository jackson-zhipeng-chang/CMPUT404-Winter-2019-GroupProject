function get_host()
{
    var url = window.location.href;
    var arr = url.split("/");
    var result = arr[0] + "//" + arr[2];
    return result
}

function getAllFriends(url) 
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
      .then(response => response.json()); // parses response to JSON
}

function deleteFriends(id)   //not yet done
{
    let url = "/myBlog/posts/"+id;
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
    .then(document.location.reload(true)) //https://stackoverflow.com/questions/3715047/how-to-reload-a-page-using-javascript
    .then(alert("Successfully deleted!"));
}
