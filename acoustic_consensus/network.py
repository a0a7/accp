from __future__ import annotations

import base64
import json
import socket
from typing import Any


def _encode_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"__bytes__": base64.b64encode(value).decode("ascii")}
    if isinstance(value, list):
        return [_encode_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _encode_value(item) for key, item in value.items()}
    return value


def _decode_value(value: Any) -> Any:
    if isinstance(value, dict):
        if "__bytes__" in value:
            return base64.b64decode(value["__bytes__"].encode("ascii"))
        return {key: _decode_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_decode_value(item) for item in value]
    return value


class UDPBroadcastChannel:
    """Small UDP broadcast abstraction for isolated local prototypes."""

    def __init__(self, port: int = 12345, broadcast_ip: str = "255.255.255.255", listen_ip: str = "127.0.0.1") -> None:
        self.port = port
        self.broadcast_ip = broadcast_ip
        self.listen_ip = listen_ip
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.listen_ip, port))
        self.sock.settimeout(0.25)

    def send(self, message: dict[str, Any]) -> None:
        payload = json.dumps(_encode_value(message), separators=(",", ":")).encode("utf-8")
        self.sock.sendto(payload, (self.broadcast_ip, self.port))

    def recv(self) -> dict[str, Any] | None:
        try:
            payload, _ = self.sock.recvfrom(65535)
        except socket.timeout:
            return None
        return _decode_value(json.loads(payload.decode("utf-8")))

    def close(self) -> None:
        self.sock.close()
