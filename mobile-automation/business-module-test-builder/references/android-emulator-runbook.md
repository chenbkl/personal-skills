# Android Emulator Runbook

Use this runbook when Android automation cannot reach the emulator, `adb devices` hangs or returns no usable device, mobile-MCP cannot list elements, or uiautomator2 cannot connect.

## Preferred Project Script

For this auto-test project, start or repair the Android emulator with:

```bash
cd /Users/chenbin/Desktop/code/iOS/auto_test/automation_android
tools/start_emulator.sh
```

The script defaults to `Pixel_9`. Override the AVD name with either:

```bash
tools/start_emulator.sh <AVD_NAME>
ANDROID_AVD_NAME=<AVD_NAME> tools/start_emulator.sh
```

## What The Script Must Do

- Use the Android SDK adb at `$HOME/Library/Android/sdk/platform-tools/adb`.
- Avoid relying on `which adb`, because Homebrew adb may be first in `PATH`.
- Clear only stale adb server processes listening on tcp:5037.
- Do not kill emulator or qemu processes during adb repair.
- Start the requested AVD only when it is not already running.
- Wait for `adb devices` to show `emulator-5554 device`.
- Wait for `sys.boot_completed=1`.
- Print the final device list and boot status before declaring the emulator ready.

## Manual Repair Checklist

When the project script is missing or fails, repair ADB in this order:

```bash
ADB="$HOME/Library/Android/sdk/platform-tools/adb"
lsof -nP -iTCP:5037 -sTCP:LISTEN
kill $(lsof -tiTCP:5037 -sTCP:LISTEN) 2>/dev/null || true
$ADB start-server
$ADB devices
$ADB -s emulator-5554 shell getprop sys.boot_completed
```

If `adb start-server` appears stuck, wait briefly before interrupting. It can still complete and print `daemon started successfully`.

## Version Conflict Rule

If both of these exist, prefer the SDK adb:

```text
$HOME/Library/Android/sdk/platform-tools/adb
/opt/homebrew/bin/adb
```

Do not uninstall or move Homebrew adb unless the user explicitly asks. Use the SDK adb by absolute path, or prepend platform-tools to `PATH` in the current shell:

```bash
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$ANDROID_HOME/platform-tools:$PATH"
```

## Ready Criteria

Android automation may start only after all checks pass:

```text
adb devices contains: emulator-5554 device
sys.boot_completed is: 1
```

If mobile-MCP or uiautomator2 still fails after these checks, debug that layer separately; do not keep restarting the emulator blindly.
