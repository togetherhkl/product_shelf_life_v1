# 基于微信小程序的产品保质期到期提醒系统

## 📖 项目简介

在快节奏的现代生活中，家庭囤积的食品、饮品、日用百货等商品日益增多，传统的人工管理方式难以实时掌握商品的保质期状态，极易造成资源浪费和潜在的健康隐患。

本项目是一款**基于微信小程序的产品保质期到期提醒系统**。通过扫码识别的方式，用户可以快速录入商品信息。系统会自动记录生产日期和到期日期，并在商品临期前通过小程序进行提醒，实现产品保质期的智能化、便捷化管理。

### 系统组成
本系统主要由微信小程序客户端、后台管理端以及后端服务接口组成。

![系统组成](./image/系统组成.png)

---

## 🛠 技术架构

系统采用前后端分离的架构设计，各模块职责明确、低耦合高内聚。

### 系统整体架构
![系统架构](./image/系统架构.png)

### 后端架构
后端采用 Python 的 FastAPI 框架，利用其高性能异步特性处理并发请求。架构上分为路由层、服务层、CRUD层、模型层等，层次分明。

![后端分层架构图](./image/后端分层架构图.png)
![后台架构](./image/后台架构.png)

*   **RESTful API**: 提供标准的HTTP接口供前端调用。
*   **MySQL**: 存储用户、商品、分类、扫码记录等核心业务数据。
*   **SQLAlchemy**: 作为ORM工具，简化数据库操作。

### 小程序架构
小程序端基于 `uni-app` 开发，实现跨平台部署（主要针对微信小程序），采用 Vue3 语法，结合组件化开发思想。

![小程序架构图](./image/小程序架构图.png)

---

## 📱 小程序功能展示

小程序作为用户使用的主要入口，提供了便捷的扫码、查询和提醒功能。

### 1. 首页与导航
首页展示各类商品的统计信息及快捷入口。
![小程序界面(首页)](./image/小程序界面(首页).png)

### 2. 扫码录入
通过调用手机摄像头扫描商品条形码，快速识别并录入商品信息，用户仅需补充生产日期等少量信息。
![小程序界面(商品扫码)](./image/小程序界面(商品扫码).png)

### 3. 商品详情与完善信息
展示商品的详细信息，包括保质期状态。用户可对录入的信息进行编辑和完善。
![小程序界面(商品详情)](./image/小程序界面(商品详情).png)
![小程序界面(完善信息)](./image/小程序界面(完善信息).png)

### 4. 扫码记录
查看历史扫码记录，方便用户追溯和管理已录入的商品。
![小程序界面(扫码记录)](./image/小程序界面(扫码记录).png)

---

## 💻 后台管理系统展示

后台管理系统面向管理员，用于维护基础数据、管理用户及查看系统运行状态。

### 1. 用户管理
管理员可以查看注册用户列表，进行用户信息的维护和管理。
![后台界面(用户管理)](./image/后台界面(用户管理).png)

### 2. 产品管理
对系统中的产品基础库进行管理，确保扫码识别的准确性。
![后台界面(产品管理)](./image/后台界面(产品管理).png)

### 3. 分类管理
管理商品的分类信息，便于用户筛选和查找。
![后台界面(分类管理)](./image/后台界面(分类管理).png)

