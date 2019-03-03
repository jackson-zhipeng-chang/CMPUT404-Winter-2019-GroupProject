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