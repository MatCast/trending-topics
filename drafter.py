import json
import logging
import os
from google import genai
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ContentDrafter:
    def __init__(self, templates_file: str):
        self.templates_file = templates_file
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "MOCK_KEY"))

    def _load_templates(self) -> List[Dict[str, str]]:
        with open(self.templates_file, "r") as f:
            data = json.load(f)
            return data.get("versions", [])

    def draft_post(
        self, trend: Dict[str, Any], template: Dict[str, str], is_mock: bool = False
    ) -> str:
        """Drafts a single LinkedIn post variation."""
        prompt = f"""
        Write a LinkedIn post about the following trending AI topic.

        Topic Title: {trend.get("title")}
        Source Link: {trend.get("url")}
        Engagement: {trend.get("ups", 0)} upvotes, {trend.get("comments", 0)} comments
        Description: {trend.get("description", "N/A")}

        Style Requirements:
        - Persona/Style: {template.get("style")}
        - Hook style (example): {template.get("hook")}

        Keep it engaging, formatted for LinkedIn (spacing, maybe a couple emojis),
        and ensure it fits the requested style perfectly.
        """

        if is_mock:
            logger.info(
                f"[MOCK] Drafted post for '{trend.get('title')}' in style '{template.get('name')}'."
            )
            return (f"[{template.get('name')}]\n\n*Mocked Content for:* {trend.get('title')}"
                    f"\n\n*Style:* {template.get('style')}\n*Link:* {trend.get('url')}\n\n#AI #Trending")

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating content from Gemini: {e}")
            return f"[Error drafting content for {trend.get('title')}]"

    def generate_all_drafts(
        self, trends: List[Dict[str, Any]], is_mock: bool = False
    ) -> str:
        """Generates all drafts for all top trends and formats them into a single text output."""
        templates = self._load_templates()
        output_blocks = []

        for i, trend in enumerate(trends, 1):
            top_header = (f"=================================================\nTOPIC {i}: {trend.get('title')}"
                          "\nSOURCE: {trend.get('url')}\n=================================================\n")
            output_blocks.append(top_header)

            for template in templates:
                draft_text = self.draft_post(trend, template, is_mock=is_mock)
                block = f"--- VERSION: {template.get('name')} ---\n{draft_text}\n\n"
                output_blocks.append(block)

            output_blocks.append("\n\n")

        return "".join(output_blocks)
