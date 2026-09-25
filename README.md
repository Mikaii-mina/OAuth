# OAuth 实验平台

本项目 fork 自 [`cyllective/oauth-labs`](https://github.com/cyllective/oauth-labs)，基于上游提交 `5c97e34c8f18ee64a85306037641b12c53b8137a`，使用 MIT 许可证，详见 `LICENSE`。当前保留 `lab00` 基线环境，并加入了实验脚手架、自动检查和 CI。暂未选定或实现具体漏洞。

## 环境要求

- Docker Desktop，包含 Docker Compose 和镜像构建功能
- Go 1.23.2 或更高版本，用于生成配置
- `server-00.oauth.labs` 和 `client-00.oauth.labs` 解析到 `127.0.0.1`

在 `/etc/hosts` 中加入以下内容，需要管理员权限：

```text
127.0.0.1 server-00.oauth.labs client-00.oauth.labs
```

本平台只能在可信本机环境运行。Caddy 只绑定本机回环地址。首次访问时可能看到本地 CA 证书警告；确认域名确实是本地实验域名后，再按需要信任该证书。

## 使用流程

尽管相同流程，Docker 数据卷、生成配置和实验账号都保存在各自电脑上，不会通过 GitHub 共享。

### 首次使用

安装并启动 Docker Desktop，安装 Go 1.23.2 或更高版本，配置 `/etc/hosts`，然后运行：

```sh
git clone https://github.com/Mikaii-mina/OAuth.git
cd OAuth
make config
make lab00
docker compose ps
make smoke
```

确认 `caddy`、`db`、`valkey`、`server-00` 和 `client-00` 都显示为 `Up` 后，打开：

- [server-00.oauth.labs](https://server-00.oauth.labs) 授权服务器：负责注册、登录、用户授权和签发授权码/令牌。首次使用可访问 [注册页面](https://server-00.oauth.labs/register)。
- [client-00.oauth.labs](https://client-00.oauth.labs) 客户端应用：发起 OAuth 登录，接收授权回调并使用令牌获取用户资料。

### 日常使用

启动 Docker Desktop 后，在仓库目录运行：

```sh
make lab00
docker compose ps
make smoke
```

确认所有服务为 `Up` 后，再打开客户端网页。使用完毕后运行：

```sh
make lab-down
```

该命令只停止服务，不删除本地数据库数据，下次可以直接运行 `make lab00`。

### 清空并重新初始化

如果需要从全新环境开始，运行：

```sh
make lab-reset
make config
make lab00
make smoke
```

`make lab-reset` 会删除本地数据库数据。不要单独运行 `make config`，因为它会重新生成数据库密码；如果旧数据库卷仍存在，新密码可能无法连接旧数据库。配置文件和凭据已被 Git 忽略，不要手动提交。

## 当前基线流程

`lab00` 是用于学习和观察 OAuth 授权码流程的基线环境，不代表完整安全实现。客户端使用 `state` 和 PKCE。

```text
浏览器 → client-00 /login
客户端 → server-00 /oauth/authorize
授权服务器 → client-00 /callback?code=...
客户端 → server-00 /oauth/token
客户端 → 资源接口获取用户资料
```

烟测会检查服务健康状态、授权 URL 中的 `state`、S256 PKCE 参数，以及错误 `state` 是否被拒绝。它不会执行完整的登录授权，也不能证明实现没有漏洞。

## 新增漏洞实验

保持 `lab00` 不变，将它作为参考基线。创建新实验，例如：

```sh
python3 scripts/new_lab.py 1
```

该命令会复制基线代码，增加对应的 Compose 服务和 Caddy 路由，并创建：

```text
lab01/scenario.json
lab01/README.md
lab01/reproduce.py
```

检查生成文件后，重新生成配置并启动实验：

```sh
make lab-reset
make config
make lab-up LAB=01
```

同时在 `/etc/hosts` 中加入：

```text
127.0.0.1 server-01.oauth.labs client-01.oauth.labs
```

完成实验实现后运行：

```sh
make lab-test LAB=01
make experiment LAB=01
```

每个实验必须只引入一个主要缺陷，并实现 `fixed` 与 `vulnerable` 两种版本。`reproduce.py --variant ...` 必须输出一个 JSON 对象，包含布尔字段：

```json
{
  "exploitable": true,
  "impact_verified": true
}
```

`make experiment LAB=01` 会依次启动两个版本，验证漏洞版可复现、修复版不可复现，并在每次运行前后删除 Compose 数据卷。生成的复现脚本默认是未完成占位符，在实现具体漏洞前不会运行。

## 常用命令

```sh
make lab00                  # 启动 lab00
make lab-up LAB=01          # 启动指定实验
make lab-test LAB=01        # 执行通用烟测
make lab-down               # 停止服务，保留数据
make lab-reset              # 停止服务并删除数据卷
make check                  # 执行 Python、Go 和配置检查
docker compose logs -f      # 查看所有服务日志
```
