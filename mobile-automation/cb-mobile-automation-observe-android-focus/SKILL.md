---
name: cb-mobile-automation-observe-android-focus
description: Record the current focused window of an Android device/emulator at a fixed interval and produce a timestamped log, for diagnosing page-transition problems in mobile automation. Use when an Android automation run fails and you need to replay which page a submit/sign flow actually landed on, when back presses seem to mis-tap and return to a previous page, or when debugging white screens or app exits on the emulator.
---

# Android 前台窗口观察器

按固定间隔记录 Android 设备当前焦点窗口（`adb shell dumpsys window` 的
`mCurrentFocus`），输出带时间戳的窗口序列日志，用于回放“流程走到了哪一步”。

## 何时使用

- 编排/用例失败后，回看提交/签约前后完整窗口序列，定位实际跳到了哪个页面。
- 怀疑误触返回：观察焦点是否被切回上一页。
- 排查白屏/崩溃：焦点是否停在空 Activity 或退出 App。
- 验证“提交后短暂回退中间页、再进结果页”这类有在途请求的跳转。

## 启动观察器

在 `automation_android` 目录（含 `.venv`）执行项目内工具
`tools/observe_focus.py`；建议在跑编排/用例前先启动，另开终端或后台会话，
结束后再读日志：

```bash
export PATH=/Users/chenbin/Library/Android/sdk/platform-tools:$PATH
.venv/bin/python -m tools.observe_focus --duration 300 --echo
```

- `--interval` 采样间隔（默认 0.5s）；`--serial` 指定设备（默认
  `ANDROID_SERIAL` 或 `emulator-5554`）。
- `--duration 0` 持续到 Ctrl+C；`--echo` 同步打印到标准输出。
- 默认过滤桌面/状态栏/导航栏/输入法等噪声窗口；`--no-noise-filter` 关闭。
- 日志默认 `/tmp/observe_focus_<时间>.log`，`--log` 自定义路径。

## 解读日志

每行格式：`时间 mCurrentFocus=Window{<窗口hash> u0 <包名>/<Activity>}`。

- 窗口 hash 变化表示 Activity 重建（同页面新实例），可用于判断是否被
  “弹走再回来”。
- `mCurrentFocus=null` 常见于相册/弹窗过渡瞬间，属正常。
- ElePay 关键页面示例：
  - `EnterprisePayUserProtocolActivity`：e企交协议页
  - `SignEnterprisePayActivity`：签约/完善企业信息页
  - `EnterprisePaySignResultActivity`：签约结果页
  - `Main2Activity`：首页

## 与流程判断配合

- 点“协议同意/提交”后，App 可能先短暂回到底层中间页（约 1-3s，请求在途）
  再进结果页；流程判断不要一看到中间页就判失败，应先等 loading 消失
  （`common/loading.py` 的 `wait_for_loading_gone`），再判页面状态。
- 观察器日志能给出“中间页停留时长”，据此调整轮询的容忍窗口。
