<!DOCTYPE html>
<html lang="fa">
<head>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Group Chatroom</title>
    {% load static %} <!-- بارگذاری تگ static -->
    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body {
            background-color: #e9ecef;
        }
        #chat-log {
            border: 2px solid #007bff;
            height: 400px;
            overflow-y: scroll;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        #chat-message-input {
            width: 80%;
            border-radius: 30px;
            padding: 10px;
            border: 1px solid #ccc;
        }
        #chat-file-input {
            margin-left: 10px;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
            background-color: #f8f9fa;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        .input-group {
            margin-top: 15px;
        }
        h1 {
            color: #007bff;
            font-weight: bold;
            font-size: 36px;
        }
        .logout-btn, .back-btn {
            background-color: #dc3545;
            color: white;
            border: none;
            border-radius: 25px;
            padding: 10px 20px;
            font-weight: bold;
            cursor: pointer;
        }
        .logout-btn:hover, .back-btn:hover {
            background-color: #c82333;
        }
        .avatar {
            border-radius: 50%;
            width: 40px;
            height: 40px;
            margin-right: 10px;
        }
        #member-list {
            border: 2px solid #007bff;
            border-radius: 10px;
            padding: 15px;
            background-color: #ffffff;
            height: 400px;
            overflow-y: auto;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        .popup {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: #ffffff;
            border: 2px solid #007bff;
            padding: 20px;
            z-index: 1000;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            width: 80%;
            max-width: 500px;
        }
        .popup button {
            margin: 5px;
            padding: 12px 25px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 30px;
            cursor: pointer;
        }
        .popup button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body class="container mt-4">
    <!-- دکمه خروج -->
    <a href="{% url 'logout' %}" class="logout-btn">خروج</a>


    <!-- عنوان گروه -->
    <h1 class="text-center">{{ group.name }}</h1>

    <a href="{% url 'index' %}" class="back-btn">برگشت</a>

    <div class="row">
        <!-- پنل چت -->
        <div class="col-md-8">
            <div id="chat-log" class="mb-3">
                {% for message in messages %}
                    <div class="message">
                        {% if message.user.userprofile.avatar %}
                        <a href="{% url 'private_chat' target_username=message.user.username %}">
                        
                            <img src="{{ message.user.userprofile.avatar.url }}" alt="Avatar" class="avatar" width="40" height="40">
                        </a>
                    {% else %}
       
                            <img src="{% static 'profiles/default.png' %}" alt="Default Avatar" class="avatar" width="40" height="40">
                        
                    {% endif %}
                    <strong>
           
                            {{ message.user.username }}
                      
                    </strong>
                    {% if message.file %}
                        <a href="{{ message.file.url }}">{{ message.file.name }}</a> <!-- لینک به فایل -->
                    {% else %}
                        {{ message.content }}
                    {% endif %}
                    <br>
                    <small>{{ message.timestamp }}</small>
                </div>
                {% endfor %}
            </div>

            <!-- ورودی پیام و فایل -->
            <div class="input-group">
                <input id="chat-message-input" type="text" class="form-control" placeholder="پیام خود را وارد کنید...">
                <input id="chat-file-input" type="file" class="ml-2">
                <div class="input-group-append">
                    <button id="chat-message-submit" class="btn btn-primary">ارسال</button>
                    <button id="emoji-button">😊</button>
                    <div id="emoji-list" style="display:none;">
                        <span class="emoji" data-emoji="😊">😊</span>
                        <span class="emoji" data-emoji="😂">😂</span>
                        <span class="emoji" data-emoji="😍">😍</span>
                        <span class="emoji" data-emoji="😢">😢</span>
                        <!-- اموجی‌های بیشتر -->
                    </div>
                </div>
            </div>
        </div>

        <!-- لیست اعضا -->
        <div class="col-md-4">
            <h4>اعضا</h4>
            <ul id="member-list" class="list-group">
                {% for user in members %}
                <li class="list-group-item" data-username="{{ user.username }}" onclick="sendNotification('{{ user.id }}')">
                    {% if user.userprofile.avatar %}
                        <img src="{{ user.userprofile.avatar.url }}" alt="Avatar" class="avatar" width="30" height="30">
                    {% else %}
                        <img src="{% static 'profiles/default.png' %}" alt="Default Avatar" class="avatar" width="30" height="30">
                    {% endif %}
                    {{ user.username }}
                </li>
                {% endfor %}
            </ul>
            <!-- فرم اضافه کردن عضو جدید -->
            <h5 class="mt-4">اضافه کردن عضو جدید</h5>
            <form method="post" action="{% url 'group_chat' group.slug  %}">
                {% csrf_token %}
                <div class="form-group">
                    <select name="username" class="form-control">
                        {% for user in all_users %}
                            <option value="{{ user.username }}">{{ user.username }}</option>
                        {% endfor %}
                    </select>
                </div>
                <button type="submit" name="add_member" class="btn btn-success btn-block">افزودن</button>
            </form>
        </div>
    </div>

    <!-- Bootstrap JS and dependencies -->
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.3/dist/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>

    <script>
        const groupSlug = "{{ group.slug }}";
        const chatSocket = new WebSocket(
            'ws://' + window.location.host + '/cht/ws/chat/' + groupSlug + '/'
        );

        // WebSocket برای اعلان‌ها
        const username = "{{ request.user.username }}"; // نام کاربری را از Django بگیرید
        const notificationSocket = new WebSocket(
            'ws://' + window.location.host + '/cht/ws/notifications/' + username + '/'
        );
        
        // console.log(username)
        console.log(notificationSocket)


        chatSocket.onmessage = function(e) {
            console.log("aki",e)
            const data = JSON.parse(e.data);
            console.log("aki",data)

            const chatLog = document.querySelector('#chat-log');
            
            if (data.message) {
                const currentTime = new Date().toLocaleString('en-US', { timeZone: 'Asia/Tehran' });
                const newMessage = document.createElement('div');
                newMessage.classList.add('message');
                newMessage.innerHTML = 
                    <img src="${data.avatar_url}" alt="Avatar" class="avatar" width="40" height="40">
                    <strong class="username" data-username="${data.user}">${data.user}:</strong> ${data.message} <br>
                    <small>${currentTime}</small>
                ;
                
                chatLog.appendChild(newMessage);
                
                // Scroll to the bottom
                chatLog.scrollTop = chatLog.scrollHeight;

                console.log(data.user);

                
            }

            if (data.file) {
                const newFileMessage = document.createElement('div');
                newFileMessage.classList.add('message');
                newFileMessage.innerHTML = 
                    <strong>${data.user}:</strong> <a href="${data.file}">${data.filename}</a>
                ;
                chatLog.appendChild(newFileMessage);
                chatLog.scrollTop = chatLog.scrollHeight;
            }
    
        };

        document.querySelector('#chat-message-input').focus();
        document.querySelector('#chat-message-input').onkeyup = function(e) {
            if (e.keyCode === 13) {  // Enter key
                document.querySelector('#chat-message-submit').click();
            }
        };

        document.querySelector('#chat-message-submit').onclick = function(e) {
            const messageInputDom = document.querySelector('#chat-message-input');
            const message = messageInputDom.value;
            const fileInput = document.querySelector('#chat-file-input');

            if (message || (fileInput.files.length > 0)) {
                const dataToSend = {
                    'message': message,
                };

                if (fileInput.files.length > 0) {
                    const file = fileInput.files[0];
                    const reader = new FileReader();

                    reader.onloadend = function() {
                        dataToSend.file = reader.result; // base64 encoded file
                        dataToSend.filename = file.name; // send filename

                        chatSocket.send(JSON.stringify(dataToSend));
                    };

                    reader.readAsDataURL(file); // Convert the file to base64
                } else {
                    chatSocket.send(JSON.stringify(dataToSend));
                }

                messageInputDom.value = '';
                fileInput.value = ''; // Clear file input
            }
        };

        document.querySelector('#chat-file-input').onchange = function(e) {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = function(event) {
                chatSocket.send(JSON.stringify({
                    'file': event.target.result,
                    'filename': file.name,
                }));
            };
            reader.readAsDataURL(file);
        };
        
    

        //emoji
        document.getElementById('emoji-button').onclick = function() {
        const emojiList = document.getElementById('emoji-list');
        emojiList.style.display = emojiList.style.display === 'none' ? 'block' : 'none';
        };

        const emojis = document.querySelectorAll('.emoji');
        emojis.forEach(emoji => {
            emoji.onclick = function() {
                const messageInput = document.querySelector('#chat-message-input');
                messageInput.value += emoji.getAttribute('data-emoji'); // افزودن اموجی به ورودی
                document.getElementById('emoji-list').style.display = 'none'; // بستن لیست اموجی‌ها
                messageInput.focus(); // فوکوس روی ورودی
            };
        });
        //emoji


        // اضافه کردن event listener به نام کاربری
        document.querySelectorAll('#member-list .list-group-item').forEach(item => {
            item.onclick = function() {
                const link = this.querySelector('.user-link').href; // دریافت URL چت خصوصی
                window.location.href = link; // هدایت به چت خصوصی
            };
        });


        console.log("ta injas");
        // برای دریافت پیام‌ها از WebSocket اعلان
        notificationSocket.onmessage = function(e) {
            const notificationData = JSON.parse(e.data);
            // console.log("Notification received:", notificationData); // نمایش اطلاعات دریافت شده

            // بررسی نوع اعلان و پردازش آن
            if (notificationData.test === 'pv') {
                console.log("New notification:", notificationData); // اطلاعات اعلان جدید را در کنسول نمایش دهید
                // alert(پیام جدید از ${notificationData.sender}: ${notificationData.message});
                Swal.fire({
                    title: دعوت به چت خصوصی از طرف ${notificationData.sender},
                    text: "آیا می‌خواهید به چت خصوصی وارد شوید؟",
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonText: 'بله، وارد شوید',
                    cancelButtonText: 'خیر'
                }).then((result) => {
                    if (result.isConfirmed) {
                        // print(window.location.host)
                        // کاربر درخواست را تایید کرده و به صفحه چت خصوصی هدایت می‌شود
                        const chatUrl = '/cht/chat/private/'+ notificationData.sender +'/';

                        window.location.href = chatUrl;
                        
                    }
                });
            }
        };
       
    </script>
</body>
</html>