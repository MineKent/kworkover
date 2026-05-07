from __future__ import annotations

import asyncio


async def run_healthcheck_server(port: int) -> None:
    server = await asyncio.start_server(_handle_connection, host="0.0.0.0", port=port)
    async with server:
        await server.serve_forever()


async def _handle_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        data = await reader.read(2048)
        request_line = data.split(b"\r\n", 1)[0].decode("ascii", errors="ignore")
        path = "/"
        parts = request_line.split()
        if len(parts) >= 2:
            path = parts[1]

        if path in {"/", "/health"}:
            body = b"ok"
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/plain; charset=utf-8\r\n"
                b"Content-Length: 2\r\n"
                b"Connection: close\r\n\r\n"
                + body
            )
        else:
            body = b"not found"
            response = (
                b"HTTP/1.1 404 Not Found\r\n"
                b"Content-Type: text/plain; charset=utf-8\r\n"
                b"Content-Length: 9\r\n"
                b"Connection: close\r\n\r\n"
                + body
            )

        writer.write(response)
        await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()
