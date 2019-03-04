var form = {
    title: "",
    content: "",
    contentType:"",
    categories: "",
    visibility: "",
    description:"",
    unlisted:""

}
function post() {
    form.title = document.getElementById("post-title").value;
    form.contentType = document.getElementById("post-contenttype").value;
    form.categories = document.getElementById("post-categories").value;
    form.content = document.getElementById("post-content").value;
    form.visibility = document.getElementById("post-visibility").value;
    form.description = document.getElementById("post-description").value;
    form.unlisted = document.getElementById("post-content").value;
    // Reference: https://stackoverflow.com/questions/9618504/how-to-get-the-selected-radio-button-s-value
    var radios = document.getElementsByName('unlisted');
    for (var i = 0, length = radios.length; i < length; i++){
        if (radios[i].checked){
            if (radios[i].value == "Yes"){
                form.unlisted = true;
            }
            else{
                form.unlisted = false;
            }
            break;
        }
    }
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
    document.getElementById("post-title").value = "";
    document.getElementById("post-content").value = "";
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