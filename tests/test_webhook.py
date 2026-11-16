import asyncio
import json
from types import SimpleNamespace

from tornado.testing import AsyncHTTPTestCase

from src.webhook import SECRET_HEADER, make_webhook_app

SECRET = "s3cret"
UPDATE = {"update_id": 42, "message": {"message_id": 1, "date": 0, "chat": {"id": 7, "type": "private"}, "text": "/p"}}


class WebhookTest(AsyncHTTPTestCase):
    def get_app(self):
        self.application = SimpleNamespace(update_queue=asyncio.Queue(), bot=None)
        return make_webhook_app(self.application, SECRET)

    def post(self, body, secret=SECRET):
        headers = {SECRET_HEADER: secret} if secret is not None else {}
        return self.fetch("/", method="POST", body=body, headers=headers)

    def test_valid_update_is_queued(self):
        response = self.post(json.dumps(UPDATE))
        assert response.code == 200
        assert self.application.update_queue.get_nowait().update_id == 42

    def test_wrong_secret_is_rejected(self):
        assert self.post(json.dumps(UPDATE), secret="wrong").code == 403
        assert self.application.update_queue.empty()

    def test_missing_secret_is_rejected(self):
        assert self.post(json.dumps(UPDATE), secret=None).code == 403

    def test_invalid_body_is_rejected(self):
        assert self.post("not json").code == 400
