import asyncio
import hmac
import json
import logging
import signal

import tornado.web
from telegram import Update
from telegram.ext import Application

SECRET_HEADER = "X-Telegram-Bot-Api-Secret-Token"

logger = logging.getLogger(__name__)


class TelegramUpdateHandler(tornado.web.RequestHandler):
    def initialize(self, telegram_app: Application, secret: str) -> None:
        self.telegram_app = telegram_app
        self.secret = secret

    async def post(self) -> None:
        received = self.request.headers.get(SECRET_HEADER, "")
        if not hmac.compare_digest(received.encode(), self.secret.encode()):
            self.set_status(403)
            return

        try:
            payload = json.loads(self.request.body)
        except ValueError:
            self.set_status(400)
            return

        await self.telegram_app.update_queue.put(Update.de_json(payload, self.telegram_app.bot))


def make_webhook_app(application: Application, secret: str) -> tornado.web.Application:
    return tornado.web.Application([(r"/", TelegramUpdateHandler, {"telegram_app": application, "secret": secret})])


async def serve_webhook(application: Application, port: int, secret: str) -> None:
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)

    async with application:
        await application.start()
        server = make_webhook_app(application, secret).listen(port, address="0.0.0.0")
        logger.info(f"Serving webhook updates on port {port}")
        try:
            await stop.wait()
        finally:
            server.stop()
            await application.stop()
