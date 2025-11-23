# Codex Extension Troubleshooting Guide

Based on the console errors you're experiencing, here are the key issues and solutions:

## Key Errors Identified

1. **Authentication Error**: `[unauthenticated] Error` - Codex can't authenticate
2. **Missing View Container**: `no composite descriptor found for workbench.view.extension.codexViewContainer`
3. **Extension API Issues**: `openai.chatgpt` extension has API proposal errors

## Troubleshooting Steps

### Step 1: Clear Extension Cache and Re-authenticate

Since this happened after a Windows security update, authentication tokens may be corrupted:

1. **Open Cursor Command Palette** (Ctrl+Shift+P / Cmd+Shift+P)
2. Run: `Developer: Reload Window`
3. If that doesn't work, try: `Developer: Restart Extension Host`

### Step 2: Check Extension Installation

1. Open Extensions view (Ctrl+Shift+X)
2. Search for "Codex" or "OpenAI"
3. Check if the extension is:
   - Installed and enabled
   - Not showing any error badges
   - Up to date

### Step 3: Clear Authentication Data

The authentication error suggests tokens may be corrupted. Try:

1. **Sign out completely**:
   - Command Palette → `Codex: Sign Out` (if available)
   - Or: Settings → Search "codex" → Clear any stored credentials

2. **Clear Cursor's storage** (WSL2 location):
   ```bash
   # In WSL2 terminal
   rm -rf ~/.cursor-server/extensions/openai.chatgpt-*/
   rm -rf ~/.cursor-server/User/globalStorage/openai.chatgpt/
   ```

3. **Restart Cursor completely** (close all windows)

4. **Sign back in**:
   - Command Palette → `Codex: Sign In`
   - Or use the Codex panel to authenticate

### Step 4: Check Network/Firewall (Windows Security Update Issue)

Since this happened after a Windows security update, check:

1. **Windows Firewall**:
   - Check if Windows Defender Firewall is blocking Cursor
   - Add Cursor to allowed apps if needed

2. **WSL2 Network**:
   - Test connectivity: `curl https://api.openai.com` (should return 401, not timeout)
   - Check WSL2 networking: `ip addr show eth0`

3. **Proxy/VPN**:
   - If using VPN/proxy, ensure it's not blocking OpenAI API
   - Check Cursor settings for proxy configuration

### Step 5: Reinstall Extension

If the above doesn't work:

1. **Uninstall the extension**:
   - Extensions view → Find Codex/OpenAI extension → Uninstall

2. **Clear extension data**:
   ```bash
   # In WSL2
   rm -rf ~/.cursor-server/extensions/openai.chatgpt-*/
   rm -rf ~/.cursor-server/User/workspaceStorage/*/state.vscdb
   ```

3. **Reinstall**:
   - Extensions view → Search "Codex" → Install
   - Restart Cursor

### Step 6: Check Cursor Settings

1. Open Settings (Ctrl+,)
2. Search for "codex" or "openai"
3. Verify:
   - API endpoint is correct
   - No proxy settings blocking connections
   - Extension is enabled

### Step 7: Check Cursor Logs

1. **Open Developer Tools**: Help → Toggle Developer Tools
2. **Check Console** for new errors
3. **Check Output**: View → Output → Select "Codex" or "Extension Host"

### Step 8: WSL2-Specific Fixes

Since you're on WSL2, try:

1. **Restart WSL2**:
   ```bash
   # In Windows PowerShell (as admin)
   wsl --shutdown
   # Then restart Cursor
   ```

2. **Check WSL2 DNS**:
   ```bash
   # In WSL2
   cat /etc/resolv.conf
   # Should show valid DNS servers
   ```

3. **Test API connectivity from WSL2**:
   ```bash
   curl -v https://api.openai.com/v1/models
   ```

### Step 9: Alternative: Use Cursor's Built-in AI

If Codex extension continues to fail, Cursor has built-in AI features:
- Use `Ctrl+K` for inline edits
- Use `Ctrl+L` for chat
- These use Cursor's own AI service, not the extension

## Quick Fix Attempt

Try this sequence first (fastest):

1. **Command Palette** (Ctrl+Shift+P) → `Developer: Reload Window`
2. If still broken → **Command Palette** → `Codex: Sign Out` (if available)
3. **Close Cursor completely**
4. **Reopen Cursor**
5. **Sign back in** to Codex
6. **Test**: Ask "Are you there?" in Codex chat

## If Nothing Works

1. **Check Cursor version**: Help → About
   - Update to latest version if outdated
   
2. **Report to Cursor support** with:
   - The console errors you shared
   - Cursor version
   - OS version (Windows + WSL2)
   - When it stopped working (after security update)

3. **Temporary workaround**: Use Cursor's built-in AI (Ctrl+L) instead of Codex extension

## Additional Notes

- The error `no composite descriptor found for workbench.view.extension.codexViewContainer` suggests the extension UI isn't loading properly, which is likely a symptom of the authentication failure
- The `[unauthenticated] Error` is the root cause - once authentication is fixed, the view container should load
- Windows security updates can sometimes reset firewall rules or network permissions


