# 宝塔面板部署全流程（Linux）

本指南面向新手，一步步完成前端（Vue3）与后端（Spring Boot）部署，并连接 MySQL。

## 一、环境准备
- 登录宝塔面板（BT），确认服务器安全组与防火墙允许 80/443 端口访问。
- 安装必备软件：
  - Nginx（用于前端静态站点与反向代理）
  - MySQL（数据库）
  - Java 17（后端 Jar 运行，若无可安装 OpenJDK 17）
- 创建 MySQL 数据库：
  - 在「软件商店 → MySQL」或「数据库」中新建数据库，设置库名、用户、密码。
  - 记录：DB_HOST（通常为 127.0.0.1）、DB_PORT（3306）、DB_NAME、DB_USERNAME、DB_PASSWORD。
  - 通过「数据库管理/导入」功能导入 `db/migrations/V1__init.sql`。

## 二、部署后端（Spring Boot）
1) 构建 Jar（本地或 CI）：
- 本地安装 Maven，进入 `backend/` 目录执行：`mvn -q -DskipTests package`
- 产物：`backend/target/fanqie-backend-0.1.0.jar`
- 若本地不便构建，可使用 GitHub Actions（我可帮你配置）。

2) 上传与运行：
- 将 Jar 上传到服务器：例如 `/www/server/fanqie-backend/app.jar`
- 在宝塔面板创建「计划任务 → Shell 脚本」：启动命令如下（请替换数据库信息）：
```
nohup java -jar /www/server/fanqie-backend/app.jar \
  --DB_HOST=127.0.0.1 --DB_PORT=3306 \
  --DB_NAME=fanqie --DB_USERNAME=fanqie_user --DB_PASSWORD='强密码' \
  --server.port=8080 \
  > /www/server/fanqie-backend/app.log 2>&1 &
```
- 检查日志：`tail -f /www/server/fanqie-backend/app.log`，出现 `Started FanqieApplication` 且无报错即成功。
- 开机自启：将上述启动命令加入「计划任务（启动时）」或使用 `systemd` 创建服务。

3) 安全与维护：
- 后端端口仅本机访问（8080 不对外开放），对外通过 Nginx 反向代理。
- 定期查看日志与磁盘空间，避免日志过大：配置 logrotate 或按月清理。

## 三、部署前端（Vue3）
1) 构建前端：
- 进入 `frontend/` 执行：
```
npm install
npm run build
```
- 产物：`frontend/dist/` 目录。

2) 创建站点与上传：
- 在宝塔面板创建站点（域名或服务器 IP）。
- 站点根目录改为前端 `dist/` 上传位置，例如 `/www/wwwroot/fanqie-web/`。
- 将 `frontend/dist/` 内所有文件上传到站点根目录。

3) 配置 Nginx 反向代理后端 API：
- 在站点「设置 → 配置文件」中加入：
```
location /api/ {
  proxy_pass http://127.0.0.1:8080/api/;
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

# 前端单页应用回退到 index.html
location / {
  try_files $uri $uri/ /index.html;
}
```
- 保存并重载 Nginx。

4) HTTPS 与证书：
- 在站点中申请并开启 SSL（Let’s Encrypt），强制跳转到 HTTPS，提高安全性。

## 四、联调与验证
- 访问前端域名：`https://你的域名/`，应能打开首页。
- 健康检查：访问 `https://你的域名/api/health`，返回 `{"status":"ok"}` 即后端联通。
- 若接口 404，确认 Nginx 反代路径与后端 `@RequestMapping("/api")` 一致。

## 五、常见问题与排查
- 数据库连接失败：检查库名、用户、密码与本机访问权限；确认防火墙与 MySQL 绑定地址。
- 端口被占用：`ss -lntp | grep 8080` 查看占用进程，修改后端端口或释放端口。
- 页面刷新 404：确保 Nginx 配置 `try_files ... /index.html` 存在。
- 上传后权限问题：确认站点目录权限为 `www` 用户，或修复 `chmod -R 755`、`chown -R www:www`。

## 六、后续扩展建议
- 使用 CI/CD：前端与后端分别添加 GitHub Actions 构建与自动上传。
- 日志与监控：接入 ELK 或简易监控（如宝塔监控），便于定位问题。
- 数据库迁移工具：后续可接入 Flyway 或 Liquibase，规范化版本迁移。