import asyncio
import time
from multiprocessing import Process
from random import random, randint

import httpx

COUNT_DEVICE = 190
COUNT_PROCESSES = 5
URL = 'http://127.0.0.1:8001/receiver/telemetry/'
API_KEYS: dict[str, str] = {
    'sensor-01': '1w6l9qySxLsYdmd7xGwu_DB2nYGCYvTJoOI88dU4LIM',
    'sensor-02': '99TUC2gdYV9HEgc2e8HQCE-A4fviiiOJMzNWcn86RjA',
    'sensor-03': 'K8509WzcydFdbCnzW2NMC7Q5wU15lx2Bv3kNrZQSGEE',
    'sensor-04': '2aV697KbdYlpqG8vZJA1sFNotg3Ku8p-22G5YIYt36A',
    'sensor-05': 'KXMTUGsPH7UTAeRIQ-UExWn0qWAzQpP9cp7odMS5MtY',
    'sensor-06': 'Xk8VdJWLzZE8YdAaHcHB1kTD6JYzHr7FPVo515pl8gM',
    'sensor-07': 'eC1jp-hGvag65NYsh5-BHwe0HoRIAkZSMwGQ-jcUot0',
    'sensor-08': 'F8amNYH6_1tTv3zox2F1BzSOBpov87lNv5VkhDUkC3c',
    'sensor-09': 'ltqrd1SHxPAtiOGEHlPUkoPiiyC-P1Y7HKT_fszivaY',
    'sensor-10': 'pCqn6fiw-eDlZNAqnOWRFoUaftY1jfkdLwoKLaSuFhk',
}


async def send_telemetry(client: httpx.AsyncClient):
    next_send = time.time()
    api_key = API_KEYS['sensor-' + f'{randint(1, 10)}'.zfill(2)]
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': api_key,
    }
    while True:
        data = {'value': round(random() * 100, 3)}
        try:
            result = await client.post(URL, json=data, headers=headers)
            print(result)
        except httpx.HTTPError as e:
            print(type(e).__name__)
        next_send += 1.0
        await asyncio.sleep(max(0.0, next_send - time.time()))


async def start_devices(max_devices: int = 1):
    limits = httpx.Limits(max_connections=max_devices, max_keepalive_connections=max_devices)
    async with httpx.AsyncClient(timeout=5.0, limits=limits) as client:
        cors = [send_telemetry(client) for _ in range(max_devices)]
        await asyncio.gather(*cors)


def start_precess():
    asyncio.run(start_devices(COUNT_DEVICE))


def main():
    processes = [Process(target=start_precess, daemon=True) for _ in range(COUNT_PROCESSES)]
    for process in processes:
        process.start()
    for process in processes:
        process.join()


if __name__ == '__main__':
    main()
