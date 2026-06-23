import json
import re
from google import genai
from app.core.config import settings


class GeminiService:
    def __init__(self) -> None:
        self._client: genai.Client | None = None
        self.model = settings.gemini_model

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            if not settings.gemini_api_key:
                raise RuntimeError(
                    "GEMINI_API_KEY not configured. Set it in .env or environment."
                )
            self._client = genai.Client(api_key=settings.gemini_api_key)
        return self._client

    def _extract_json(self, text: str) -> dict:
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
            text = text.strip()

        text = re.sub(r",\s*([}\]])", r"\1", text)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        text = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r"\\\\", text)
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            if "Extra data" in str(e):
                decoder = json.JSONDecoder()
                try:
                    obj, _ = decoder.raw_decode(text)
                    return obj
                except json.JSONDecodeError:
                    pass
            raise

    async def optimize_resumes(
        self,
        templates_by_role: dict[str, str],
        jds_by_role: dict[str, list[dict]],
    ) -> list[dict]:
        sections = []
        expected_outputs: list[str] = []
        total_jd_count = 0
        for role in templates_by_role:
            template = templates_by_role[role]
            jds = jds_by_role.get(role, [])
            total_jd_count += len(jds)
            jd_lines = "\n".join(
                f"  JD #{entry['index']}: {entry['title']}\n  {entry['content']}"
                for entry in jds
            )
            sections.append(
                f"### {role}\n\nTemplate:\n{template}\n\nJDs:\n{jd_lines}"
            )
            for entry in jds:
                expected_outputs.append(f"- {role} JD #{entry['index']}")

        prompt = f"""You are an ATS resume optimization expert.

For each role below, optimize the LaTeX template against each JD.

There are exactly {total_jd_count} pairs. Output exactly {total_jd_count} results, one per pair.

Expected outputs:
{chr(10).join(expected_outputs)}

Rules:
- Keep the template structure, packages, commands, fonts, colors, and layout exactly as-is.
- PRESERVE ALL entries — never remove any project, job, education, certification, or any other listing. Duplicate all existing entries in the output.
- Never fabricate experience, projects, certifications, employers, or education.
- Add JD-relevant keywords and required skills into the Skills section, project descriptions, and experience bullet points.
- Rephrase existing bullet points to naturally incorporate JD keywords — but never delete any bullet point, project, or job entry.
- Update the Skills section to include skills from the JD that match the candidate's background.
- Include ats_before and ats_after scores (0-100) for each result.

Use this exact JSON format — no markdown, no explanation:
{{"results":[{{"role":"business_analyst","jd_index":0,"ats_before":72,"ats_after":91,"optimized_latex":"<full LaTeX>"}}]}}

Role keys must be exactly: business_analyst, business_intelligence_analyst, project_manager, product_owner.

Every backslash in optimized_latex must be escaped as \\\\ (double backslash in JSON).

DATA:

{chr(10).join(sections)}
"""
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        raw = response.text.strip()
        data = self._extract_json(raw)
        return data.get("results", [])


gemini_service = GeminiService()
