// function to make a get request every 30s to get current pending friend request
// https://makitweb.com/how-to-fire-ajax-request-on-regular-interval/
function getFriendReuqest(){
    $.ajax({
        url:"/myBlog/friendrequest/",
        type:"get",
        success:function(data){
            // console.log(data);
            let reqeustNum =  data.length;
            let fRsign = document.querySelector('#FR');
            fRsign.innerHTML = reqeustNum;

        },
        complete:function(data){
            console.log('complete');
            setTimeout(getFriendReuqest,5000);
        },
        error:function(){
            console.log('error');
        }
    });
}


$(document).ready(function(){
    setTimeout(getFriendReuqest,0)
});

// when mouse hover on the notification icon, show how many requests coming
//https://www.w3schools.com/jquery/tryit.asp?filename=tryjquery_event_hover
$(document).ready(function(){
    $("#dropdown-hover").hover(function(){
        let currentRequest = document.querySelector('#FR').innerHTML;
        document.querySelector("#dropdown").innerHTML = currentRequest+ " new friend request!";
    })
});