function getFR_List(url){
    return fetch(url,{
        method:"GET",
        mode:"cors",
        cache:"no-cache",
        credentials:"same-origin",
        headers:{
            "Content-Type":"application/json"
        },
        redirect:"follow",
        referrer:"no-referrer",
    }).then(response => response.json());
}

function sendFRrequest(fr_id,status){
    let change_status_form = {
        'id':fr_id,
        'status':status
    }
    let body = JSON.stringify(change_status_form);

    let url = "/myBlog/friendrequest/";
    return fetch(url,{
        method:"PUT",
        mode:"cors",
        cache:"no-cache",
        credentials: "same-origin",
        body:body,
        headers:{
            "Content-Type":"application/json",
            "x-csrftoken":csrf_token
        },
        redirect: "follow",
        referrer: "no-referrer",
    }).then(data=>console.log(data))
        .then(document.location.reload(true));
}

function content_page(data){
    var content = document.getElementById('content');
    content.ineerHTML='';
    for(let i = 0; i < data.length;i++ ){
        var frs = document.createElement('div');
        frs.classList.add("w3-container","w3-card","w3-white","w3-round","w3-margin");
        content.appendChild(frs);

        var title = document.createElement("h3");
        var request_id = data[i].id;

        var friend_name = data[i]['author']['displayName'];

        title.innerHTML = "Friend Request from " + friend_name;
        title.classList.add("w3-row-padding");
        title.style.marginTop = "20px";
        frs.appendChild(title);
        var acceptDiv = document.createElement("div");
        acceptDiv.classList.add("w3-row-padding");
        acceptDiv.style.marginBottom = "20px";
        frs.appendChild(acceptDiv);

        var acceptBtn = document.createElement("BUTTON");
        var acceptText = document.createTextNode("Accept");
        acceptBtn.addEventListener('click',function(){
            sendFRrequest(request_id,'Accept');
        });
        acceptBtn.appendChild(acceptText);
        acceptDiv.appendChild(acceptBtn);

        var declineBtn = document.createElement('BUTTON');
        var declineText = document.createTextNode('Decline');
        declineBtn.addEventListener('click',function(){
            sendFRrequest(request_id,'Decline');
        });
        declineBtn.appendChild(declineText);
        acceptDiv.appendChild(declineBtn);
    }
}
