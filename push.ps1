# 一键把本目录推到你的 GitHub，并打印最终可用的订阅地址
# 用法：  pwsh -File push.ps1                      （仓库名默认 tvbox）
#         pwsh -File push.ps1 -RepoName mybox    （自定义仓库名）

param(
    [string]$RepoName = "tvbox",
    [switch]$Private
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "未找到 gh CLI，请先安装：winget install --id GitHub.cli -e"
}

# 1) 登录检查
gh auth status 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "尚未登录 GitHub，正在启动交互式登录..." -ForegroundColor Yellow
    gh auth login -h github.com -p https -w
}

$user = gh api user --jq .login
Write-Host "已登录：$user" -ForegroundColor Green

# 2) 初始化本地仓库
if (-not (Test-Path .git)) { git init | Out-Null }
git add -A
git -c user.name="$user" -c user.email="$user@users.noreply.github.com" commit -m "init: tvbox multi-repo (verified)" 2>$null | Out-Null
git branch -M main

# 3) 建仓并推送
$visibility = if ($Private) { "--private" } else { "--public" }
gh repo view "$user/$RepoName" 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    git remote remove origin 2>$null | Out-Null
    git remote add origin "https://github.com/$user/$RepoName.git"
    git push -u origin main --force
} else {
    gh repo create "$RepoName" $visibility --source . --remote origin --push --description "TVBox 多仓订阅（自建·探活·固定入口）"
}

# 4) 打印地址
Write-Host ""
Write-Host "================ 导入地址 ================" -ForegroundColor Cyan
Write-Host "全量     : https://cdn.jsdelivr.net/gh/$user/$RepoName@main/tvbox.json"
Write-Host "国内优先 : https://cdn.jsdelivr.net/gh/$user/$RepoName@main/tvbox-lite.json"
Write-Host "极简     : https://cdn.jsdelivr.net/gh/$user/$RepoName@main/tvbox-mini.json"
Write-Host "直链备用 : https://raw.githubusercontent.com/$user/$RepoName/main/tvbox.json"
Write-Host "镜像备用 : https://gh-proxy.com/https://raw.githubusercontent.com/$user/$RepoName/main/tvbox.json"
Write-Host "=========================================" -ForegroundColor Cyan

if ($Private) {
    Write-Warning "私有仓库的 raw 地址需要 token 鉴权，TVBox 无法直接拉取；要当订阅用请用公开仓库。"
}
