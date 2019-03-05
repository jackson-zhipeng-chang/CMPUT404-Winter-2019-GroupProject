var form = {
    title: "",
    content: "",
    contentType:"",
    categories: "",
    visibility: "",
    description:"",
    visibleTo:"",
    unlisted:""

}

var encoded_img="";

//function to make a get request every 30s to get current pending friend request
//https://makitweb.com/how-to-fire-ajax-request-on-regular-interval/
function getFriendReuqest(){
    $.ajax({
        url:"friendrequest/",
        type:"get",
        success:function(data){
            // console.log(data);
            let reqeustNum =  data.length;
            let fRsign = document.querySelector('#FR');
            fRsign.innerHTML = reqeustNum;

        },
        complete:function(data){
            console.log('complete');
            setTimeout(getFriendReuqest,5000);
        },
        error:function(){
            console.log('error');
        }
    });
}

$(document).ready(function(){
    setTimeout(getFriendReuqest,5000)
});

// when mouse hover on the notification icon, show how many requests coming
//https://www.w3schools.com/jquery/tryit.asp?filename=tryjquery_event_hover
$(document).ready(function(){
    $("#FRdropdown").hover(function(){
        let currentRequest = document.querySelector('#FR').innerHTML;
        document.querySelector("#dropdown").innerHTML = currentRequest+ " new friend request!";
    })
});





function previewFile(){
    var preview = document.querySelector('img');
    var file= document.querySelector('input[type=file]').files[0];
    var reader  = new FileReader();
    reader.onloadend = function () {
        preview.src = reader.result;
        encoded_img = preview.src;
    }
    if (file) {
        reader.readAsDataURL(file); //reads the data as a URL
    } else {
        preview.src = "";
    }
}
// https://www.w3schools.com/jsref/prop_style_visibility.asp
function enableInput(){
    var selectedType = document.getElementById("post-contenttype").value;
    console.log(selectedType)
    if (selectedType=="image/png;base64" || selectedType=="image/jpeg;base64"){
        alert("Since you selected img, you will not be able to add content");
        document.getElementById("post-content").readOnly  = true;
        document.getElementById("post-image").style.visibility = "visible";
    }
    else{
        document.getElementById("post-content").readOnly  = false;
        document.getElementById("post-image").style.visibility = "hidden";

    }
}

// https://stackoverflow.com/questions/6941533/get-protocol-domain-and-port-from-url
function get_host(){
    var url = window.location.href
    var arr = url.split("/");
    var result = arr[0] + "//" + arr[2]
    return result
}

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
function post() {
    form.title = document.getElementById("post-title").value;
    form.contentType = document.getElementById("post-contenttype").value;
    form.categories = document.getElementById("post-categories").value;
    form.content = document.getElementById("post-content").value;
    form.visibility = document.getElementById("post-visibility").value;
    form.unlisted = document.getElementById("post-content").value;
    form.visibleTo = document.getElementById("post-visibleto").value;
    form.description = document.getElementById("post-description").value;
    if (form.contentType == "image/png;base64" || form.contentType =="image/jepg;base64") {
        form.content = encoded_img;
    }

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
    console.log("Posting")
    xhr.open("POST",  get_host()+"/myBlog/posts/", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("X-CSRFToken", csrf_token);
    xhr.send(JSON.stringify(form));
    console.log(JSON.stringify(form))
    window.location.replace(get_host()+"/myBlog/all/");
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
