//var author_id;
// get author details which are his posts
function getAuthorDetials(authorid){
    //author_id = authorid;
    let url = '/myBlog/author/'+authorid;
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

// check whether the author is my friend
function is_friend(authorid){
    let url = '/myBlog/friends/'+authorid;
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

// check if i have followed the author
function has_followed(authorid){
    let url = '/myBlog/friendrequest/';
    return fetch(url,{
        method:'GET',
        mode:"cors",
        cache:"no-cache",
        credentials:"same-origin",
        headers:{
            "Content-Type":"application/json"
        },
        redirect:"follow",
        referrer:"no-referrer",
    }).then(response => response.json()).catch(error=>console.log(error));
}
// follow the author
function sendFollowRequest(author_id,author_host,author_name,author_url){
    let request_form = {
        "query":"friendrequest",
        "friend":{
            'id':author_id,
            'host':author_host,
            'displayName':author_name,
            'url':author_url,
        }
    }
    let body = JSON.stringify(request_form);

    let url = "/myBlog/localfriendrequest/";
    return fetch(url,{
        method:"POST",
        mode:"cors",
        cache:"no-cache",
        credentials:"same-origin",
        body:body,
        headers:{
            "Content-Type":"application/json",
            "x-csrftoken":csrf_token
        },
        redirect:"follow",
        referrer:"no-referrer",
    }).then(data=>console.log(data))
        .then(document.location.reload(true))
}

// got data, render the page
function renderpage(data){
    var content = document.getElementById('content');

    // traverse data
    //for (let i=0;i<data.length;i++){
    var authorDiv = document.createElement('div');
    authorDiv.classList.add("w3-container","w3-card","w3-white","w3-round","w3-margin");
    content.appendChild(authorDiv);
    var userLogo = document.createElement('i');
    userLogo.classList.add("fa", "fa-user");
    userLogo.classList.add("w3-left", "w3-circle", "w3-margin-right");
    userLogo.style.width = "20px";
    userLogo.style.margin = "25px";
    authorDiv.appendChild(userLogo);

    var author_name = document.createElement('h3');
    author_name.innerHTML = 'NAME: '+ data['displayName'];
    // TODO: add more detail
    authorDiv.appendChild(author_name);

    var line = document.createElement('hr');
    line.classList.add('w3-clear');
    authorDiv.appendChild(line);

    var btnDiv = document.createElement('div');
    btnDiv.classList.add('w3-row-padding');
    btnDiv.style.marginBottom = '20px';
    authorDiv.appendChild(btnDiv);
    if (is_friend(data['id'])['friends']) {
        var unFriendBtn = document.createElement("BUTTON");
        unFriendBtn.classList.add('w3-button','w3-theme-d1','w3-margin-bottom');
        var unfriendText = document.createTextNode("Unfollow");
        //Todo: set un befriend
        // unFriendBtn.addEventListener('click',function(){
        //     sendUnfriend();
        // })
        unFriendBtn.appendChild(unfriendText);
        authorDiv.appendChild(unFriendBtn);
    }else{
        // if (has_followed(data['id'])[0][]) Todo: check if I have followed the author
        var followBtn = document.createElement("BUTTON");
        followBtn.classList.add('w3-button','w3-theme-d1','w3-margin-bottom');
        var followText = document.createTextNode('follow');
        followBtn.addEventListener('click',function(){
            sendFollowRequest(data['id'],data['host'],data['displayName'],data['url']);
        })
        followBtn.appendChild(followText);
        authorDiv.appendChild(followBtn);
        //}






    }

}
