# Solo Companion — Install

Paste the prompt below into a new Cursor conversation. Claude will handle the full setup — no terminal commands needed.

---

## Prerequisites

- macOS (Apple Silicon or Intel)
- Python 3 installed (`python3 --version` should work)
- Git installed
- Access to the `scoots31/engineering-playbook` and `scoots31/solo-companion` GitHub repos

---

## Install Prompt

Copy everything between the lines and paste it into Cursor:

---

```
Set up the Solo Companion app on this machine. Work through each step in order, run all terminal commands directly, and confirm each step before moving to the next.

Step 1 — Clone the framework playbook
Check if ~/Developer/engineering-playbook exists. If it does, skip this step. If not, clone it:
  git clone https://github.com/scoots31/engineering-playbook.git ~/Developer/engineering-playbook

Step 2 — Clone Solo Companion
Check if ~/Developer/Solo Companion exists. If it does, skip this step. If not, clone it:
  git clone https://github.com/scoots31/solo-companion.git ~/Developer/Solo\ Companion

Step 3 — Create Python venv
Create a virtual environment at ~/Developer/Solo Companion/.venv using python3. Then install Flask into it.
  cd ~/Developer/Solo\ Companion && python3 -m venv .venv && .venv/bin/pip install flask

Step 4 — Ask one question
Ask me: "What would you like to label this machine?" (Example: Dan's MacBook Pro)
Wait for my answer before continuing.

Step 5 — Write config.json
Generate a random 3-digit number for the universe ID (pick any number 100–999).
Write the following to ~/Developer/Solo Companion/config.json, filling in my machine label and the universe ID you generated:

{
  "framework_path": "~/Developer/engineering-playbook",
  "universe": "[GENERATED_UNIVERSE_ID]",
  "machine_label": "[MY_ANSWER_FROM_STEP_4]",
  "machine_id": "[MY_ANSWER_LOWERCASED_WITH_HYPHENS]",
  "push_api_key": "41b7b236f83a0f4ea7dcb82b3f10dd59795e2650cda2cfe3"
}

Step 6 — Create LaunchAgent plist
Get my actual home directory path using: echo $HOME
Write the following plist to ~/Library/LaunchAgents/com.solocompanion.plist, replacing [HOME] with my actual home directory path:

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
Run:
  launchctl unload ~/Library/LaunchAgents/com.solocompanion.plist 2>/dev/null; launchctl load ~/Library/LaunchAgents/com.solocompanion.plist

Step 8 — Confirm it started
Wait up to 15 seconds for http://localhost:8710 to respond. Check with:
  curl -s -o /dev/null -w "%{http_code}" http://localhost:8710

If it returns 200, open http://localhost:8710 in the browser.
If it does not respond, check the log: tail -20 ~/Developer/Solo\ Companion/companion.log

Setup is complete. Solo Companion is running at http://localhost:8710 and will auto-start on login.
The dashboard will be empty until you have a project with a backlog underway.
```

---

## After install

- Companion runs at **http://localhost:8710**
- Auto-starts on login
- To update: `cd ~/Developer/Solo\ Companion && git pull`
- Log file: `~/Developer/Solo Companion/companion.log`
