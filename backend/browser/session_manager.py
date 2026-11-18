
import asyncio
import threading
import uuid

from playwright.async_api import async_playwright

from agent.runner import prepare_form_fill, execute_approved_fill


class BrowserJobManager:
    def __init__(self, headless=False):
        self.headless = headless
        self.loop = None
        self.thread = None
        self.ready = threading.Event()

        self.playwright = None
        self.browser = None
        self.jobs = {}

        self._start_loop()

    def _start_loop(self):
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.ready.set()
            self.loop.run_forever()

        self.thread = threading.Thread(
            target=run_loop,
            daemon=True,
        )
        self.thread.start()
        self.ready.wait()

        self._submit(self._start_browser())

    def _submit(self, coroutine):
        future = asyncio.run_coroutine_threadsafe(
            coroutine,
            self.loop,
        )
        return future.result(timeout=180)

    async def _start_browser(self):
        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=["--disable-notifications"],
        )

    async def _inspect(self, url, instruction):
        job_id = str(uuid.uuid4())

        context = await self.browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            fields, plan = await prepare_form_fill(
                page=page,
                user_instruction=instruction,
            )

            self.jobs[job_id] = {
                "page": page,
                "context": context,
                "fields": fields,
                "plan": plan,
                "status": "awaiting_approval",
            }

            return {
                "job_id": job_id,
                "status": "awaiting_approval",
                "fields": [
                    field.model_dump()
                    for field in fields
                ],
                "plan": plan.model_dump(),
            }

        except Exception:
            await context.close()
            raise

    async def _fill(self, job_id):
        job = self.jobs.get(job_id)

        if not job:
            raise ValueError("Job not found or browser session expired")

        if job["status"] != "awaiting_approval":
            raise ValueError("Job is not awaiting approval")

        results = await execute_approved_fill(
            page=job["page"],
            form_fields=job["fields"],
            approved_plan=job["plan"],
            approval_confirmed=True,
        )

        job["status"] = "filled"
        return {
            "job_id": job_id,
            "status": "filled",
            "results": results,
        }

    def inspect(self, url, instruction):
        return self._submit(self._inspect(url, instruction))

    def fill(self, job_id):
        return self._submit(self._fill(job_id))


# One manager per Django process.
browser_manager = BrowserJobManager(headless=False)
