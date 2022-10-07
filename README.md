# Engine Patcher
🎞️ SMM:WE localization &amp; server patch

#### Usage

##### To patch SMM:WE for PC

- Use `patch.py` to replace strings (It's Chinese, you may need a translator)

- Use `patch_server_ip.sh <SMM_WE_EngineTribe_XX.exe>` to replace game server's IP

- Use `package_pc.sh` to package PC patch

##### To patch SMM:WE for Android

- Extract `libyoyo.so` from game

- Use `patch.py` to replace strings (It's Chinese, you may need a translator)

- Use `patch_server_ip.sh <libyoyo.so>` to replace game server's IP

- Sign the apk which replaced `libyoyo.so` yourself
