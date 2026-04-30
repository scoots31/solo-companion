# Solo Companion — Install & Update

Paste the prompt below into a new Cursor conversation. Claude will handle everything — no terminal commands needed.

---

## Prerequisites

- macOS (Apple Silicon or Intel)
- Python 3 installed (`python3 --version` should work)
- Git installed
- `~/Developer/engineering-playbook` already cloned on this machine

---

## Install Prompt

Copy everything between the triple-backtick lines and paste into Cursor:

---

```
Set up Solo Companion on this machine. Run all terminal commands directly — do not paste them for me to run. Confirm each step before moving to the next.

Step 1 — Update the framework playbook
Run: git -C ~/Developer/engineering-playbook pull
Report what git says (already up to date, or what changed).

Step 2 — Clone Solo Companion
Check if ~/Developer/Solo Companion exists.
If it does: run git -C ~/Developer/Solo\ Companion pull and report what git says.
If it does not: run git clone https://github.com/scoots31/solo-companion.git ~/Developer/Solo\ Companion

Step 3 — Create Python venv and install Flask
Check if ~/Developer/Solo Companion/.venv exists.
If it does not: run python3 -m venv ~/Developer/Solo\ Companion/.venv
Then run: ~/Developer/Solo\ Companion/.venv/bin/pip install flask

Step 4 — Ask one question
Ask me: "What would you like to label this machine?" (Example: Scott's Work MacBook)
Wait for my answer before continuing.

Step 5 — Write config.json
Check if ~/Developer/Solo Companion/config.json already exists.
If it does not: generate a random 3-digit number for the universe ID (any number 100–999), then write the file below to ~/Developer/Solo Companion/config.json — fill in my machine label from Step 4 and the universe ID you generated:

{
  "framework_path": "~/Developer/engineering-playbook",
  "universe": "[GENERATED_UNIVERSE_ID]",
  "machine_label": "[MY_ANSWER_FROM_STEP_4]",
  "machine_id": "[MY_ANSWER_LOWERCASED_SPACES_AS_HYPHENS]",
  "push_api_key": "41b7b236f83a0f4ea7dcb82b3f10dd59795e2650cda2cfe3"
}

If config.json already exists: show me its current contents and skip writing it.

Step 6 — Create LaunchAgent plist
Get my actual home directory: run echo $HOME and use that value.
Write the following to ~/Library/LaunchAgents/com.solocompanion.plist, replacing [HOME] with my actual home path:

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.solocompanion</string>
    <key>ProgramArguments</key>
    <array>
        <string>[HOME]/Developer/Solo Companion/.venv/bin/python3</string>
        <string>[HOME]/Developer/Solo Companion/app.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>[HOME]/Developer/Solo Companion/companion.log</string>
    <key>StandardErrorPath</key>
    <string>[HOME]/Developer/Solo Companion/companion.log</string>
</dict>
</plist>

Step 7 — Load the LaunchAgent
Run: launchctl unload ~/Library/LaunchAgents/com.solocompanion.plist 2>/dev/null; launchctl load ~/Library/LaunchAgents/com.solocompanion.plist

Step 8 — Confirm it started
Poll http://localhost:8710 for up to 15 seconds.
Run: curl -s -o /dev/null -w "%{http_code}" http://localhost:8710
If it returns 200: open http://localhost:8710 in the browser and tell me setup is complete.
If it does not respond after 15 seconds: show me the last 20 lines of ~/Developer/Solo\ Companion/companion.log so we can diagnose.
```

---

## After install

- Companion runs at **http://localhost:8710** and auto-starts on login
- To update later: paste the same prompt — it will pull the latest and skip steps already done
- Log file: `~/Developer/Solo Companion/companion.log`
