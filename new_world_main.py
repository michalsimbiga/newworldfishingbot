import asyncio

from new_world_fishing_bot import NewWorldFishingBot

if __name__ == '__main__':

    BOT = NewWorldFishingBot()

    loop = asyncio.get_event_loop()
    loop.create_task(BOT.run())
    loop.run_forever()
