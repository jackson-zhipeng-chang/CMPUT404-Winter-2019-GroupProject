//https://stackoverflow.com/questions/22087076/how-to-make-a-simple-image-upload-using-javascript-html
var encoded_img="";
function previewFile()
{
    var file = document.querySelector('input[type=file]').files[0]; 
    var reader  = new FileReader();
    reader.onloadend = function () 
    {
        encoded_img = reader.result;
        document.getElementById("post-content").value = encoded_img;
        let selectedType = document.getElementById("post-contenttype").value;
        if (! encoded_img.includes(selectedType))
        {
            alert("Please upload the selected type image!");
        }
    }
    if (file) 
    {
        reader.readAsDataURL(file); //reads the data as a URL
    }
}

function enableVisibleTo()
{
    var selectedVisibility = document.getElementById("post-visibility").value;

    if (selectedVisibility == "PRIVATE"){
        document.getElementById("friendsoptions").disabled = false;
        set_friends_list();
    }
    else{
        document.getElementById("friendsoptions").disabled = true;
        document.getElementById("friendsoptions").setAttribute("data-placeholder", "Only avaliable when PRIVATE TO selected ");
        $('#friendsoptions').empty();
        $('#friendsoptions').trigger("chosen:updated");
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
        document.getElementById("my-file").disabled = false;
    }
    else
    {
        document.getElementById("post-content").readOnly  = false;
        document.getElementById("my-file").disabled = true;
        document.getElementById("post-content").value = "";

    }
}

function set_friends_list (){
    
    get_friends_list().then(function(response) {
        if (response.length ==0){
            document.getElementById("friendsoptions").setAttribute("data-placeholder", "Looks like you don't have any friends...");
            $('#friendsoptions').trigger("chosen:updated");
        }
        else{
            document.getElementById("friendsoptions").setAttribute("data-placeholder", "Please typing a name to filter... ");
            for (var i = 0; i < response.length; i++){
                let value =response[i].id;
                let innerText=response[i].displayName;
                let option = '<option value='+value+'>'+innerText+'</option>';
                var newOption = $(option);
                $('#friendsoptions').append(newOption);
                $('#friendsoptions').trigger("chosen:updated");
            }
        }
    })    
}

function get_friends_list()
{
    let url = "/myBlog/myfriends/";
    return fetch(url, {
        method: "GET", 
        mode: "cors", 
        cache: "no-cache", 
        credentials: "same-origin", 
        redirect: "follow", 
        referrer: "no-referrer", 
    })
    .then(response => {
        if (response.status === 200) 
        { 
            return response.json(); 
        } 
        else 
        {
            alert("Something went wrong: " + response.status);
        }
    }); 
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
    form.visibleTo = String($(".chosen-select").chosen().val());
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
    let body = JSON.stringify(form);
    let url =  get_host()+"myBlog/posts/";
    console.log(body);
    return fetch(url, {
        method: "POST", 
        mode: "cors", 
        cache: "no-cache", 
        credentials: "same-origin", 
        body: body,
        headers: {
            "Content-Type": "application/json",
            "x-csrftoken": csrf_token
        },
        redirect: "follow", 
        referrer: "no-referrer", 
    })
    .then(response => {
        if (response.status === 200) 
        { 
            window.location.replace(get_host()+"myBlog/all/"); 
        } 
        else 
        {
            alert("Something went wrong: " +  response.status);
        }
    }); 

  }
