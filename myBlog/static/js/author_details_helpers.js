
var author_id;
// get author details which are his posts
function getAuthorDetials(authorid){
    author_id = authorid;
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
    // the data are whole posts made by the author i want to see
    var content = document.getElementById('content');

    var aPosts = data['posts'][0];
    var authorDiv = document.createElement('div');
    authorDiv.classList.add("w3-container","w3-card","w3-white","w3-round","w3-margin");
    content.appendChild(authorDiv);
    var author_info_div = document.createElement('div');
    var userLogo = document.createElement('i');
    userLogo.classList.add("fa", "fa-user");
    userLogo.classList.add("w3-left", "w3-circle", "w3-margin-right");
    userLogo.style.width = "20px";
    userLogo.style.margin = "25px";
    author_info_div.appendChild(userLogo);

    var author_name = document.createElement('h3');
    author_name.innerHTML = 'NAME: '+ aPosts['author']['displayName'];
    author_info_div.appendChild(author_name);

    var author_url = document.createElement('a');

    author_url.innerHTML = aPosts['author']['url'].toString();
    author_url.setAttribute('href',aPosts['author']['url']);

    author_info_div.appendChild(author_url);
    authorDiv.appendChild(author_info_div);


    // follow button div
    var btnDiv = document.createElement('div');
    btnDiv.classList.add('w3-row-padding');
    btnDiv.style.marginBottom = '20px';
    authorDiv.appendChild(btnDiv);

    // boolean var to check whether is friend already
    var is_friend_bool;
    try{
        is_friend_bool = is_friend(author_id)['friends'];
    }catch (e) {
        is_friend_bool = false;
    }

    // boolean var to check whether this author has been followed by me before
    var has_followed_bool;
    try{
        has_followed_bool = has_followed(authorid);
    }catch(e){
        has_followed_bool = false;
    }

    if (is_friend_bool) {
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
        followBtn.style.marginLeft='30px';
        var followText = document.createTextNode('follow');
        followBtn.addEventListener('click',function(){
            sendFollowRequest(aPosts['author']['id'],aPosts['author']['host'],aPosts['author']['displayName'],aPosts['author']['url']);
        });
        followBtn.appendChild(followText);
        authorDiv.appendChild(followBtn);
    }
    var line = document.createElement('hr');
    line.classList.add('w3-clear');
    authorDiv.appendChild(line);


    // traverse data, render posts
    for (let i=0;i<data['posts'].length;i++){
        let posts = data['posts'][i];
        console.log(posts);
        let postsDiv = document.createElement('div');
        authorDiv.appendChild(postsDiv);

        let contentDiv = document.createElement('div');
        contentDiv.innerHTML = posts['content'];
        postsDiv.appendChild(contentDiv);
        let public_time = document.createElement('div');
        public_time.innerHTML = posts['published'];
        public_time.style.fontSize='0.8em';
        postsDiv.appendChild(public_time);

        // render all comments
        var commentContent = posts['comments'];
        for (let j=0; j<commentContent.length; j++){
            let commentDiv = document.createElement('div');
            commentDiv.innerHTML = commentContent[j]['comment'];
            commentDiv.style.fontSize='0.5em';
            postsDiv.appendChild(commentDiv);

        }




        let line = document.createElement('hr');
        line.classList.add('w3-clear');
        authorDiv.appendChild(line);







    }

}
