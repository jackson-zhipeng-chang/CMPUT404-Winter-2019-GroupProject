//https://stackoverflow.com/questions/22087076/how-to-make-a-simple-image-upload-using-javascript-html
var encoded_img="";
function previewFile()
{
    var preview = document.querySelector('img'); 
    var file= document.querySelector('input[type=file]').files[0]; 
    var reader  = new FileReader();
    reader.onloadend = function () 
    {
        preview.src = reader.result;
        encoded_img = preview.src;
    }
    if (file) 
    {
        reader.readAsDataURL(file); //reads the data as a URL
    } 
    else 
    {
        preview.src = "";
    }
}

// https://www.w3schools.com/jsref/prop_style_visibility.asp
function enableInput()
{
    var selectedType = document.getElementById("post-contenttype").value;
    if (selectedType=="image/png;base64" || selectedType=="image/jpeg;base64")
    {
        alert("Since you selected img, you will not be able to add content");
        document.getElementById("post-content").readOnly  = true;
        document.getElementById("post-image").style.visibility = "visible";
    }
    else
    {
        document.getElementById("post-content").readOnly  = false;
        document.getElementById("post-image").style.visibility = "hidden";

    }
}

// https://stackoverflow.com/questions/6941533/get-protocol-domain-and-port-from-url
function get_host()
{
    var url = window.location.href;
    var arr = url.split("/");
    var result = arr[0] + "//" + arr[2];
    return result
}

function post() 
{
    let form = 
    {
        title: "",
        content: "",
        contentType:"",
        categories: "",
        visibility: "",
        description:"",
        visibleTo:"",
        unlisted:""
    }

    form.title = document.getElementById("post-title").value;
    form.contentType = document.getElementById("post-contenttype").value;
    form.categories = document.getElementById("post-categories").value;
    form.content = document.getElementById("post-content").value;
    form.visibility = document.getElementById("post-visibility").value;
    form.unlisted = document.getElementById("post-content").value;
    form.visibleTo = document.getElementById("post-visibleto").value;
    form.description = document.getElementById("post-description").value;
    if (form.contentType == "image/png;base64" || form.contentType =="image/jepg;base64") 
    {
        form.content = encoded_img;
    }

// Reference: https://stackoverflow.com/questions/9618504/how-to-get-the-selected-radio-button-s-value
    var radios = document.getElementsByName('unlisted');
    for (var i = 0, length = radios.length; i < length; i++)
    {
        if (radios[i].checked)
        {
            if (radios[i].value == "Yes")
            {
                form.unlisted = true;
            }
            else
            {
                form.unlisted = false;
            }
            break;
        }
    }
    var xhr = new XMLHttpRequest();
    xhr.open("POST",  get_host()+"/myBlog/posts/", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("X-CSRFToken", csrf_token);
    xhr.send(JSON.stringify(form));
    window.location.replace(get_host()+"/myBlog/all/");
  }
