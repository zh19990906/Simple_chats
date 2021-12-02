function logon() {
    var username = $('#username').val();
    var email = $('#email').val();
    if (username === '') {
        alert('昵称不能为空！');
        return
    }
    if (email === '') {
        alert('邮箱不能为空！');
        return
    }
    if (username === 'admin') {
        alert('你除了admin就不会换个名字？')
        return
    }
    var reg = new RegExp("^[a-z0-9]+([._\\-]*[a-z0-9])*@([a-z0-9]+[-a-z0-9]*[a-z0-9]+.){1,63}[a-z0-9]+$");
    if(!reg.test(email)){
        alert('用这个正确的邮箱你会死？')
        return
    }
    $.ajax({
        url: '/api/logon',
        data: JSON.stringify({
            'username': username,
            'email':email
        }),
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        // success: function (data) {
        //     if (!data['success']) {
        //         alert(data['reason']);
        //         //window.location.replace('/')
        //     }
        //     else {
        //         alert("123456")
        //         // window.location.replace('/room')
        //     }
        // },
        statusCode: {
            200: function () {
                alert('欢迎加入我们的扯犊子公会');
                window.location.replace('/');
                // window.location.href = "index.html";
            },
            500: function (){
                alert('你确定你填写的信息对吗。');
                // window.location.replace('/');
            },
            530: function (){
                alert('你的名字或者邮箱可能被用了，换个试试。');
                // window.location.replace('/');
            },
            590: function (){
                alert('不出意外的的话我出意外了！');
            }
        }
    })
}

$('#reg').click(logon);

