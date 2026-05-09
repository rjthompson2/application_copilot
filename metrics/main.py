import asyncio
from database.database import get_metrics

async def main():
    applied, failed, total = await get_metrics()
    print(f"Applied {len(applied)}, Failed {len(failed)}, Total {len(total)}")

if __name__ == '__main__':
    asyncio.run(main())