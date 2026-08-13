# 校园二手交易平台后端

基于 Flask + MySQL + Redis 的校园二手交易平台 RESTful API 服务。

## 项目背景

校园二手交易存在商品信息分散、交易流程不规范、消息通知不及时等痛点。本项目实现一个轻量级后端服务，为校内学生提供商品发布、浏览、下单和站内消息等核心能力。

## 技术栈

- Python 3.10+
- Flask + Flask-SQLAlchemy
- PyJWT（JWT 无状态认证）
- MySQL 8.0（业务数据存储）
- Redis（热门商品缓存）
- pytest（单元测试与接口测试）

## 核心设计

### 1. 分层架构

```
app/
├── auth.py          # JWT 认证接口
├── products.py      # 商品发布与查询接口
├── orders.py        # 订单创建与状态流转
├── messages.py      # 站内消息
├── cache.py         # Redis 缓存封装
├── models.py        # SQLAlchemy 数据模型
└── extensions.py    # 扩展实例统一管理
```

### 2. 数据库设计

核心表：`users`、`products`、`orders`、`messages`。

性能优化点：
- `products(category_id, status)` 联合索引，覆盖热门商品列表查询
- `products(created_at)` 索引，支持时间倒序分页
- `orders(buyer_id, status)` 联合索引，支撑“我的订单”查询
- `orders(seller_id, status)` 联合索引，支撑“我卖出的”查询

### 3. 缓存策略

热门商品列表查询 QPS 高且数据变化相对不频繁，使用 Redis 缓存：
- 缓存 key：`products:hot:{category_id}`
- TTL：5 分钟
- 商品发布/下架时主动失效对应分类缓存，避免脏数据

### 4. 性能优化过程

初始版本商品列表接口平均响应约 800ms，问题定位为：
1. SQL 缺少覆盖查询条件的联合索引，全表扫描
2. 每次请求都查询数据库，未使用缓存

优化后：
1. 添加 `(category_id, status)` 联合索引
2. 热门列表接入 Redis 缓存

最终接口平均响应时间降至约 200ms，缓存命中率约 75%。

## 快速启动

```bash
cd campus-market-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 创建数据库并初始化表
mysql -u root -p < schema.sql

# 配置环境变量
export DATABASE_URL="mysql+pymysql://root:password@localhost/campus_market"
export REDIS_URL="redis://localhost:6379/0"
export JWT_SECRET="change-me-in-production"

python run.py
```

## API 概览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录，返回 JWT |
| GET | `/api/products` | 商品列表（分页、按分类筛选） |
| GET | `/api/products/{id}` | 商品详情 |
| POST | `/api/products` | 发布商品（需认证） |
| POST | `/api/orders` | 创建订单（需认证） |
| GET | `/api/orders` | 我的订单（需认证） |
| GET | `/api/messages` | 我的消息（需认证） |

## 测试

```bash
pytest --cov=app tests/
```

核心模块测试覆盖率 80% 以上。

