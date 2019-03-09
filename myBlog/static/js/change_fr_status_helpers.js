
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

    let url = "/myBlog/localfriendrequest/";
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
    //content.ineerHTML='';
    for(let i = 0; i < data.length;i++ ){
        var frs = document.createElement('div');
        frs.classList.add("w3-container","w3-card","w3-white","w3-round","w3-margin");
        content.appendChild(frs);

        var title = document.createElement("h3");
        var request_id = data[i].id;// get request id

        var friend_name = data[i]['author']['displayName'];//get the friend name of the request
        var friend_info = document.createElement('a');//create a link to the friend's info
        var friend_id = data[i]['author']['id'];
        //click to see friend's info details
        friend_info.setAttribute('href','/myBlog/author/'+friend_id);
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
            sendFRrequest(request_id,'Accept');
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
