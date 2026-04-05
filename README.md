# Flask JWT API

一个简单的 Flask REST API，包含用户注册、JWT 登录、受保护接口和健康检查。

## 功能

- `POST /register`：注册用户，使用内存用户库保存账号
- `POST /login`：登录并返回 JWT
- `GET /protected`：需要 `Authorization: Bearer <token>`
- `GET /health`：健康检查

## 安装依赖

```bash
pip3 install --break-system-packages -r requirements.txt
```

## 运行服务

```bash
python3 app.py
```

服务默认监听 `http://127.0.0.1:5000`。

## 运行测试

```bash
python3 -m pytest test_app.py -v
```

## 示例请求

注册：

```bash
curl -X POST http://127.0.0.1:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"wonderland"}'
```

登录：

```bash
curl -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"wonderland"}'
```

访问受保护接口：

```bash
curl http://127.0.0.1:5000/protected \
  -H "Authorization: Bearer <token>"
```
