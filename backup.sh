#!/usr/bin/env bash
# 每天 08:00 由 cron 调用：把笔记 commit 并 push 到 GitHub。
# 手动执行：/home/jwdeng/Code/NJU_Notes/backup.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

# cron 的 PATH 很干净，显式补上常用路径
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
# 无人值守时不要卡在账号密码输入上（凭据走 gh 的 credential helper）
export GIT_TERMINAL_PROMPT=0
# 若某天必须走本地代理才能访问 GitHub，取消下面两行注释
# export https_proxy="http://127.0.0.1:7890"
# export http_proxy="http://127.0.0.1:7890"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
STAMP="$(date '+%F %T')"

echo "===== ${STAMP} 开始备份（分支 ${BRANCH}）====="

git add -A

if git diff --cached --quiet; then
    echo "没有改动，跳过提交与推送"
    exit 0
fi

git commit -m "backup: ${STAMP}"

if git push origin "$BRANCH"; then
    echo "已推送到 origin/${BRANCH}"
else
    echo "推送失败：本地已提交，但没推上去（检查 gh auth status 与网络）" >&2
    exit 1
fi
