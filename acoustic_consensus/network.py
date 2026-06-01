from __future__ import annotations

import pickle
import socket
from typing import Any


class UDPBroadcastChannel:
    """Small UDP broadcast abstraction for isolated local prototypes."""

    def __init__(self, port: int = 12345, broadcast_ip: str = "255.255.255.255") -> None:
        self.port = port
        self.broadcast_ip = broadcast_ip
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", port))
        self.sock.settimeout(0.25)

    def send(self, message: dict[str, Any]) -> None:
        self.sock.sendto(pickle.dumps(message), (self.broadcast_ip, self.port))

    def recv(self) -> dict[str, Any] | None:
        try:
            payload, _ = self.sock.recvfrom(65535)
        except socket.timeout:
            return None
        return pickle.loads(payload)

    def close(self) -> None:
        self.sock.close()
