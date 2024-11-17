# API Documentation

## 1. Create User Model from Token
**URL**: `https://dev3.nargil.co/cht/save-user-data/`

## 2. Create Public Group

**URL**: `https://dev3.nargil.co/cht/api/groups/create/`

**Request Body**:

```json
{
    "group_name": "arash",
    "slug": "arash",
    "type": "public"
}
**Response:**

json
{
    "id": "5a65eac5-11ec-4147-a3d5-63c1354f9d1e",
    "name": "arash",
    "slug": "arash",
    "created_by": "userCreator",
    "type": "public",
    "members_count": 1
}
```
## 3. Add Users to Group
**URL**: https://dev3.nargil.co/cht/api/group_chat/{GroupSlug}/

**Request Body**:

```json
{
    "add_member": true,
    "uuid": "5c4f39fb8cc04229813f0b2b367edcff"
}
```
***Response for Add:***

```json
{
    "message": "کاربر با نام firstname lastname به گروه arash اضافه شد.",
    "user": {
        "id": "5c4f39fb-8cc0-4229-813f-0b2b367edcff",
        "nationalcode": "2240175931",
        "first_name_fa": "firstname",
        "last_name_fa": "lastname",
        "usr_avatar": "https://demo.nargil.co/usr/base-user/file/3079f569e7cd4171a1de5ebc47fa52ec/"
    }
}
```
***Response for Remove:***

```json
{
    "message": "کاربر با کد ملی 2240175931 از گروه arash حذف شد."
}
```
## 4. See All Groups in which the User is a Member
**URL**: https://dev3.nargil.co/cht/api/groups/

## 5. Enter to Group
**URL**: https://dev3.nargil.co/cht/api/groups/Arash/chat/

Response:

```json
{
    "group": {
        "id": "36d42b76-0229-4f73-9b44-f1db4cd05a55",
        "name": "arash",
        "slug": "arash",
        "type": "public",
        "members": [
            {
                "id": "4a74eda0-474b-4467-8437-2ba9b9842235",
                "firstname": "firstname",
                "lastname": "lastname",
                "is_superuser": false,
                "avatar": null
            },
            {
                "id": "825fe339-0a5e-4af2-b98e-544822d3b6d5",
                "firstname": "firstname",
                "lastname": "firstname",
                "is_superuser": true,
                "avatar": "/cht/media/https%3A/demo.nargil.co/usr/base-user/file/3079f569e7cd4171a1de5ebc47fa52ec/"
            }
        ]
    },
    "messages": [
        {
            "id": "cc7b3293-b747-44ac-aa44-22a7e15539a9",
            "content": "",
            "timestamp": "2024-11-13T05:11:49.926952Z",
            "user": "11e794cc-44eb-4915-af02-524426a0bda1",
            "user_name": "firstname",
            "avatar": null,
            "group": "36d42b76-0229-4f73-9b44-f1db4cd05a55",
            "file": "/cht/media/static/files/578017"
        },
        {
            "id": "784fd636-6a14-420e-8db9-f79639b10a23",
            "content": "",
            "timestamp": "2024-11-13T05:12:00.582337Z",
            "user": "11e794cc-44eb-4915-af02-524426a0bda1",
            "user_name": "firstname",
            "avatar": null,
            "group": "36d42b76-0229-4f73-9b44-f1db4cd05a55",
            "file": "/cht/media/static/files/388233"
        }
    ],
    "all_users": [],
    "user_profile": {
        "id": "4a74eda0-474b-4467-8437-2ba9b9842235",
        "user": "11e794cc-44eb-4915-af02-524426a0bda1",
        "first_name": "firstname",
        "last_name": "firstname",
        "avatar": null,
        "is_superuser": false
    }
}
```
## 6. See All Users Information
**URL**: https://dev3.nargil.co/cht/api/users-info/

Response:

