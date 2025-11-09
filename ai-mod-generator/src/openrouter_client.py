"""OpenRouter API client with tool calling support."""

import json
import time
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from openai import OpenAI
import tiktoken


logger = logging.getLogger(__name__)


class ToolCall:
    """Represents a tool call from the AI."""

    def __init__(self, id: str, name: str, arguments: Dict[str, Any]):
        self.id = id
        self.name = name
        self.arguments = arguments

    def to_dict(self):
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "type": "function",
            "function": {
                "name": self.name,
                "arguments": json.dumps(self.arguments)
            }
        }


class OpenRouterResponse:
    """Wrapper for OpenRouter API response."""

    def __init__(self, response):
        self.response = response
        self.message = response.choices[0].message
        self.content = self.message.content
        self.tool_calls = self._parse_tool_calls()
        self.usage = response.usage

    def _parse_tool_calls(self) -> List[ToolCall]:
        """Parse tool calls from response."""
        if not hasattr(self.message, 'tool_calls') or self.message.tool_calls is None:
            return []

        tool_calls = []
        for tc in self.message.tool_calls:
            tool_calls.append(ToolCall(
                id=tc.id,
                name=tc.function.name,
                arguments=json.loads(tc.function.arguments)
            ))
        return tool_calls

    def has_tool_calls(self) -> bool:
        """Check if response contains tool calls."""
        return len(self.tool_calls) > 0

    def is_final(self) -> bool:
        """Check if this is the final response (no tool calls)."""
        return not self.has_tool_calls() and self.content is not None


class CostTracker:
    """Track API costs and token usage."""

    def __init__(self, log_dir: Path, input_cost_per_1m: float, output_cost_per_1m: float):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.input_cost_per_1m = input_cost_per_1m
        self.output_cost_per_1m = output_cost_per_1m
        self.tracker_file = self.log_dir / "cost_tracker.json"
        self.usage_log = self.log_dir / "api_usage.log"

        # Load existing costs
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self._load_tracker()

    def _load_tracker(self):
        """Load existing cost tracking data."""
        if self.tracker_file.exists():
            with open(self.tracker_file, 'r') as f:
                data = json.load(f)
                self.total_input_tokens = data.get("total_input_tokens", 0)
                self.total_output_tokens = data.get("total_output_tokens", 0)
                self.total_cost = data.get("total_cost", 0.0)

    def _save_tracker(self):
        """Save cost tracking data."""
        data = {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost": self.total_cost,
            "last_updated": datetime.now().isoformat()
        }
        with open(self.tracker_file, 'w') as f:
            json.dump(data, f, indent=2)

    def track_usage(self, input_tokens: int, output_tokens: int, operation: str = ""):
        """Track token usage and calculate cost."""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

        input_cost = (input_tokens / 1_000_000) * self.input_cost_per_1m
        output_cost = (output_tokens / 1_000_000) * self.output_cost_per_1m
        call_cost = input_cost + output_cost
        self.total_cost += call_cost

        # Log the usage
        log_entry = (
            f"{datetime.now().isoformat()} | "
            f"Operation: {operation} | "
            f"Input: {input_tokens} | "
            f"Output: {output_tokens} | "
            f"Cost: ${call_cost:.6f} | "
            f"Total: ${self.total_cost:.4f}\n"
        )
        with open(self.usage_log, 'a') as f:
            f.write(log_entry)

        self._save_tracker()
        return call_cost

    def get_total_cost(self) -> float:
        """Get total cost so far."""
        return self.total_cost


class OpenRouterClient:
    """OpenRouter API client with tool calling support."""

    def __init__(self, api_key: str, base_url: str, model: str, log_dir: str,
                 input_cost_per_1m: float = 0.15, output_cost_per_1m: float = 1.50):
        """Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key
            base_url: API base URL
            model: Model identifier
            log_dir: Directory for logs
            input_cost_per_1m: Cost per 1M input tokens
            output_cost_per_1m: Cost per 1M output tokens
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model
        self.cost_tracker = CostTracker(
            Path(log_dir),
            input_cost_per_1m,
            output_cost_per_1m
        )

        # Initialize tokenizer for counting
        try:
            self.encoder = tiktoken.encoding_for_model("gpt-4")
        except:
            self.encoder = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if not text:
            return 0
        return len(self.encoder.encode(text))

    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False
    ) -> OpenRouterResponse:
        """Make a chat completion request with optional tool support.

        Args:
            messages: Conversation messages
            tools: Tool definitions in OpenAI format
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            OpenRouterResponse object
        """
        request_params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if tools:
            request_params["tools"] = tools
            request_params["tool_choice"] = "auto"

        # Retry logic with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(**request_params)

                # Track usage
                if hasattr(response, 'usage') and response.usage:
                    self.cost_tracker.track_usage(
                        response.usage.prompt_tokens,
                        response.usage.completion_tokens,
                        operation="chat_completion"
                    )

                return OpenRouterResponse(response)

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"API call failed (attempt {attempt + 1}): {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"API call failed after {max_retries} attempts: {e}")
                    raise

    def get_total_cost(self) -> float:
        """Get total cost of all API calls."""
        return self.cost_tracker.get_total_cost()

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "total_input_tokens": self.cost_tracker.total_input_tokens,
            "total_output_tokens": self.cost_tracker.total_output_tokens,
            "total_cost": self.cost_tracker.total_cost
        }
