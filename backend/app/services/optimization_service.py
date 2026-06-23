import logging
import os
import re
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import mongodb
from app.core.config import settings
from app.services.gemini_service import gemini_service
from app.services.latex_service import latex_service

logger = logging.getLogger("optimization")

RE_NON_SAFE = re.compile(r"[^\w\s-]")


def _sanitize_filename_part(s: str) -> str:
    return RE_NON_SAFE.sub("", s).strip().replace(" ", "_")


class OptimizationService:
    async def run(self, project_id: str) -> None:
        db = mongodb.get_db()

        job_doc = {
            "project_id": ObjectId(project_id),
            "status": "processing",
            "created_at": datetime.utcnow(),
        }
        job_result = await db.optimization_jobs.insert_one(job_doc)
        job_id = job_result.inserted_id

        try:
            templates_cursor = db.resume_templates.find(
                {"project_id": ObjectId(project_id)}
            )
            templates = await templates_cursor.to_list(length=100)
            templates_by_role = {t["role"]: t for t in templates}

            candidate_names: dict[str, str | None] = {}
            for role, t in templates_by_role.items():
                name = latex_service.extract_candidate_name(t["latex_content"])
                if name:
                    candidate_names[role] = _sanitize_filename_part(name)
                else:
                    candidate_names[role] = None

            jds_cursor = db.job_descriptions.find(
                {"project_id": ObjectId(project_id)}
            )
            jds = await jds_cursor.to_list(length=500)

            jds_by_role: dict[str, list[dict]] = {}
            for jd in jds:
                role = jd["role"]
                if role not in jds_by_role:
                    jds_by_role[role] = []
                jds_by_role[role].append({
                    "index": len(jds_by_role[role]),
                    "_id": str(jd["_id"]),
                    "company_name": jd.get("company_name", "Unknown"),
                    "title": jd.get("title", ""),
                    "content": jd["content"],
                })

            templates_map = {
                role: t["latex_content"]
                for role, t in templates_by_role.items()
            }

            logger.info(
                "Starting single Gemini call for %d roles with templates",
                len(templates_map),
            )
            results = await gemini_service.optimize_resumes(
                templates_by_role=templates_map,
                jds_by_role=jds_by_role,
            )
            logger.info("Got %d total results from Gemini", len(results))

            role_key_map = {
                "business_analyst": "business_analyst",
                "business analyst": "business_analyst",
                "business intelligence analyst": "business_intelligence_analyst",
                "business_intelligence_analyst": "business_intelligence_analyst",
                "project_manager": "project_manager",
                "project manager": "project_manager",
                "product_owner": "product_owner",
                "product owner": "product_owner",
            }

            def resolve_role(raw: str) -> str | None:
                lower = raw.strip().lower()
                return role_key_map.get(lower)

            role_jd_lookup: dict[str, dict[int, dict]] = {}
            for role, entries in jds_by_role.items():
                role_jd_lookup[role] = {e["index"]: e for e in entries}

            def _rename_pdf(uuid_pdf: str, company: str, role: str) -> str:
                cand = candidate_names.get(role)
                if not cand:
                    cand = "Candidate"
                company_safe = _sanitize_filename_part(company)
                base = f"{cand}_{company_safe}_{role}"
                filename = f"{base}.pdf"
                dest = os.path.join(settings.generated_dir, filename)
                counter = 1
                while os.path.exists(dest):
                    filename = f"{base}_{counter}.pdf"
                    dest = os.path.join(settings.generated_dir, filename)
                    counter += 1
                src = os.path.join(settings.generated_dir, uuid_pdf)
                if os.path.exists(src):
                    os.rename(src, dest)
                return filename

            generated_count = 0
            handled: set[tuple[str, int]] = set()

            for result in results:
                raw_role = result.get("role", "")
                role = resolve_role(raw_role)
                jd_index = result.get("jd_index")
                optimized_latex = result.get("optimized_latex", "")
                ats_before = result.get("ats_before")
                ats_after = result.get("ats_after")

                if role is None:
                    logger.warning("Unknown role %s in result, skipping", raw_role)
                    continue

                jd_entry = role_jd_lookup.get(role, {}).get(jd_index)
                if jd_entry is None:
                    logger.warning(
                        "Invalid jd_index %s for role %s", jd_index, role
                    )
                    continue

                handled.add((role, jd_index))

                pdf_filename = latex_service.compile(optimized_latex)
                if pdf_filename:
                    company_name = jd_entry.get("company_name", "Unknown")
                    pdf_filename = _rename_pdf(pdf_filename, company_name, role)
                else:
                    logger.warning(
                        "PDF compilation failed for %s JD %s", role, jd_index
                    )

                gen_doc = {
                    "job_id": job_id,
                    "role": role,
                    "jd_id": ObjectId(jd_entry["_id"]),
                    "jd_title": jd_entry["title"],
                    "company_name": jd_entry.get("company_name", ""),
                    "ats_before": ats_before,
                    "ats_after": ats_after,
                    "optimized_latex": optimized_latex,
                    "pdf_path": pdf_filename,
                    "created_at": datetime.utcnow(),
                }
                await db.generated_resumes.insert_one(gen_doc)
                generated_count += 1

            for role, entries in jds_by_role.items():
                template = templates_by_role.get(role)
                if not template:
                    continue
                for entry in entries:
                    idx = entry["index"]
                    if (role, idx) in handled:
                        continue
                    logger.warning(
                        "Gemini missed JD %s for role %s, using original template",
                        idx, role,
                    )
                    gen_doc = {
                        "job_id": job_id,
                        "role": role,
                        "jd_id": ObjectId(entry["_id"]),
                        "jd_title": entry["title"],
                        "company_name": entry.get("company_name", ""),
                        "optimized_latex": template["latex_content"],
                        "pdf_path": None,
                        "created_at": datetime.utcnow(),
                    }
                    await db.generated_resumes.insert_one(gen_doc)
                    generated_count += 1

            await db.optimization_jobs.update_one(
                {"_id": job_id},
                {"$set": {"status": "completed"}},
            )
            logger.info(
                "Optimization complete for project %s: %d resumes generated",
                project_id, generated_count,
            )
        except Exception:
            await db.optimization_jobs.update_one(
                {"_id": job_id},
                {"$set": {"status": "failed"}},
            )
            logger.exception("Optimization failed for project %s", project_id)


optimization_service = OptimizationService()