```json
{
    "all_users": [
        {
            "id": "825fe339-0a5e-4af2-b98e-544822d3b6d5",
            "firstname": "firstname",
            "lastname": "lastname",
            "avatar": "https://demo.nargil.co/usr/base-user/file/3079f569e7cd4171a1de5ebc47fa52ec/",
            "is_superuser": true,
            "groups": [
                {
                    "id": "36d42b76-0229-4f73-9b44-f1db4cd05a55",
                    "name": "arash",
                    "slug": "arash",
                    "type": "public"
                }
            ]
        },
        {
            "id": "4a74eda0-474b-4467-8437-2ba9b9842235",
            "firstname": "firstname",
            "lastname": "lastname",
            "avatar": "https://demo.nargil.co/usr/base-user/file/4a043f140bc94a3188158890f813c266/",
            "is_superuser": false,
            "groups": [
                {
                    "id": "36d42b76-0229-4f73-9b44-f1db4cd05a55",
                    "name": "arash",
                    "slug": "arash",
                    "type": "public"
                }
            ]
        }
    ]
}
```
## 7. User Profile
**URL**: https://dev3.nargil.co/cht/api/user/profile/

**Response:**

```json
{
    "message": "User Profile Found",
    "data": {
        "id": "4a74eda0-474b-4467-8437-2ba9b9842235",
        "user": "11e794cc-44eb-4915-af02-524426a0bda1",
        "first_name": "firstname",
        "last_name": "lastname",
        "avatar": null,
        "is_superuser": false
    }
}
```
***If Superuser, you can fetch all profiles:***

***Request Parameter: get-all=true***

**Response:**

```json
{
    "message": "All User Profiles Retrieved",
    "data": [
        {
            "id": "4a74eda0-474b-4467-8437-2ba9b9842235",
            "user": "11e794cc-44eb-4915-af02-524426a0bda1",
            "first_name": "firstname",
            "last_name": "lastname",
            "avatar": null,
            "is_superuser": false
        },
        {
            "id": "825fe339-0a5e-4af2-b98e-544822d3b6d5",
            "user": "5c4f39fb-8cc0-4229-813f-0b2b367edcff",
            "first_name": "firstname",
            "last_name": "lastname",
            "avatar": "/cht/media/https%3A/demo.nargil.co/usr/base-user/file/3079f569e7cd4171a1de5ebc47fa52ec/",
            "is_superuser": true
        }
    ]
}
```
## 8. Private Message
**URL**: https://dev3.nargil.co/cht/api/private-chat/{pv_group_name}/

**Response:**

```json
{
    "private_group": {
        "id": "df6ca747-e704-44b2-952d-0cb3af5d5973",
        "name": "private_chat_admin_user",
        "slug": "private_chat_admin_user",
        "members": [
            {
                "id": "11e794cc-44eb-4915-af02-524426a0bda1"
            },
            {
                "id": "5c4f39fb-8cc0-4229-813f-0b2b367edcff"
            }
        ]
    },
    "messages": [
        {
            "id": "fb973c98-c7c4-4f96-9d06-3782ac23a9fb",
            "content": "hello",
            "timestamp": "2024-11-13T06:42:22.734742Z",
            "user": "11e794cc-44eb-4915-af02-524426a0bda1",
            "user_name": "firstname",
            "avatar": null,
            "group": "df6ca747-e704-44b2-952d-0cb3af5d5973"
        }
    ]
}
```



# WebSocket Documentation

## Public Group WebSocket
**URL**: `wss://dev3.nargil.co/cht/ws/chat/arash/`

### Sending a Message
**Message Format**:
```json
{
    "message": "hello",
    "avatar_url": "/media/avatars/template_0_FZzDUpq.jpg",
    "timestamp": "2024-11-03 08:04:40"
}
```
**Sending a File**
***Message Format:***

```json
{
    "file": "Base64 Format Only",
    "filename": "filename",
    "avatar_url": "/media/avatars/template_0_FZzDUpq.jpg",
    "timestamp": "2024-11-03 08:04:40"
}
```
## Private Group WebSocket
**URL**: wss://dev3.nargil.co/cht/ws/private_chat/{private_chat_url}/

**Sending a Message**
***Message Format:***

```json
{
    "message": "Message of User",
    "recipient": "User UUID Only"
}
```
**Sending a File**
***Message Format:***

```json
{
    "file": "Base64 Format Only",
    "filename": "files",
    "recipient": "User UUID Only"
}
```