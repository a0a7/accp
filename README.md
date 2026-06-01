# Acoustic Context Consensus Protocol (ACCP)

Offline context agreement from ambient audio.

## Features
- 5-second ambient capture (mono 16kHz)
- Spectral fingerprint extraction + hash-chain exchange
- Ambient timestamp from three loud transients
- Three-round lightweight gossip consensus over UDP broadcast
- Optional custom GUI (`gui.py`) with five stylized screens

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run CLI prototype
```bash
python -m acoustic_consensus.main
```
Prints a 32-bit context ID (`00000000` means no usable context).

For multi-device LAN demos, set `ACCP_LISTEN_IP=0.0.0.0` (loopback is the default for safer local-only behavior).

## Run GUI prototype
```bash
python gui.py
```
Screens:
1. Listening start screen
2. Recording/feature extraction visualization
3. Consensus rounds visualization
4. Result screen with stylized context ID
5. Morph transition animation between screens

## Run tests
```bash
pytest -q
```

## Two-device demo (isolated subnet)
1. Connect both devices to the same isolated LAN/Wi‑Fi.
2. Start the app on both within a few seconds.
3. Compare printed context IDs.

## Switching to acoustic modem
Replace `UDPBroadcastChannel` in `acoustic_consensus/network.py` with an audio-modem transport that sends the same message schema (`type`, `data`, `timestamp`, `device_id`).

## Patent status workflow files
See `/patent` for provisional/design draft artifacts and prior-art notes.
