# Hermes 双仓库同步指南

本文档用于说明这台机器与另一台机器在维护 `Hermes Agent` 和 `Hermes WebUI` 时的 Git 规则、远端角色与安全操作方式。目标是让人类开发者和 AI 助手都能快速接手，不重复踩历史分叉、软件更新覆盖和错误 force push 的坑。

## 适用范围

本机维护两套相关但独立的仓库：

1. `Hermes Agent`
2. `Hermes WebUI`

它们必须分别跟踪各自的官方上游，不能混用。

## 总原则

### 1. `origin` 永远指向个人 fork / 共享仓库

这是两台机器之间同步自定义改动的主入口。

### 2. `upstream` 永远指向官方源头仓库

这是吸收官方更新的唯一可信来源。

### 3. 两个仓库必须分别处理、分别验证

`Hermes Agent` 与 `Hermes WebUI` 的主分支名、测试入口、上游仓库都不同。不要把一个仓库的命令直接套到另一个仓库。

### 4. 优先使用 Git 同步，不要把软件内置 update 和源码定制混在同一个工作区

如果目录已经作为 Git 工作区维护，就优先通过 Git 同步。  
如果一个目录主要作为安装产物运行，就不要在上面做长期源码定制。

### 5. 任何历史重写前都先做备份

命名建议：

```text
backup/<用途>-YYYY-MM-DD
```

### 6. 默认使用 `--force-with-lease`，不要裸 `--force`

这样可以避免覆盖掉另一台机器刚推上去但本机还没拉到的提交。

## 仓库一：Hermes Agent

### 仓库身份

- 本地目录：`G:\Hermes Agent`
- 官方上游：`https://github.com/NousResearch/hermes-agent.git`
- 个人 fork：`https://github.com/fioer1/hermes-agent.git`
- 主分支：`main`

### 远端角色

```bash
origin   = https://github.com/fioer1/hermes-agent.git
upstream = https://github.com/NousResearch/hermes-agent.git
```

### 长期同步策略

- `main` 始终以 `upstream/main` 为基线
- 本地定制通过干净提交保留在 `main` 之上
- 需要吸收官方更新时，优先 `rebase upstream/main`
- 只有在历史已经乱掉时，才新建清理分支并 `cherry-pick`

### 日常更新方式

```bash
git fetch upstream origin
git checkout main
git rebase upstream/main
git push --force-with-lease origin main
```

### 最小检查清单

```bash
git remote -v
git status --short --branch
git rev-list --left-right --count upstream/main...main
git rev-list --left-right --count origin/main...main
```

理想状态：

- `upstream/main...main` 只显示 `main` 领先若干个“你自己的有效提交”
- 不应该出现长期 `behind` 官方主线的状态
- `origin/main...main` 正常情况下应为 `0 0`

### 测试入口

优先使用仓库自己的测试包装脚本：

```bash
scripts/run_tests.sh
```

如果当前环境无法直接使用该脚本，再退回到虚拟环境里的 `pytest`，并至少覆盖本次改动相关测试。

## 仓库二：Hermes WebUI

### 仓库身份

- 本地目录：`G:\hermes-webui`
- 官方上游：`https://github.com/nesquena/hermes-webui.git`
- 个人 fork：`https://github.com/fioer1/hermes-webui.git`
- 主分支：`master`

### 远端角色

```bash
origin   = https://github.com/fioer1/hermes-webui.git
upstream = https://github.com/nesquena/hermes-webui.git
```

### 长期同步策略

- `master` 始终建立在 `upstream/master` 之上
- 个人改动保留为少量清晰提交
- 另一台机器需要同步时，优先对齐 `origin/master`

### 日常更新方式

```bash
git fetch upstream origin
git checkout master
git rebase upstream/master
git push --force-with-lease origin master
```

### 另一台机器同步方式

如果另一台机器没有本地未提交改动，直接对齐共享远端：

```bash
git fetch origin
git checkout master
git reset --hard origin/master
```

如果另一台机器有本地改动：

1. 先提交或备份
2. 再执行 `reset --hard`

不要在断开历史和新历史之间尝试自动 merge。

### 最小验证

至少运行这组回归测试：

```bash
python -m pytest tests/test_updates.py tests/test_pwa_manifest_sw.py tests/test_auto_title_setting.py tests/test_perf_fast_ui.py tests/test_prompt_cache_toggle.py -q
```

## 双机协作约定

### 1. 先判断，再更新

默认假设另一台机器可能落后。涉及同步时，先运行：

```bash
git remote -v
git status --short --branch
git rev-list --left-right --count origin/<branch>...HEAD
git rev-list --left-right --count upstream/<branch>...HEAD
```

### 2. 没确认历史关系之前，不要直接 `git pull`

`pull` 会把 fetch 和 merge/rebase 混在一起，容易在脏现场里做出错误决定。

### 3. 文档优先更新到仓库

如果同步策略、目录命名、远端角色发生变化，先更新本文档和对应仓库的 `AGENTS.md`，再做大规模历史整理。这样另一台机器上的 AI 才能看懂现场。

## 给 AI 助手的直接指令

如果你是另一个会话中的 AI 助手，处理这两个仓库时请遵循以下顺序：

1. 先读当前仓库根目录下的 `SYNC_WORKFLOW.md`
2. 再读当前仓库根目录下的 `AGENTS.md`
3. 运行：

```bash
git remote -v
git status --short --branch
```

4. 如果涉及同步，再运行：

```bash
git rev-list --left-right --count origin/<branch>...HEAD
git rev-list --left-right --count upstream/<branch>...HEAD
```

5. 没有确认历史关系之前，不要直接 `pull`
6. 没有备份分支之前，不要直接重写历史

## 最后更新

- 更新时间：2026-04-29
- 更新人：OpenAI Codex
