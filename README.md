# Flask REST API with JWT Authentication

轻量级 Flask REST API，包含用户注册、登录和 JWT 认证。

## 功能

- ✅ 用户注册 (`POST /register`)
- ✅ 用户登录 (`POST /login`)
- ✅ 受保护接口 (`GET /protected`)
- ✅ 健康检查 (`GET /health`)
- ✅ JWT Token 认证

## 运行

```bash
pip install -r requirements.txt
python app.py
```

API 运行在 http://localhost:5000

## 测试

```bash
pytest test_app.py -v
```

## API 示例

### 注册
```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret123"}'
```

### 登录
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret123"}'
```

### 访问受保护接口
```bash
curl http://localhost:5000/protected \
  -H "Authorization: Bearer <your-token>"
```
