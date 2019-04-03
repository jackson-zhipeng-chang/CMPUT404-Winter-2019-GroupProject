var is_friend_bool;
var author_id;
var current_user_id;
var follow_status;
var cuurent_user_name;
var current_user_github;
var authorName;
var authorUrl;
var authorHost;
var authorGithub;


// https://stackoverflow.com/questions/6941533/get-protocol-domain-and-port-from-url
function get_host(){
    let current_url = window.location.href;
    let arr = current_url.split("/");
    let host_url = arr[0]+'//'+arr[2]+'/';
    return host_url;
}

// get author details which are the author's info & his posts
function getAuthorDetails(authorid,currentUserID,isFriend,followStatus,currentUserName,friend_host,friend_url,friend_name,friend_github,user_github){
    author_id = authorid;
    current_user_id = currentUserID;
    is_friend_bool = isFriend;
    follow_status = followStatus;
    cuurent_user_name = currentUserName;
    current_user_github=user_github;
    authorName = friend_name;
    authorUrl = friend_url;
    authorHost = friend_host;
    authorGithub = friend_github;
    if (currentUserID != authorid){
        let url = '/service/author/'+authorid+'/posts/';
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
        let url = '/service/posts/mine/?size=10';
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
function sendUnFriendRequest(author_id){
    let url = '/service/unfriend/'+author_id+'/';
    return fetch(url,{
        method:"delete",
        mode:"cors",
        cache:"no-cache",
        credentials:"same-origin",
        headers:{
            "Content-Type":"application/json;charset=utf-8",
            "Accept": "application/json",
            "x-csrftoken":csrf_token,
        },
        redirect:"follow",
        referrer:"no-referrer",
    })
    .then(response => {
        if (response.status === 200) 
        { 
            document.location.reload(true); 
        } 
        else 
        {
            alert("Something went wrong: " +  response.status);
        }
    }); 
}
function sendFollowRequest(author_id,author_host,author_name,author_url,currentUserName,currentUserID){
    let host = get_host();
    console.log(host)
    let request_form = {
        "query":"friendrequest",
        "author":{
            'id':currentUserID,
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
    console.log(body);
    // let url = author_host+"service/friendrequest/";
    let url_local = host+"service/friendrequest/";
    // console.log("Sending to author server:");
    // console.log(url);
    return fetch(url_local,{
        method:"POST",
        mode:"cors",
        cache:"no-cache",
        credentials:"same-origin",
        body:body,
        headers:{
            "Content-Type":"application/json",
            "Accept": "application/json",
            "x-csrftoken":csrf_token,
        },
        redirect:"follow",
        referrer:"no-referrer",
    })
    .then(response => {
        if (response.status === 200) {
           document.location.reload(true);
        }else{
           alert("Something went wrong: " +  response.status);
        }
    })

}

// got data, render the page
function renderpage(data){
    var content = document.getElementById('content');

    var authorDiv = document.createElement('div');
    authorDiv.setAttribute('id','author_div');
    authorDiv.classList.add("w3-container","w3-card","w3-white","w3-round","w3-margin");
    content.appendChild(authorDiv);

    var userLogo = document.createElement('i');
    userLogo.classList.add("fa","fa-user");
    userLogo.classList.add("w3-left","w3-circle","w3-margin-right");
    userLogo.style.width="20px";
    userLogo.style.margin='25px';
    authorDiv.appendChild(userLogo);

    var name = document.createElement('h3');
    name.innerHTML = "Name: " +authorName;
    name.style.margin = "14px";
    authorDiv.appendChild(name);

    var id = document.createElement('p');
    id.innerHTML = "Id: " + author_id;
    id.style.margin='14px';
    authorDiv.appendChild(id);

    var divDescription = document.createElement('div');
    divDescription.style.margin='14px';
    authorDiv.appendChild(divDescription);

    var url = document.createElement('p');
    url.innerHTML ='URL: '+authorUrl.toString();
    url.style.marginLeft='48px';
    divDescription.appendChild(url);

    var github = document.createElement('p');
    github.innerHTML = 'Github: '+authorGithub;
    github.style.marginLeft='48px';
    divDescription.appendChild(github);

    var btnDiv = document.createElement('div');
    btnDiv.setAttribute('id','btn_Div');
    btnDiv.classList.add("w3-white","w3-round","w3-margin","w3-right");
    authorDiv.appendChild(btnDiv);

    if(current_user_id!=author_id) {
        if (is_friend_bool == 'true') {
            var dropdownDiv = document.createElement('div');
            btnDiv.appendChild(dropdownDiv);
            dropdownDiv.classList.add('w3-dropdown-hover');

            var unFriendBtn = document.createElement("BUTTON");
            dropdownDiv.appendChild(unFriendBtn);
            unFriendBtn.classList.add('w3-button', 'w3-theme-d1');

            var dropdownContentDiv = document.createElement('div');
            dropdownDiv.appendChild(dropdownContentDiv);
            dropdownContentDiv.classList.add("w3-dropdown-content", "w3-card-4", "w3-bar-block");

            var contentlink = document.createElement('a');
            dropdownContentDiv.appendChild(contentlink);
            contentlink.classList.add("w3-bar-item", "w3-button");
            contentlink.innerHTML = 'Unfollow';
            // TODO: change function
            contentlink.addEventListener('click',function(){
                sendUnFriendRequest(author_id);
            });


            var unfriendText = document.createTextNode('Friend');
            unFriendBtn.appendChild(unfriendText);
        } 

        else {
            if (follow_status == 'Pending' || follow_status == 'Decline') {
                var dropdownDiv = document.createElement('div');
                btnDiv.appendChild(dropdownDiv);
                dropdownDiv.classList.add('w3-dropdown-hover');

                var unFriendBtn = document.createElement("BUTTON");
                dropdownDiv.appendChild(unFriendBtn);
                unFriendBtn.classList.add('w3-button', 'w3-theme-d1');

                var dropdownContentDiv = document.createElement('div');
                dropdownDiv.appendChild(dropdownContentDiv);
                dropdownContentDiv.classList.add("w3-dropdown-content", "w3-card-4", "w3-bar-block");

                var contentlink = document.createElement('a');
                dropdownContentDiv.appendChild(contentlink);
                contentlink.classList.add("w3-bar-item", "w3-button");
                contentlink.innerHTML = 'Unfollow';
                // TODO: change function
                contentlink.addEventListener('click',function(){
                    sendUnFriendRequest(author_id);
                });
                var unfriendText = document.createTextNode('Following');
                unFriendBtn.appendChild(unfriendText);
            } 
            else if (follow_status == 'notFound') {
                var followBtn = document.createElement("BUTTON");
                followBtn.setAttribute('id', 'follow_Btn');
                followBtn.classList.add('w3-button', 'w3-theme-d1', 'w3-margin-bottom');
                var followText = document.createTextNode('Follow');
                followBtn.appendChild(followText);
                btnDiv.appendChild(followBtn);
                followBtn.addEventListener('click', function () {
                    sendFollowRequest(author_id, authorHost, authorName, authorUrl, cuurent_user_name,current_user_id);
                });

            }
        }
        // traverse data, render posts
        for (let i = 0; i < data['posts'].length; i++) {
            let posts = data['posts'][i];
            let postsDiv = document.createElement('div');
            postsDiv.classList.add("w3-container", "w3-card", "w3-white", "w3-round", "w3-margin");
            content.appendChild(postsDiv);

            var post_details_link = document.createElement("a");
            post_details_link.setAttribute('href','/service/postdetails/'+data.posts[i].id+'/');
            postsDiv.appendChild(post_details_link);
            var title = document.createElement("h3");
            title.innerHTML = data.posts[i].title;
            title.classList.add("w3-row-padding");
            title.style.marginTop = "20px";
            title.style.marginLeft = "20px";
            post_details_link.appendChild(title);

            var line = document.createElement('hr');
            line.classList.add('w3-clear');
            line.style.marginLeft = '25px';
            line.style.marginRight = '25px';
            postsDiv.appendChild(line);

            var divDescription = document.createElement('div');
            divDescription.classList.add('w3-row-padding');
            divDescription.style.margin = '0 20px';
            postsDiv.appendChild(divDescription);

            if (posts.contentType == 'image/png;base64' || posts.contentType == 'image/jpeg;base64') {
                var imgContent = document.createElement('img');
                imgContent.src = posts.content;
                imgContent.style.width = '20%';
                imgContent.style.height = '20%';
            } 
            else {
                var imgContent = document.createElement('p');
                imgContent.innerHTML = posts.content;
            }
            divDescription.appendChild(imgContent);

            var line = document.createElement('hr');
            line.classList.add('w3-clear');
            divDescription.appendChild(line);

            var commentText = document.createElement('h4');
            commentText.innerHTML = 'Comments';
            divDescription.appendChild(commentText);

            for (let j = 0; j < posts.comments.length; j++) {
                var comment = document.createElement('p');
                comment.innerHTML = posts.comments[j].author.displayName + ' commented: ' + posts.comments[j].comment;
                divDescription.appendChild(comment);
            }

            var commentInput = document.createElement('textarea');
            commentInput.id = 'commentInput' + posts.id;
            commentInput.classList.add('w3-border', 'w3-padding');
            commentInput.type = 'text';
            commentInput.style.width = '100%';
            divDescription.appendChild(commentInput);

            var commentButton = document.createElement('button');
            commentButton.classList.add('w3-buuton', "w3-theme-d1", "w3-margin-bottom", "w3-right");
            commentButton.insertAdjacentHTML("beforeend", "<i class='fa fa-comment'></i>  Comment");
            let post_id = posts.id;
            let post_host = posts.author.host;
            commentButton.onclick = function () {
                commentPost(post_id,post_host,current_user_id,cuurent_user_name,current_user_github);
            };
            divDescription.appendChild(commentButton);

        }
    }
}
