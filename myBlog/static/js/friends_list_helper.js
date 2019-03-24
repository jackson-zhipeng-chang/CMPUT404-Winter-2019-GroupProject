

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
            document.location.reload(true); //https://stackoverflow.com/questions/3715047/how-to-reload-a-page-using-javascript
        } 
        else 
        {
            alert("Something went wrong: " +  response.status);
        }
    });
}