### 4. 管理员管理
系统管理员账号的创建与权限分配。
![后台界面(管理员管理）](./image/后台界面(管理员管理）.png)

---

## 💾 数据设计

### E-R图 (实体关系图)
系统核心实体包括用户、商品、分类、扫码记录等，它们之间的关系如下所示：
![数据库E-R图](./image/数据库E-R图.drawio.png)

### 数据流向
展示了数据在小程序、后端服务及数据库之间的流转过程。
![数据流向](./image/数据流向.png)

---

## 📂 目录结构说明

```text
code/
├── backend/          # 后端服务代码 (FastAPI)
│   ├── app/
│   │   ├── routers/      # 路由层 (API接口定义)
│   │   ├── services/     # 业务逻辑层
│   │   ├── crud/         # 数据库操作层
│   │   ├── models/       # 数据库模型 (ORM)
│   │   ├── schemas/      # Pydantic模型 (数据校验)
│   │   └── utils/        # 工具函数
│   └── main.py           # 程序入口
├── frontend/         # 小程序端代码 (uni-app + Vue3)
├── v3-admin-vite/    # 后台管理端代码 (Vue3 + Element Plus + TypeScript)
└── image/            # 项目设计文档与截图
```

---

## 🚀 项目部署

### 1. 后端部署 (Backend)

后端采用 Python FastAPI 框架，依赖 MySQL 数据库。

**前提条件：**
*   Python 3.8+
*   MySQL 5.7+

**步骤：**

1.  **创建数据库**：
    在 MySQL 中创建一个新的数据库（例如 `hamu_db`）。

2.  **配置环境变量**：
    在 `backend` 目录下，配置 `.env` 文件（或修改 `core/settings.py`），设置数据库连接信息。
    ```ini
    # .env 示例
    #jwt相关密钥
    SECRET_KEY = "e83edb67616fcd746102adfa59739271707d39b9ac9c46fa8fb8e27e04764938"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = "10080" # 7天
    #数据库相关连接
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/hamu_db?charset=utf8mb4"
    #前端首页地址
    FRONTEND_URL = "http://localhost:5173/"
    #后端跨域地址
    BACKEND_CORS_ORIGINS = "http://localhost:5173, http://localhost:8000"
    #项目名称:产品保质期
    PROJECT_NAME = "product_shelf_life"

    #微信小程序相关配置
    WX_APPID = "your_appid_here"
    WX_SECRET = "your_secret_here"
    ```

3.  **安装依赖**：
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

4.  **数据库迁移**：
    使用 Alembic 初始化数据库表结构。
    ```bash
    alembic upgrade head
    ```

5.  **启动服务**：
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    启动后，API 文档访问地址：`http://localhost:8000/docs`

### 2. 小程序部署 (Frontend)

小程序端基于 uni-app 开发，需配合微信开发者工具使用。

**前提条件：**
*   Node.js 16+
*   微信开发者工具

**步骤：**

1.  **安装依赖**：
    ```bash
    cd frontend
    npm install
    # 或者使用 pnpm
    pnpm install
    ```

2.  **运行开发环境**：
    ```bash
    npm run dev:mp-weixin
    ```
    运行成功后，会在 `dist/dev/mp-weixin` 目录下生成编译后的文件。

3.  **导入微信开发者工具**：
    打开微信开发者工具 -> 导入项目 -> 选择 `frontend/dist/dev/mp-weixin` 目录。
    *注意：需修改 `manifest.json` 中的微信小程序 AppID。*

**参考资料:**
*   [使用VSCode搭建UniApp + TS + Vue3 + Vite项目 - 牛初九 - 博客园](https://www.cnblogs.com/boboooo/p/18407383)
*   [uniapp项目实践第二章：使用vscode开发uniapp项目-腾讯云开发者社区-腾讯云](https://cloud.tencent.com/developer/article/2490072)

### 3. 后台管理系统部署 (Web Admin)

后台管理端基于 Vue3 + Vite + Element Plus。

**前提条件：**
*   Node.js 16+
*   pnpm (推荐)

**步骤：**

1.  **安装依赖**：
    ```bash
    cd v3-admin-vite
    pnpm install
    ```

2.  **运行开发环境**：
    ```bash
    pnpm dev
    ```
    启动后，访问地址通常为 `http://localhost:3333` (具体端口见控制台输出)。

3.  **构建生产环境**：
    ```bash
    pnpm build
    ```
    构建完成后，生成的 `dist` 目录可部署到 Nginx 或其他静态文件服务器。
