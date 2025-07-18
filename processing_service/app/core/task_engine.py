import logging
from pathlib import Path
import openai
from openai import OpenAI
from tenacity import (
    retry, stop_after_attempt, wait_exponential_jitter,
    retry_if_exception_type, before_sleep_log
)
from processing_service.app.utils import prompt_loader
from processing_service.app.config.settings import Settings

logger = logging.getLogger(__name__)

class TaskEngine:
    """Executes the llm task for the target document."""

    def __init__(self, settings: Settings, default_prompt_name: str):
        self._model          = settings.OPENAI_MODEL
        self._max_tokens     = settings.OPENAI_MAX_TOKENS
        self._api_key        = settings.OPENAI_API_KEY
        self._default_prompt = default_prompt_name

        self._prompt_loader  = prompt_loader.PromptLoader()
        self._client         = OpenAI(api_key=self._api_key, timeout=30.0)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=1, max=10),
        retry=retry_if_exception_type((
            openai.RateLimitError,
            openai.APITimeoutError,
            openai.APIConnectionError,
            openai.APIError,
            openai.InternalServerError,
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def _call_llm(self, prompt: str) -> str:
        """Send the prompt to the LLM; retry if errors."""
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": "You are a document assistant."},
                {"role": "user",    "content": prompt},
            ],
            max_tokens=self._max_tokens,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

    def run(self, text: str, prompt_name: str | None = None) -> str:
        """Run the task on *text* using *prompt_name* or the default."""
        prompt_name = prompt_name or self._default_prompt

        try:
            template = self._prompt_loader.load(prompt_name)
            prompt   = template.replace("{input}", text.strip())
            logger.debug("TaskEngine | prompt='%s' model='%s'", prompt_name, self._model)
            return self._call_llm(prompt)

        except openai.OpenAIError as oe:
            logger.error("OpenAI failure on prompt '%s': %s", prompt_name, oe)
            raise RuntimeError(f"LLM error: {oe}") from oe

        except Exception as ex:
            logger.exception("TaskEngine unexpected failure (%s)", prompt_name)
            raise RuntimeError("Task execution failed") from ex
