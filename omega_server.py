import asyncio
import os

MEMORY_FILE = "/data/data/com.termux/files/home/OMEGA_MEMORY/knowledge_base.txt"

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Příchozí spojení od {addr}")

    try:
        data = await reader.read(4096)
        message = data.decode('utf-8').strip()

        if message.startswith("MEMORIZE:"):
            content = message.split("MEMORIZE:")[1]
            os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
            await asyncio.to_thread(write_memory, content)
            response = "VZPOMINKA ULOZENA"
            writer.write(response.encode('utf-8'))

        elif message == "RECALL":
            if os.path.exists(MEMORY_FILE):
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()[-5:]
                response = "".join(lines)
            else:
                response = "PAMET PRAZDNA"
            writer.write(response.encode('utf-8'))

        await writer.drain()
    except Exception as e:
        print(f"Chyba: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

def write_memory(content):
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {content}\n")

async def main():
    server = await asyncio.start_server(handle_client, '0.0.0.0', 8888)
    print("OMEGA SERVER (Hermes) běží na portu 8888...")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
