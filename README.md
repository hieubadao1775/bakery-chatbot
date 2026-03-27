# Backend API Guide - LangGraph Chatbot

## 1. Tong quan
Backend cung cap 1 endpoint de he thong khac goi vao chatbot.

- Endpoint: `POST /chat`
- Input JSON:
  - `user_id` (string)
  - `chat_session_id` (string)
  - `new_query` (string)
- Output JSON:
  - `answer` (string)

API duoc build bang FastAPI, goi LangGraph trong `chatbot.py`, va luu lich su chat vao SQLite theo cap:

- 1 `user_id`
- Nhieu `chat_session_id`

## 2. Cau truc file lien quan
- `api/main.py`: FastAPI app va endpoint `/chat`
- `chatbot.py`: LangGraph flow + `chat_once(...)`
- `databases/sqlite_db.py`: tao schema va luu lịch su hoi thoai
- `test.py`: client chat terminal de test API

## 3. Chuan bi moi truong
### 3.1 Tao virtual env (khuyen nghi)

```powershell
conda create -n env python=3.12 -y
```

### 3.2 Cai dependencies
```powershell
pip install -r requirements.txt
```

## 5. Chay API
Tu root project:

```powershell
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Kiem tra Swagger UI:
- http://127.0.0.1:8000/docs

## 6. Contract API chi tiet
### 6.1 Request
`POST http://127.0.0.1:8000/chat`

Header:
- `Content-Type: application/json`

Body:

```json
{
  "user_id": "user_001",
  "chat_session_id": "session_a1",
  "new_query": "Shop co banh sinh nhat cho 6 nguoi khong?"
}
```

Validation:
- Tat ca field la bat buoc
- Field khong duoc rong sau khi trim
- `user_id`, `chat_session_id`: max 128 ky tu
- `new_query`: max 4000 ky tu

### 6.2 Response thanh cong
HTTP 200

```json
{
  "answer": "..."
}
```

### 6.3 Response loi
- HTTP 422: payload sai schema/validation cua FastAPI
- HTTP 500: loi noi bo trong qua trinh goi model/DB

## 7. Vi du goi API
### 7.1 PowerShell
```powershell
$body = @{
  user_id = "user_001"
  chat_session_id = "session_a1"
  new_query = "Goi y giup minh 3 loai banh socola"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/chat" -ContentType "application/json" -Body $body
```

### 7.2 curl
```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_001","chat_session_id":"session_a1","new_query":"Cho minh xem banh best seller"}'
```

## 8. Test nhanh bang terminal chat
Sau khi API dang chay, mo terminal khac:

```powershell
python test.py
```

Tuy chon:

```powershell
python test.py --url http://127.0.0.1:8000/chat --user demo_user --session demo_session_01
```

Lenh trong chat terminal:
- `/new`: tao session moi
- `/exit`: thoat

## 9. Luu tru lich su chat
SQLite tao cac bang:
- `users`
- `chat_sessions`
- `messages`

Moi request `/chat` se:
1. Dam bao user/session ton tai
2. Luu message role `user`
3. Goi LangGraph
4. Luu message role `assistant`

Dong thoi LangGraph dung `thread_id = user_id:chat_session_id` de tach bo nho hoi thoai theo tung session.

