function logon() {
    // var username = $('#username').val();
    var email = $('#email').val();
    // if (username === '') {
    //     alert('昵称不能为空！');
    //     return
    // }
    if (email === '') {
        alert('邮箱不能为空！');
        return
    }
    if (email === 'admin@admin.com'){
        alert('你咋就这么想当管理员呢？');
        return
    }
    $.ajax({
        url: '/api/login',
        data: JSON.stringify({
            // 'username': username,
            'email':email
        }),
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        statusCode: {
            200: function () {
                alert('欢迎回到我们的扯犊子公会');
                window.location.replace('/chatroom');
                // window.location.href = "index.html";
            },
            500: function (){
                alert('你确定你填写的信息对吗。');
                // window.location.replace('/');
            },
            590: function (){
                alert('不出意外的的话我出意外了！');
            }
        }
    })
}


function refresh() {
    $.ajax({
        url: '/api/login/token',
        data: JSON.stringify({
            'token': window.decodeURI(Cookies('token')),
        }),
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        statusCode: {
            200: function () {
                alert('欢迎回到我们的扯犊子公会');
                window.location.replace('/chatroom');
            },

        }

    })
}

refresh();
$('#logon').click(logon);

