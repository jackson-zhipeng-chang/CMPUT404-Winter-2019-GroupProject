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
    let url = "/service/friendrequest/";
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
    })
    .then(response => {
        if (response.status === 200)
        {
            window.location.replace(get_host()+"service/myfriendslist/");
        }
        else
        {
            alert("Something went wrong: " +  response.status);
        }
    });
}

function acceptFRrequest(author_id, author_host, author_name, author_url, currentUserName, currentUserID){
    let host = get_host();
    let request_form = {
        "query": "friendrequest",
        "author": {
            'id': currentUserID,
            'host': host,
            'displayName': currentUserName,
            'url': host + current_user_id,
        },
        "friend": {
            'id': author_id,
            'host': author_host,
            'displayName': author_name,
            'url': author_url,
        }
    }
    let body = JSON.stringify(request_form);
    console.log(body);
    let url_local = host + "service/acceptFriendRequest/";
    return fetch(url_local, {
        method: "POST",
        mode: "cors",
        cache: "no-cache",
        credentials: "same-origin",
        body: body,
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-csrftoken": csrf_token,
        },
        redirect: "follow",
        referrer: "no-referrer",
    })
        .then(response => {
            if (response.status === 200) {
                document.location.reload(true);
            } else {
                alert("Something went wrong: " + response.status);
            }
        })
}

function content_page(data){
    var content = document.getElementById('content');
    content.ineerHTML='';
    if (data.length == 0){
        let frs = document.createElement("div");
        frs.classList.add("w3-container", "w3-card", "w3-white", "w3-round", "w3-margin");
        content.appendChild(frs);
        let notFound = document.createElement("h2");
        notFound.innerHTML = "No friend requests found";
        notFound.classList.add("w3-row-padding");
        notFound.style.margin = "20px";
        frs.appendChild(notFound);
    }
    else{
        for(let i = 0; i < data.length;i++ ){
            var frs = document.createElement('div');
            frs.classList.add("w3-container","w3-card","w3-white","w3-round","w3-margin");
            content.appendChild(frs);

            var title = document.createElement("h3");
            var request_id = data[i].id;// get request id
            var sender_dict = data[i].author; // info of the FR sender
            var receiver_dict = data[i].friend;

            var friend_name = data[i]['author']['displayName'];//get the friend name of the request
            var friend_info = document.createElement('a');//create a link to the friend's info
            var friend_id = data[i]['author']['id'];
            //click to see friend's info details
            friend_info.setAttribute('href','/service/authordetails/'+ friend_id);
            friend_info.innerHTML = friend_name;// set the href text

            title.innerHTML = "Friend Request from ";
            title.classList.add("w3-row-padding");
            title.style.marginTop = "20px";
            title.appendChild(friend_info);
            frs.appendChild(title);
            var acceptDiv = document.createElement("div");
            acceptDiv.classList.add("w3-row-padding");
            acceptDiv.style.marginBottom = "20px";
            frs.appendChild(acceptDiv);

            //create two buttons for changing status
            var acceptBtn = document.createElement("BUTTON");
            acceptBtn.classList.add('w3-button','w3-theme-d1','w3-margin-bottom');
            acceptBtn.style.marginLeft='40px';
            var acceptText = document.createTextNode("Accept");
            acceptBtn.addEventListener('click',function(){
                // sendFRrequest(request_id,sender_dict,receiver_id);
                acceptFRrequest(sender_dict['id'],sender_dict['host'],sender_dict['displayName'],sender_dict['url'],receiver_dict['displayName'],receiver_dict['id'])
            });
            acceptBtn.appendChild(acceptText);
            acceptDiv.appendChild(acceptBtn);

            var declineBtn = document.createElement('BUTTON');
            declineBtn.classList.add('w3-button','w3-theme-d1','w3-margin-bottom');
            declineBtn.style.marginLeft='10px';
            var declineText = document.createTextNode('Decline');
            declineBtn.addEventListener('click',function(){
                sendFRrequest(request_id,'Decline');
            });
            declineBtn.appendChild(declineText);
            acceptDiv.appendChild(declineBtn);
        }
    }
}
