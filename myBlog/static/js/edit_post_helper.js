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