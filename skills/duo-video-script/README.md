# workbuddy-skills

多多个人公司 WorkBuddy 自建 skills 同步仓库（private）。

## 已同步 skills
- `duo-video-script/` — 多多视频脚本生产技能（10 集生产包 / 分镜 / 四轨音频 / 独立叙事 / 全季结语）

## 三同步铁律（每次封 skill 都执行）
1. 更新 `~/.workbuddy/skills/<skill>/SKILL.md`
2. 镜像一份到 vault `99_Systems/Workflows/<skill>_SKILL.md`
3. 上传到本仓库（commit + push）

## 同步方法（Windows 侧）
- 凭证：vault `00_凭证_passwords.md` → `### github` 段（token，仅程序内使用，不打印）
- GitHub 账号 login = `faifaida`（注意不是 fayezang28）
- 仓库：`faifaida/workbuddy-skills`（private）
- 推送必须走代理 + OpenSSL：
  ```
  git config http.proxy http://127.0.0.1:7897
  git config https.proxy http://127.0.0.1:7897
  git config http.sslBackend openssl   # 关键：schannel 过代理会 TLS 握手失败
  git remote set-url origin https://<token>@github.com/faifaida/workbuddy-skills.git
  git add -A && git commit -m "..." && git push
  ```
