function setupEditPostPage()
{
    var selectedType = document.getElementById("post-contenttype").value;
    if (selectedType=="image/png;base64" || selectedType=="image/jpeg;base64"){
        alert("Since you selected img, you will not be able to add content");
        document.getElementById("post-content").readOnly  = true;
        document.getElementById("files").disabled = false;
        document.getElementById("file-button").style.visibility = "visible";
        document.getElementById("file-button").innerText = "Change File";
    }
    else{
        document.getElementById("post-content").readOnly  = false;
        document.getElementById("files").disabled = true;
        document.getElementById("file-button").style.visibility = "hidden";
    }
}

function put(id){
    let form =
    {
        id: id,
        title: "",
        content: "",
        contentType:"",
        categories: "",
        visibility: "",
        description:"",
        visibleTo:"",
        unlisted:""
    };
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
    let url =  get_host()+"service/posts/";
    return fetch(url, {
        method: "PUT",
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
            console.log(get_host())
            window.location.replace(get_host()+"service/all/");
        }
        else
        {
            alert("Something went wrong: " +  response.status);
        }
    });

}