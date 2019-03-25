function post(){
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
    let url =  get_host()+"myBlog/posts/";
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
