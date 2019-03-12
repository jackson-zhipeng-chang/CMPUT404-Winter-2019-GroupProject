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
       document.getElementById('follow_Btn').childNodes[0].nodeValue="Following";

    })
}

function commentPost(id) {
    let commentForm =
        {
            "query": "addComment",
            "comment":
                {
                    "comment": "",
                    "contentType": "text/plain"
                }
        }
    commentForm.comment.comment = document.getElementById("commentInput" + id).value;
    let body = JSON.stringify(commentForm);
    let url = "/myBlog/posts/" + id + "/comments/";
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
            if (response.status === 200) {
                document.location.reload(true);
            } else {
                alert("Something went wrong: " + response.status);
            }
        });
}
// got data, render the page
function renderpage(data){
    var content = document.getElementById('content');

    aPosts = data['posts'][0];
    var authorName = aPosts['author']['displayName'];
    var authorUrl = aPosts['author']['url'];
    var authorHost = aPosts['author']['host'];
    var authorGithub = aPosts['author']['github'];

    var authorDiv = document.createElement('div');
    authorDiv.setAttribute('id','author_div');
    authorDiv.classList.add("w3-container","w3-card","w3-white","w3-round","w3-margin");
    content.appendChild(authorDiv);

    var author_name_div = document.createElement('div');
    author_name_div.setAttribute('id','authorname')
    author_name_div.classList.add('w3-margin-top','w3-left');
    authorDiv.appendChild(author_name_div);

    var userLogo = document.createElement('i');
    userLogo.classList.add("fa","fa-user");
    userLogo.classList.add("w3-center","w3-circle");
    userLogo.style.width="50px";
    author_name_div.appendChild(userLogo);


    var author_name = document.createElement('h3');
    author_name.innerHTML = authorName;
    author_name.classList.add("w3-margin-right","w3-show-inline-block");
    author_name_div.appendChild(author_name);

    var btnDiv = document.createElement('div');
    btnDiv.setAttribute('id','btn_Div');
    btnDiv.classList.add("w3-white","w3-round","w3-margin");
    author_name_div.appendChild(btnDiv);


    var author_info_div = document.createElement('div');
    authorDiv.appendChild(author_info_div);
    author_info_div.classList.add("w3-container","w3-card","w3-white","w3-round","w3-margin","w3-right");
    author_info_div.style.width = '400px';

    var info_text = document.createElement('h4');
    info_text.innerHTML='User Info';
    author_info_div.appendChild(info_text);

    var url_text = document.createElement('h5');
    url_text.innerHTML = 'Url: ';
    url_text.style.fontSize='15px';
    url_text.style.marginBottom='0px';
    author_info_div.appendChild(url_text);

    var author_url = document.createElement('a');
    author_info_div.appendChild(author_url);
    author_url.innerHTML = authorUrl.toString();
    author_url.setAttribute('href',authorUrl);
    author_url.style.fontSize = '15px';

    var github_text = document.createElement('h5');
    github_text.innerHTML = 'Github: ';
    github_text.style.fontSize='15px';
    github_text.style.marginBottom='0px';
    author_info_div.appendChild(github_text);

    if (authorGithub){
        let github_url = document.createElement('a');
        author_info_div.appendChild(github_url);
        github_url.innerHTML = authorGithub.toString();
        github_url.setAttribute('href',authorGithub);
        github_url.style.fontSize = '15px';
    }else{
        var blank = document.createElement('br');
        author_info_div.appendChild(blank);
    }

    if(is_friend_bool=='true'){
        var dropdownDiv = document.createElement('div');
        btnDiv.appendChild(dropdownDiv);
        dropdownDiv.classList.add('w3-dropdown-hover');

        var unFriendBtn = document.createElement("BUTTON");
        dropdownDiv.appendChild(unFriendBtn);
        unFriendBtn.classList.add('w3-button','w3-theme-d1');

        var dropdownContentDiv = document.createElement('div');
        dropdownDiv.appendChild(dropdownContentDiv);
        dropdownContentDiv.classList.add("w3-dropdown-content","w3-card-4", "w3-bar-block");

        var contentlink = document.createElement('a');
        dropdownContentDiv.appendChild(contentlink);
        contentlink.classList.add("w3-bar-item", "w3-button");
        // contentlink.setAttribute('href','#');
        contentlink.innerHTML='Unfollow';
        // TODO: change function
        // contentlink.setAttribute('onclick',sendFollowRequest(author_id,authorHost,authorName,authorUrl,cuurent_user_name));


        var unfriendText = document.createTextNode('Friend');
        unFriendBtn.appendChild(unfriendText);
    }
    else{
        if(follow_status=='Pending' || follow_status=='Decline'){
            var dropdownDiv = document.createElement('div');
            btnDiv.appendChild(dropdownDiv);
            dropdownDiv.classList.add('w3-dropdown-hover');

            var unFriendBtn = document.createElement("BUTTON");
            dropdownDiv.appendChild(unFriendBtn);
            unFriendBtn.classList.add('w3-button','w3-theme-d1');

            var dropdownContentDiv = document.createElement('div');
            dropdownDiv.appendChild(dropdownContentDiv);
            dropdownContentDiv.classList.add("w3-dropdown-content","w3-card-4", "w3-bar-block");

            var contentlink = document.createElement('a');
            dropdownContentDiv.appendChild(contentlink);
            contentlink.classList.add("w3-bar-item", "w3-button");
            // contentlink.setAttribute('href','#');
            contentlink.innerHTML='Unfollow';
            // TODO: change function
            // contentlink.setAttribute('onclick',sendFollowRequest(author_id,authorHost,authorName,authorUrl,cuurent_user_name));
            var unfriendText = document.createTextNode('Following');
            unFriendBtn.appendChild(unfriendText);
        }
        else if (follow_status=='notFound'){
            var followBtn = document.createElement("BUTTON");
            followBtn.setAttribute('id','follow_Btn');
            followBtn.classList.add('w3-button','w3-theme-d1','w3-margin-bottom');
            var followText = document.createTextNode('Follow');
            followBtn.appendChild(followText);
            btnDiv.appendChild(followBtn);
            followBtn.addEventListener('click',function(){
                sendFollowRequest(author_id,authorHost,authorName,authorUrl,cuurent_user_name);
            });

        }
    }
            // traverse data, render posts
    for (let i=0;i<data['posts'].length;i++) {
        let posts = data['posts'][i];
        let postsDiv = document.createElement('div');
        postsDiv.classList.add("w3-container", "w3-card", "w3-white", "w3-round", "w3-margin");
        content.appendChild(postsDiv);

        var title = document.createElement('h3');
        title.innerHTML = posts.title;
        title.classList.add('w3-row-padding');
        title.style.margin = '0 20p;x';
        title.style.marginTop='10px';
        postsDiv.appendChild(title);

        var line = document.createElement('hr');
        line.classList.add('w3-clear');
        postsDiv.appendChild(line);

        var divDescription = document.createElement('div');
        divDescription.classList.add('w3-row-padding');
        divDescription.style.margin = '0 20px';
        postsDiv.appendChild(divDescription);

        if(posts.contentType == 'image/png;base64' || posts.contentType == 'image/jpeg;base64'){
            var imgContent = document.createElement('img');
            imgContent.src = posts.content;
            imgContent.style.width='20%';
            imgContent.style.height = '20%';
        }else{
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

        for (let j=0; j < posts.comments.length;j++){
            var comment = document.createElement('p');
            comment.innerHTML = posts.comments[j].author.displayName+' commented: '+ posts.comments[j].comment;
            divDescription.appendChild(comment);
        }

        var commentInput = document.createElement('textarea');
        commentInput.id = 'commentInput'+posts.postid;
        commentInput.classList.add('w3-border','w3-padding');
        commentInput.type = 'text';
        commentInput.style.width='100%';
        divDescription.appendChild(commentInput);

        var commentButton = document.createElement('button');
        commentButton.classList.add('w3-buuton',"w3-theme-d1", "w3-margin-bottom", "w3-right");
        commentButton.insertAdjacentHTML("beforeend","<i class='fa fa-comment'></i>  Comment");
        let post_id = posts.postid;
        commentButton.onclick=function(){commentPost(post_id)};
        divDescription.appendChild(commentButton);

    }


    // if (data.next !=null){
    //     var nextButton = document.createElement('button');
    //     nextButton.classList.add("w3-button", "w3-theme-d1", "w3-margin-bottom", "w3-right");
    //     nextButton.insertAdjacentHTML("beforeend", "<i class='fa fa-arrow-right	'></i> Next Page");
    //     nextButton.onclick=function(){getAuthorDetails(data.next).then(renderpage)} ;
    //     content.appendChild(nextButton);
    // }
    //
    // if (data.previous != null){
    //     var nextButton = document.createElement('button');
    //     nextButton.classList.add("w3-button", "w3-theme-d1", "w3-margin-bottom", "w3-right");
    //     nextButton.insertAdjacentHTML("beforeend", "<i class='fa fa-arrow-left	'></i> Previous Page");
    //     nextButton.onclick=function(){getAuthorDetails(data.next).then(renderpage)} ;

    //}

}