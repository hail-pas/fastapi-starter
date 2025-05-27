import asyncio
import threading

from loguru import logger

from core.context import ctx
from api.service.task.consumer_health_check import consumer_status, start_http_server


async def msg_handler(msg: dict) -> None: ...


async def consume() -> None:
    async with ctx():
        consumer = ""  # 这里需要初消费数据原
        while True:
            try:
                if last_msg:
                    logger.info("retrying last message")
                    await msg_handler(last_msg)  # 重试错误数据
                async for msg in consumer:
                    last_msg = msg
                    await msg_handler(msg)
                    consumer_status.last_message = msg.value.decode()
                    last_msg = None
            except Exception as e:
                logger.error(f"Consume encounter an error: {e}. Retrying after 5 seconds.")
                consumer_status.status = "error"
                consumer_status.error = str(e)
                await asyncio.sleep(5)


if __name__ == "__main__":
    http_thread = threading.Thread(target=start_http_server)
    http_thread.daemon = True
    http_thread.start()
    # asyncio.run(consume())
    # 启动Kafka消费者
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume())
