var is_friend_bool;
var author_id;
var current_user_id;
var follow_status;
var aPosts;
var cuurent_user_name;

// https://stackoverflow.com/questions/6941533/get-protocol-domain-and-port-from-url
function get_host(){
    let current_url = window.location.href;
    let arr = current_url.split("/");
    let host_url = arr[0]+'//'+arr[2]+'/';
    return host_url;
}

// get author details which are the author's info & his posts
function getAuthorDetails(authorid,currentUserID,isFriend,followStatus,currentUserName){

    author_id = authorid;
    current_user_id = currentUserID;
    is_friend_bool = isFriend;
    follow_status = followStatus;
    cuurent_user_name = currentUserName;
    if (currentUserID != authorid){

        let url = '/myBlog/author/'+authorid+'/posts/';
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
    else{
        let url = '/myBlog/posts/mine/?size=10';
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
}

function sendFollowRequest(author_id,author_host,author_name,author_url,currentUserName){
    let host = get_host();
    let request_form = {
        "query":"friendrequest",
        "author":{
            'id':current_user_id,
            'host':host,
            'displayName':currentUserName,
            'url':host+current_user_id,
        },
        "friend":{
            'id':author_id,
            'host':author_host,
            'displayName':author_name,
            'url':author_url,
        }
    }
    let body = JSON.stringify(request_form);
    let url = "/myBlog/friendrequest/";
    return fetch(url,{
        method:"POST",
        mode:"cors",
        cache:"no-cache",
        credentials:"same-origin",
        body:body,
        headers:{
            "Content-Type":"application/json",
            "x-csrftoken":csrf_token,
        },
        redirect:"follow",
        referrer:"no-referrer",
    }).then(function(){
        //https://www.permadi.com/tutorial/jsInnerHTMLDOM/index.html
       document.getElementById('follow_Btn').childNodes[0].nodeValue="Followed";
    })
}
// got data, render the page
function renderpage(data){
    var content = document.getElementById('content');

    aPosts = data['posts'][0];
    let authorName = aPosts['author']['displayName'];
    let authorUrl = aPosts['author']['url'];
    let authorHost = aPosts['author']['host'];

    var authorDiv = document.createElement('div');
    authorDiv.setAttribute('id','author_div');
    authorDiv.classList.add("w3-container","w3-card","w3-white","w3-round","w3-margin");
    content.appendChild(authorDiv);

    var author_info_div = document.createElement('div');
    var userLogo = document.createElement('i');
    userLogo.classList.add("fa","fa-user");
    userLogo.classList.add("w3-left","w3-circle","w3-margin-right");
    userLogo.style.width="40px";
    userLogo.style.margin="25px";
    author_info_div.append(userLogo);

    var author_name = document.createElement('h3');
    author_name.innerHTML = authorName;
    author_info_div.appendChild(author_name);

    var author_url = document.createElement('a');
    author_url.innerHTML = authorUrl.toString();
    author_url.setAttribute('href',authorUrl);

    author_info_div.appendChild(author_url);
    authorDiv.appendChild(author_info_div);

    var btnDiv = document.createElement('div');
    btnDiv.setAttribute('id','btn_Div');
    btnDiv.classList.add('w3-row-padding');
    btnDiv.style.marginBottom = '20px';
    btnDiv.style.marginLeft='70px';
    authorDiv.appendChild(btnDiv);
    
    if (author_id != current_user_id){
        if(is_friend_bool=='true'){
            var unFriendBtn = document.createElement("BUTTON");
            unFriendBtn.classList.add('w3-button','w3-theme-d1','w3-margin-bottom');
            var unfriendText = document.createTextNode('Unfollow');
            unFriendBtn.appendChild(unfriendText);
            btnDiv.append(unFriendBtn);
            var isFriendText = document.createTextNode('Friend');
            btnDiv.append(isFriendText);
        }
        else{
            if(follow_status=='Pending' || follow_status=='Decline'){
                var unFriendBtn = document.createElement("BUTTON");
                unFriendBtn.classList.add('w3-button','w3-theme-d1','w3-margin-bottom');
                var unfriendText = document.createTextNode('Unfollow');
                unFriendBtn.appendChild(unfriendText);
                btnDiv.append(unFriendBtn);
                var followingText = document.createTextNode('Following');
                btnDiv.appendChild(followingText);

            }
            else if (follow_status=='notFound'){
                var followBtn = document.createElement("BUTTON");
                followBtn.setAttribute('id','follow_Btn');
                followBtn.classList.add('w3-button','w3-theme-d1','w3-margin-bottom');
                var followText = document.createTextNode('follow');
                followBtn.appendChild(followText);
                btnDiv.append(followBtn);
                followBtn.addEventListener('click',function(){
                    sendFollowRequest(author_id,authorHost,authorName,authorUrl,cuurent_user_name);
                });

            }
        }
    }

    let line = document.createElement('hr');
    line.classList.add('w3-clear');
    authorDiv.append(line);

}