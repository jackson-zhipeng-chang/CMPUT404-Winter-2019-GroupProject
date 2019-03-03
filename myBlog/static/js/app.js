var form = {
    post_title: "",
    post_content: "",
    post_type: "text/plain",
    open_to: "me",
    unlisted: false
}

function post() {
    form.post_title = document.getElementById("post-title").value;
    form.post_content = document.getElementById("post-content").value;

    var xhr = new XMLHttpRequest();
    console.log("Posting...")
    xhr.open("POST", "myBlog/posts/", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("X-CSRFToken", csrf_token);
    xhr.send(JSON.stringify(form));
    console.log("Finished Posting!")

    //resetting fields
    document.getElementById("post-title").value = "";
    document.getElementById("post-content").value = "";
  }

function getAllPosts() {
    // Default options are marked with *
      return fetch("/myBlog/author/posts/", {
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