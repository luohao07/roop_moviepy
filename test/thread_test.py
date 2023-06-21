import asyncio

async def method_a(content):
    while True:
        print(content)
        await asyncio.sleep(1)

async def method_b(content):
    while True:
        print(content)
        await asyncio.sleep(1)

async def main():
    task_a = asyncio.create_task(method_a("A"))
    task_b = asyncio.create_task(method_b("B"))
    await asyncio.gather(task_a, task_b)

if __name__ == '__main__':
    asyncio.run(main())
