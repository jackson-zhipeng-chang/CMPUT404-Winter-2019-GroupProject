// boolean var to check whether is friend already
var is_friend_bool;
var author_id;
var current_user_id;
var aPosts;
// get author details which are his posts
function getAuthorDetials(authorid,currentUserID){
    author_id = authorid;
    current_user_id = currentUserID;
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
    }).then(response=>response.json())
        .then(data=>{

            is_friend_bool = data['friends'];
            if (author_id!=current_user_id){
                if (is_friend_bool=='true'){
                    var unFriendBtn = document.createElement("BUTTON");
                    unFriendBtn.classList.add('w3-button','w3-theme-d1','w3-margin-bottom');
                    var unfriendText = document.createTextNode("Unfollow");
                    unFriendBtn.appendChild(unfriendText);
                    let parentDiv = document.getElementById('author_div');
                    parentDiv.appendChild(unFriendBtn);
                    // unFriendBtn.addEventListener('click',function(){
                    //     sendUnFollowRequest()
                    // })

                }else{
                    console.log('here');
                    var followBtn = document.createElement("BUTTON");
                    followBtn.classList.add('w3-button','w3-theme-d1','w3-margin-bottom');
                    followBtn.style.marginLeft='30px';
                    followBtn.setAttribute('id','follow_Btn');
                    var followText = document.createTextNode('follow');

                    followBtn.appendChild(followText);
                    let parentDiv = document.getElementById('author_div');
                    parentDiv.appendChild(followBtn);
                    followBtn.addEventListener('click',function(){
                        sendFollowRequest(aPosts['author']['id'],aPosts['author']['host'],aPosts['author']['displayName'],aPosts['author']['url']);
                    });
                    var line = document.createElement('hr');
                    line.classList.add('w3-clear');
                    parentDiv.appendChild(line);
                }
            }else{
                let parentDiv = document.getElementById('author_div');
                var line = document.createElement('hr');
                line.classList.add('w3-clear');
                parentDiv.appendChild(line);
            }
        });
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
    }).then(function(){
        //https://www.permadi.com/tutorial/jsInnerHTMLDOM/index.html
       document.getElementById('follow_Btn').childNodes[0].nodeValue="Followed";

    })
}

// got data, render the page
function renderpage(data){
    // the data are whole posts made by the author i want to see
    var content = document.getElementById('content');

    aPosts = data['posts'][0];
    var authorDiv = document.createElement('div');
    authorDiv.setAttribute('id','author_div');
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


    try{
        is_friend(author_id).then(function(){
            // traverse data, render posts
            for (let i=0;i<data['posts'].length;i++) {
                let posts = data['posts'][i];
                console.log(posts);
                let postsDiv = document.createElement('div');
                authorDiv.appendChild(postsDiv);

                let contentDiv = document.createElement('div');
                contentDiv.innerHTML = posts['content'];
                postsDiv.appendChild(contentDiv);
                let public_time = document.createElement('div');
                public_time.innerHTML = posts['published'];
                public_time.style.fontSize = '0.8em';
                postsDiv.appendChild(public_time);

                // render all comments
                var commentContent = posts['comments'];
                for (let j = 0; j < commentContent.length; j++) {
                    let commentDiv = document.createElement('div');
                    commentDiv.innerHTML = commentContent[j]['comment'];
                    commentDiv.style.fontSize = '0.5em';
                    postsDiv.appendChild(commentDiv);

                }


                let line = document.createElement('hr');
                line.classList.add('w3-clear');
                authorDiv.appendChild(line);
            }

        });
    }catch (e) {
        console.log(e);
    }

    // // boolean var to check whether this author has been followed by me before
    // var has_followed_bool;
    // try{
    //     has_followed_bool = has_followed(authorid);
    // }catch(e){
    //     has_followed_bool = false;
    // }







    // // traverse data, render posts
    // for (let i=0;i<data['posts'].length;i++){
    //     let posts = data['posts'][i];
    //     console.log(posts);
    //     let postsDiv = document.createElement('div');
    //     authorDiv.appendChild(postsDiv);
    //
    //     let contentDiv = document.createElement('div');
    //     contentDiv.innerHTML = posts['content'];
    //     postsDiv.appendChild(contentDiv);
    //     let public_time = document.createElement('div');
    //     public_time.innerHTML = posts['published'];
    //     public_time.style.fontSize='0.8em';
    //     postsDiv.appendChild(public_time);
    //
    //     // render all comments
    //     var commentContent = posts['comments'];
    //     for (let j=0; j<commentContent.length; j++){
    //         let commentDiv = document.createElement('div');
    //         commentDiv.innerHTML = commentContent[j]['comment'];
    //         commentDiv.style.fontSize='0.5em';
    //         postsDiv.appendChild(commentDiv);
    //
    //     }
    //
    //
    //
    //
    //     let line = document.createElement('hr');
    //     line.classList.add('w3-clear');
    //     authorDiv.appendChild(line);
    //
    //
    //
    //
    //
    //
    //
    // }

}
