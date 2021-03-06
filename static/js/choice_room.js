function go_chat(bt) {
    console.log(bt);
    var chat_only_name = bt.value;
    console.log(chat_only_name);
    $.ajax({
        url: '/api/chatroom/check',
        data: JSON.stringify({
            'token': window.decodeURI(Cookies('token')),
            'chat_only_name':chat_only_name
        }),
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        statusCode: {
            200: function (data) {
                console.log(data.chat_only_data['chat_only_name']);
                var chat_only_name = data.chat_only_data['chat_only_name'];
                window.location.replace('/chatroom/'+chat_only_name+'');
            },
            333:function(){
                alert('你可以刷新一下界面再试试。');
                window.location.replace('/chatroom');
            },
            300: function (){
                alert('你可以重新登陆一下再来');
                window.location.replace('/');
            },

        }
    })

}

function logout() {
    $.ajax({
        url: '/api/logout',
        data: JSON.stringify({
            'token': window.decodeURI(Cookies('token')),
        }),
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        statusCode: {
            200: function () {
                window.location.replace('/');
            },
            363: function () {
                window.location.replace('/');
            }
        }
    })

}

function sign_in(){
    $.ajax({
        url: '/api/sign/in',
        data: JSON.stringify({
            'token': window.decodeURI(Cookies('token')),
        }),
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        statusCode: {
            200: function (data) {
                 console.log(data.integral);
                alert('本次签到获得：'+data.integral+'积分');
                // window.location.replace('/');
                var btn = document.querySelector("#Sign_in");
                btn.setAttribute("disabled", true);
                btn.innerHTML = "今日已签到";
            },
            443: function () {
                alert('积分虽好请不到贪杯！');
            },
            500: function () {
                window.location.replace('/');
            }
        }
    })
}

$('#Sign_in').click(sign_in);

$('#logout').click(logout);


