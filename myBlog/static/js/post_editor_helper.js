//https://stackoverflow.com/questions/22087076/how-to-make-a-simple-image-upload-using-javascript-html
var encoded_img="";
function previewFile()
{
    var file = document.querySelector('input[type=file]').files[0];
    var reader  = new FileReader();
    reader.onloadend = function (){
        encoded_img = reader.result;

        let selectedType = document.getElementById("post-contenttype").value;
        if (! encoded_img.includes(selectedType))
        {
            alert("Please upload the selected type image!");
        } else {
            document.getElementById("post-content").value = encoded_img;
            document.getElementById("file-button").innerText = "Change File"
        }
    };
    if (file){
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
    if (selectedType=="image/png;base64" || selectedType=="image/jpeg;base64"){
        alert("Since you selected img, you will not be able to add content");
        document.getElementById("post-content").readOnly  = true;
        document.getElementById("files").disabled = false;
        document.getElementById("file-button").style.visibility = "visible";
        document.getElementById("file-button").innerText = "Add File";
    }
    else{
        document.getElementById("post-content").readOnly  = false;
        document.getElementById("files").disabled = true;
        document.getElementById("file-button").style.visibility = "hidden";
    }
    document.getElementById("post-content").value = "";
}

function set_friends_list (selectedFriendsIDs=""){

    get_friends_list().then(function(response) {
        if (response.length === 0){
            document.getElementById("friendsoptions").setAttribute("data-placeholder", "Looks like you don't have any friends...");
            $('#friendsoptions').trigger("chosen:updated");
        }
        else{
            if (selectedFriendsIDs.length > 0){
                selectedFriendsIDs = selectedFriendsIDs
                    .replace(",", "")
                    .replace("[", "")
                    .replace("]", "")
                    .replace(/'/g, "")
                    .split(" ");
            }

            document.getElementById("friendsoptions").setAttribute("data-placeholder", "Please typing a name to filter... ");

            for (var i = 0; i < response.length; i++){
                let value =response[i].id;
                let innerText=response[i].displayName;
                let option = null;

                if (selectedFriendsIDs.length === 0){
                    option = '<option value=' + value + '>' + innerText + '</option>';
                } else {
                    for (var j in selectedFriendsIDs) {
                        if (selectedFriendsIDs[j].valueOf() === response[i].id.valueOf()) {
                            option = '<option value=' + value + ' selected>' + innerText + '</option>';
                            break;
                        }
                    }

                    if (option === null){
                        option = '<option value=' + value + '>' + innerText + '</option>';
                    }
                }

                var newOption = $(option);
                $('#friendsoptions').append(newOption);
                $('#friendsoptions').trigger("chosen:updated");
            }
        }
    })
}

function get_friends_list(){
    let url = "/service/myfriends/";
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
// function get_host(){
//     var url = window.location.href;
//     var arr = url.split("/");
//     var result = arr[0] + "//" + arr[2];
//     return result
// }

