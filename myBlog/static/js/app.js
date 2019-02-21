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
    xhr.open("POST", "myBlog/posts/", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("X-CSRFToken", csrf_token);
    xhr.send(JSON.stringify(form));
    console.log(form);
    console.log(JSON.stringify(form));

  }
function getAllPosts() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            
            var data = JSON.parse(this.responseText);
            console.log(data);
            // we get the returned data
        }
    };
    xhr.open("GET", "/myBlog/author/posts/", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("x-csrf-token", csrf_token);
    xhr.send();
    
}