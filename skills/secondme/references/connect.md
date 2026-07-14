# 连接与登录

本文件负责登录、退出登录、重新登录、授权码交换和令牌持久化。

当用户说「登录小己」「登录 Second Me」「登入 second me」「login second me」「连上小己」，或索要登录授权地址时，立即进入登录流程；缺少凭据时直接提供浏览器授权地址。

全局产品介绍、安装成功文案和首次使用路线由 [SKILL.md](../SKILL.md) 统一负责。本文件不得重复展示功能清单；进入本文件后，只处理登录、退出、授权和登录后的必要衔接。

如果用户已经提出查看身份与形象、创建分身或搜索记忆等明确任务，不要再展示通用能力介绍。直接处理该请求；未登录时只完成继续该任务所必需的最小登录步骤。

## 退出与重新登录

当用户说「退出登录」「重新登录」「logout」「re-login」，或要求切换账号时：

1. 删除 `~/.secondme/credentials`。
2. 如果 `~/.openclaw/.credentials` 也存在，一并删除。
3. 丢弃本次对话中已读取的上一账号用户信息。
4. 告诉用户：`已退出登录，下次用的时候重新登录就行。`
5. 如果用户要求重新登录，继续执行下方登录流程。

## 登录流程

如果凭据缺失或无效，标记 `firstTimeLocalConnect = true`。

### 步骤一：生成 PKCE 参数

展示授权地址前，先在本地生成 PKCE 参数：

```bash
CODE_VERIFIER=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
CODE_CHALLENGE=$(printf '%s' "$CODE_VERIFIER" | openssl dgst -sha256 -binary | openssl base64 -A | tr '+/' '-_' | tr -d '=')
```

将 `CODE_VERIFIER` 保存在本地变量中，稍后交换令牌时还要使用。

### 步骤二：展示授权地址

让用户在浏览器中打开授权页面，并在地址后附加 `?challenge=<CODE_CHALLENGE>`。登录地址不得使用反引号、代码块或 Markdown 链接包装。

只输出原始地址，并让它单独占一行：

https://second-me.cn/auth/skills?challenge=<CODE_CHALLENGE>

告诉用户：

> 你还没有登录小己（Second Me），点这个链接登录一下：
>
> {auth page URL with challenge}
>
> 登录完把页面上的授权码发给我，格式像 lba_ac_xxxxxxxxxxxx。

注意：
- 该页面会先处理小己（Second Me）网页版的登录或注册。
- 登录后，页面会生成一个以 `lba_ac_` 开头的一次性授权码。
- 授权码有效期为 5 分钟，并且只能使用一次。
- 授权码与 PKCE challenge 绑定，只有原始 `code_verifier` 可以用它交换令牌。

到此停止，等待用户回复授权码。

## 用授权码换取令牌

当用户发来 `lba_ac_...` 时，运行：

```bash
curl -s -X POST {BASE}/api/auth/skills/token \
  -H "Content-Type: application/json" \
  -d "{\"code\": \"<lba_ac_...>\", \"codeVerifier\": \"$CODE_VERIFIER\"}"
```

规则：

- 确认 `response.code == 0`。
- 确认 `response.data.accessToken` 存在。
- `lba_at_...` 是后续所有小己（Second Me）流程使用的令牌。
- `codeVerifier` 必须与步骤一生成的 `CODE_VERIFIER` 一致。

成功后：

1. 如果 `~/.secondme/` 目录不存在，先创建该目录。
2. 写入 `~/.secondme/credentials`：
   ```json
   {
    "accessToken": "<data.accessToken>",
    "tokenType": "<data.tokenType>"
   }
   ```

登录成功后，先按 [SKILL.md 的用户信息读取与复用规则](../SKILL.md#用户信息读取与复用) 调用一次 `GET {BASE}/api/secondme/user/info`。这一步对所有登录入口都执行，不因用户已有明确任务而跳过。

Profile 初始化完成后，按以下规则交接：

- 如果登录只是某项明确请求的前置条件，读取用户信息时保持静默；告诉用户 `登录成功，token 已保存。`，然后立即继续原请求。
- 如果用户是从安装引导进入登录，或登录前没有其他明确任务，不要在本文件中继续设计首次使用引导，也不要单独发送登录成功消息。将 `firstTimeLocalConnect`、登录入口上下文和已读取的用户信息交给 [profile.md](profile.md#guided-profile-review)，由身份与形象流程输出第一条登录成功消息并继续引导。

完成上述交接后，本文件流程结束。
