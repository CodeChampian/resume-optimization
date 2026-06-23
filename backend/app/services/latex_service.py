import logging
import os
import re
import struct
import subprocess
import tempfile
import uuid
import zlib
from app.core.config import settings

logger = logging.getLogger("latex")


class LatexService:
    # Characters that need escaping in LaTeX text mode.
    # Does NOT include {} (structural delimiters) or # (parameter references in \newcommand).
    _LATEX_SPECIAL_CHARS = re.compile(r"(?<!\\)([&%$_])")

    @staticmethod
    def sanitize_latex(latex_content: str) -> str:
        """Escape LaTeX special characters (& % $ # _) in text content.

        Only escapes characters that are NOT already preceded by a backslash.
        Does NOT escape curly braces {} as they are structural LaTeX delimiters.
        """
        return LatexService._LATEX_SPECIAL_CHARS.sub(r"\\\1", latex_content)

    @staticmethod
    def extract_candidate_name(latex_content: str) -> str | None:
        m = re.search(r"\\resumename\s*\{([^}]+)\}", latex_content)
        return m.group(1).strip() if m else None

    @staticmethod
    def _create_placeholder_png(path: str) -> None:
        """Create a 1x1 white PNG placeholder."""
        sig = b"\x89PNG\r\n\x1a\n"
        ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
        ihdr = struct.pack(">I", 13) + b"IHDR" + ihdr_data + struct.pack(">I", zlib.crc32(b"IHDR" + ihdr_data))
        raw = b"\x00\xff\xff\xff"
        compressed = zlib.compress(raw)
        idat = struct.pack(">I", len(compressed)) + b"IDAT" + compressed + struct.pack(">I", zlib.crc32(b"IDAT" + compressed))
        iend = struct.pack(">I", 0) + b"IEND" + struct.pack(">I", zlib.crc32(b"IEND"))
        with open(path, "wb") as f:
            f.write(sig + ihdr + idat + iend)

    @staticmethod
    def _create_placeholder_jpeg(path: str) -> None:
        """Create a minimal 1x1 white JPEG placeholder."""
        data = bytes([
            0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46,
            0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01,
            0x00, 0x01, 0x00, 0x00, 0xff, 0xdb, 0x00, 0x43,
            0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08,
            0x07, 0x07, 0x07, 0x09, 0x09, 0x08, 0x0a, 0x0c,
            0x14, 0x0d, 0x0c, 0x0b, 0x0b, 0x0c, 0x19, 0x12,
            0x13, 0x0f, 0x14, 0x1d, 0x1a, 0x1f, 0x1e, 0x1d,
            0x1a, 0x1c, 0x1c, 0x20, 0x24, 0x2e, 0x27, 0x20,
            0x22, 0x2c, 0x23, 0x1c, 0x1c, 0x28, 0x37, 0x29,
            0x2c, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1f, 0x27,
            0x39, 0x3d, 0x38, 0x32, 0x3c, 0x2e, 0x33, 0x34,
            0x32, 0xff, 0xc0, 0x00, 0x0b, 0x08, 0x00, 0x01,
            0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xff, 0xc4,
            0x00, 0x1f, 0x00, 0x00, 0x01, 0x05, 0x01, 0x01,
            0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04,
            0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0xff,
            0xc4, 0x00, 0xb5, 0x10, 0x00, 0x02, 0x01, 0x03,
            0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x01, 0x02, 0x03, 0x11, 0x04, 0x05, 0x21, 0x12,
            0x31, 0x41, 0x06, 0x13, 0x51, 0x61, 0x07, 0x22,
            0x71, 0x14, 0x32, 0x81, 0x91, 0xa1, 0x08, 0x23,
            0x42, 0xb1, 0xc1, 0x15, 0x52, 0xd1, 0xf0, 0x24,
            0x33, 0x62, 0x72, 0x82, 0x09, 0x0a, 0x16, 0x17,
            0x18, 0x19, 0x1a, 0x25, 0x26, 0x27, 0x28, 0x29,
            0x2a, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a,
            0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4a,
            0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5a,
            0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6a,
            0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x7a,
            0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8a,
            0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99,
            0x9a, 0xa2, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7, 0xa8,
            0xa9, 0xaa, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7,
            0xb8, 0xb9, 0xba, 0xc2, 0xc3, 0xc4, 0xc5, 0xc6,
            0xc7, 0xc8, 0xc9, 0xca, 0xd2, 0xd3, 0xd4, 0xd5,
            0xd6, 0xd7, 0xd8, 0xd9, 0xda, 0xe1, 0xe2, 0xe3,
            0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9, 0xea, 0xf1,
            0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf7, 0xf8, 0xf9,
            0xfa, 0xff, 0xda, 0x00, 0x08, 0x01, 0x01, 0x00,
            0x00, 0x3f, 0x00, 0x7b, 0x94, 0x11, 0x00, 0xff,
            0xd9,
        ])
        with open(path, "wb") as f:
            f.write(data)

    def compile(self, latex_content: str) -> str | None:
        file_id = str(uuid.uuid4())
        tex_filename = f"{file_id}.tex"
        pdf_filename = f"{file_id}.pdf"

        # Sanitize only the document body — preamble % comments must be preserved
        parts = latex_content.split(r"\begin{document}", 1)
        if len(parts) == 2:
            preamble = parts[0]
            body = parts[1]
            end_idx = body.rfind(r"\end{document}")
            if end_idx != -1:
                body_before = body[:end_idx]
                body_after = body[end_idx:]
                body_before = self.sanitize_latex(body_before)
                latex_content = preamble + r"\begin{document}" + body_before + body_after
            else:
                latex_content = preamble + r"\begin{document}" + self.sanitize_latex(body)
        else:
            latex_content = self.sanitize_latex(latex_content)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create placeholder images for any \includegraphics references
            for img_match in re.finditer(
                r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}",
                latex_content,
            ):
                img_path = img_match.group(1).strip()
                img_name = os.path.basename(img_path)
                if not img_name:
                    continue
                placeholder = os.path.join(tmpdir, img_name)
                if os.path.exists(placeholder):
                    continue
                ext = os.path.splitext(img_name)[1].lower()
                if ext in (".jpg", ".jpeg"):
                    self._create_placeholder_jpeg(placeholder)
                else:
                    self._create_placeholder_png(placeholder)
                logger.info("Created placeholder image: %s", img_name)
            tex_path = os.path.join(tmpdir, tex_filename)
            with open(tex_path, "w") as f:
                f.write(latex_content)

            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_filename],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=60,
            )

            pdf_path = os.path.join(tmpdir, pdf_filename)
            if not os.path.exists(pdf_path):
                log_path = os.path.join(tmpdir, f"{file_id}.log")
                if os.path.exists(log_path):
                    with open(log_path) as lf:
                        log_content = lf.read()
                    error_lines = [
                        line
                        for line in log_content.split("\n")
                        if line.startswith("!")
                    ]
                    logger.error(
                        "LaTeX compilation failed for %s. Errors: %s",
                        file_id,
                        error_lines[:10],
                    )
                else:
                    logger.error(
                        "LaTeX compilation failed for %s. stdout: %s, stderr: %s",
                        file_id,
                        result.stdout[-500:] if result.stdout else "",
                        result.stderr[-500:] if result.stderr else "",
                    )
                return None

            if result.returncode != 0:
                logger.warning(
                    "LaTeX had non-zero exit for %s but PDF was produced",
                    file_id,
                )

            os.makedirs(settings.generated_dir, exist_ok=True)
            dest_path = os.path.join(settings.generated_dir, pdf_filename)
            os.rename(pdf_path, dest_path)
            return pdf_filename

    def cleanup(self, pdf_filename: str) -> None:
        pdf_path = os.path.join(settings.generated_dir, pdf_filename)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


latex_service = LatexService()
