// https://stackoverflow.com/questions/6941533/get-protocol-domain-and-port-from-url
function get_host(){
    var url = window.location.href
    var arr = url.split("/");
    var result = arr[0] + "//" + arr[2]
    return result
}

function getAllPosts(url) {
    // Default options are marked with *
        console.log(csrf_token)
      return fetch(url, {
          method: "GET", // *GET, POST, PUT, DELETE, etc.
          mode: "cors", // no-cors, cors, *same-origin
          cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
          credentials: "same-origin", // include, *same-origin, omit
          headers: {
              "Content-Type": "application/json",
              "x-csrf-token": csrf_token
              // "Content-Type": "application/x-www-form-urlencoded",
          },
          redirect: "follow", // manual, *follow, error
          referrer: "no-referrer", // no-referrer, *client
        //   body: JSON.stringify(data), // body data type must match "Content-Type" header
      })
      .then(response => response.json()); // parses response to JSON
  }

function deletePost(id){
    console.log(csrf_token)
    let url = "/myBlog/posts/"+id;
    return fetch(url, {
            method: "DELETE", // *GET, POST, PUT, DELETE, etc.
            headers: {
                "x-csrf-token": csrf_token
            },
    })
    .then(response => response.json()); // parses response to JSON
}
