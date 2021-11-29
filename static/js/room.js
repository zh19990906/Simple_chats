function generate_chat_list_html(chat_list,username) {
    var msg_list = '';
    // alert(chat_list['spoken_text'])
    for (i = 0; i < chat_list.length; i++) {
        msg = chat_list[i]['spoken_text'];
        nick = chat_list[i]['spoke_man'];
        post_time = chat_list[i]['spoke_time'];
        var line = '<div class="columns" style="margin-top: 5px">';
        line += '<div class="user_name">';
        if (nick === username) {
            line += '<span class="label label-success centered">' + '我' + '</span>';
        } else {
            line += '<span class="label label-secondary">' + nick + '</span>';
        }
        line += '</div>';
        line += '<div class="text-gray">';
        line += '<span class="label">' + post_time + '</span>';
        line += '</div>';
        line += '<br />';
        line += '<div class="float-right">' + msg + '</div>';
        line += '</div>';
        msg_list += line;
    }
    return msg_list
}

function refresh() {
    $.ajax({
        url: '/api/speak/log',
        data: JSON.stringify({
            'token': window.decodeURI(Cookies('token')),
            'chat_name':'text',
        }),
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        success: function (data) {
            // console.log(data.data);
            var chat_list_html = generate_chat_list_html(data.data,data.username);

            $(".panel-body").html(chat_list_html)
        },
        statusCode: {
            400: function (){
                alert('emmm聊天室丢了');
                window.location.replace('/');
            },
            300: function (){
                alert('你可以重新登陆一下再来');
                window.location.replace('/');
            },

        }

    })
}

function post_data() {
    var msg = $('.form-input').val();
    if (msg === '') {
        alert('内容不能为空！');
        return
    }

    $.ajax({
        url: '/api/speak',
        data: JSON.stringify({
            'token': window.decodeURI(Cookies('token')),
            'chat_name':'text',
            'spoken_text': msg
        }),
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        statusCode: {
            200: function () {
                // alert('欢迎加入我们的扯犊子公会');
                // window.location.replace('/');
                refresh();
                $("#divId").val("");
                time();
                // window.location.href = "index.html";

            },
            400: function (){
                alert('emmm聊天室丢了');
                // window.location.replace('/');
            },
            300: function (){
                alert('你可以重新登陆一下再来');
                window.location.replace('/');
            },
            590: function (){
                alert('不出意外的的话我出意外了！');
            },
            500: function (){
                window.location.replace('/');
            }

        }
    });
    var wait = 10;
    function time() {
        var btn = document.querySelector('button');
        if (wait == 0) {
            btn.removeAttribute("disabled");
            btn.innerHTML = "发送";
            wait = 10;
        } else {
            btn.setAttribute("disabled", true);
            btn.innerHTML = wait + "秒后重新发言";
            // console.log(wait + "秒后重新获取验证码");
            wait--;
            setTimeout(function () {
                    time(btn);
                },
                1000)
        }
    }
}
$('#post').click(post_data);
refresh();
setInterval(refresh, 10000);