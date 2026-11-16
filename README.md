# TVBox 固定多仓入口

自建、自验活的 TVBox / FongMi / 影视仓 多仓订阅。**入口地址固定不变**，上游删库也不影响你用。

本仓库只做「聚合 + 探活 + 索引」，不存储、不提供任何音视频内容，全部地址来自互联网公开分享。

## 一、导入地址（三选一）

| 版本 | 地址 | 说明 |
|---|---|---|
| **全量** | `https://cdn.jsdelivr.net/gh/afan-fan/tvbox@main/tvbox.json` | 48 个实测存活单仓，资源最全 |
| **国内优先** | `https://cdn.jsdelivr.net/gh/afan-fan/tvbox@main/tvbox-lite.json` | 16 条不含 raw.githubusercontent 直链，国内加载快 |
| **极简** | `https://cdn.jsdelivr.net/gh/afan-fan/tvbox@main/tvbox-mini.json` | 8 条，低配盒子 / 老人机首选 |

把 `afan-fan/tvbox` 换成你自己的账号和仓库名（push 脚本会自动打印真实地址）。

备用前缀（jsDelivr 不通时换任意一条，内容完全一样）：

```
https://raw.githubusercontent.com/afan-fan/tvbox/main/tvbox.json
https://gh-proxy.com/https://raw.githubusercontent.com/afan-fan/tvbox/main/tvbox.json
https://ghfast.top/https://raw.githubusercontent.com/afan-fan/tvbox/main/tvbox.json
https://ghproxy.net/https://raw.githubusercontent.com/afan-fan/tvbox/main/tvbox.json
```

## 二、导入步骤

**影视仓 / TVBox**
1. 设置 → 配置地址（接口地址）
2. 粘贴上面的地址 → 确定（影视仓请选「多仓」模式）
3. 回首页下拉，出现仓库列表，点一个加载

**FongMi（蜂蜜）**
1. 右上角 设置 ⚙️ → 点播
2. 粘贴地址 → 确定

某个仓当天挂了就在列表里换另一个 —— 这就是多仓的意义。

## 三、目录

```
tvbox.json        全量多仓（48 条，机器验活）
tvbox-lite.json   国内优先（16 条）
tvbox-mini.json   极简（8 条）
STATUS.md         最近一次探活结果明细
tools/check.py    探活脚本（纯标准库）
.github/workflows/check.yml  每天自动跑一次探活并提交
```

## 四、自动保鲜

仓库自带 GitHub Actions：每天北京时间 04:00 重新探测所有单仓，
把返回 HTML / 404 / 超时的条目从 `tvbox.json` 里剔除，并把结果写进 `STATUS.md`。

手动触发：Actions → check → Run workflow。

本地手动跑：

```bash
python tools/check.py
```

## 五、加自己的源

编辑 `tvbox.json`，在 `urls` 数组里加一行：

```json
{ "name": "我的源", "url": "https://example.com/tv.json" }
```

推上去，jsDelivr 几秒后自动生效，入口地址不用改。

⚠️ jsDelivr 缓存约 12 小时，刚改完想立刻看到效果，先用 `raw.githubusercontent.com` 那条地址。

## 六、说明

- 所有接口均来自互联网公开分享，版权归各原始权利人所有，仅供个人学习与技术研究。
- 接口随时可能被上游改动或关停，可用性以 `STATUS.md` 的最近一次探活结果为准。
- 请勿用于商业用途或传播。
