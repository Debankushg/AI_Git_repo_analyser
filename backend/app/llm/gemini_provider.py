from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from app.core.config import settings
from app.core.exceptions import RateLimitError, UpstreamError
from app.llm.base_llm_provider import BaseLLMProvider, LLMSession, LLMTurn
from app.models.chat_model import ConversationMessage
from app.models.tool_model import ToolCall, ToolResult, ToolSpec


class GeminiSession(LLMSession):
    def __init__(self, client: genai.Client, config: types.GenerateContentConfig, contents: list) -> None:
        self._client = client
        self._config = config
        self._contents = contents

    async def generate(self) -> LLMTurn:
        try:
            response = await self._client.aio.models.generate_content(
                model=settings.gemini_model, contents=self._contents, config=self._config
            )
        except genai_errors.ClientError as exc:
            if exc.code == 429:
                raise RateLimitError(
                    "Gemini rate limit reached (free tier). Wait a minute and retry, or enable billing."
                ) from exc
            raise UpstreamError(f"Gemini error: {exc.message}") from exc

        if not response.candidates or not response.candidates[0].content:
            return LLMTurn(text="The model returned no content (possibly blocked or empty).")

        content = response.candidates[0].content
        self._contents.append(content)  # keep as-is (preserves thought signatures)
        parts = content.parts or []
        return LLMTurn(
            text="".join(p.text for p in parts if p.text),
            tool_calls=[ToolCall(p.function_call.name, dict(p.function_call.args or {})) for p in parts if p.function_call],
        )

    def add_tool_results(self, results: list[ToolResult]) -> None:
        parts = [types.Part.from_function_response(name=r.name, response={"output": r.output}) for r in results]
        self._contents.append(types.Content(role="user", parts=parts))


class GeminiProvider(BaseLLMProvider):
    def __init__(self) -> None:
        self._client = genai.Client(api_key=settings.gemini_api_key)

    def new_session(self, system_prompt: str, messages: list[ConversationMessage], tools: list[ToolSpec]) -> GeminiSession:
        declarations = [
            types.FunctionDeclaration(name=t.name, description=t.description, parameters_json_schema=t.input_schema)
            for t in tools
        ]
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=[types.Tool(function_declarations=declarations)],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        contents = [
            types.Content(role="user" if m.role == "user" else "model", parts=[types.Part(text=m.content)])
            for m in messages
        ]
        return GeminiSession(self._client, config, contents)
