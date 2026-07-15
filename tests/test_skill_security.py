from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import re
import sys
import unittest
import zipfile
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
USER_SKILL = ROOT / "skills" / "secondme"
SCRIPT = ROOT / "scripts" / "sync_skills_to_cos.py"
SPEC = importlib.util.spec_from_file_location("sync_skills_to_cos", SCRIPT)
assert SPEC and SPEC.loader
sync_skills_to_cos = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = sync_skills_to_cos
SPEC.loader.exec_module(sync_skills_to_cos)


class SkillSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.uploads, cls.stale_prefixes = sync_skills_to_cos.build_uploads()
        cls.by_key = {upload.key: upload for upload in cls.uploads}
        cls.release = sync_skills_to_cos.build_release_artifact(USER_SKILL)

    def test_v2_index_uses_versioned_archive_and_sha256_digest(self) -> None:
        index = json.loads(
            self.by_key[".well-known/agent-skills/index.json"].body()
        )

        self.assertEqual(index["$schema"], sync_skills_to_cos.DISCOVERY_SCHEMA_V2)
        self.assertEqual(len(index["skills"]), 1)
        entry = index["skills"][0]
        self.assertEqual(entry["name"], "secondme")
        self.assertEqual(entry["type"], "archive")
        self.assertEqual(entry["url"], self.release.archive_url)
        self.assertEqual(entry["digest"], self.release.digest)
        self.assertEqual(
            entry["digest"],
            f"sha256:{hashlib.sha256(self.release.data).hexdigest()}",
        )

        versioned_index = json.loads(self.by_key[self.release.index_key].body())
        self.assertEqual(versioned_index, index)
        self.assertTrue(self.by_key[self.release.archive_key].immutable)
        self.assertTrue(self.by_key[self.release.index_key].immutable)

    def test_release_archive_is_deterministic_and_complete(self) -> None:
        rebuilt = sync_skills_to_cos.build_release_artifact(USER_SKILL)
        self.assertEqual(rebuilt.data, self.release.data)

        with zipfile.ZipFile(io.BytesIO(self.release.data)) as archive:
            self.assertEqual(
                archive.namelist(), sync_skills_to_cos.skill_files(USER_SKILL)
            )
            for relative in archive.namelist():
                self.assertEqual(
                    archive.read(relative), (USER_SKILL / relative).read_bytes()
                )

    def test_install_command_uses_latest_discovery_without_automatic_flags(self) -> None:
        command = "npx skills add https://second-me.cn"
        for path in [USER_SKILL / "SKILL.md", ROOT / "README.md"]:
            text = path.read_text(encoding="utf-8")
            self.assertIn(command, text)
            command_lines = [line for line in text.splitlines() if line == command]
            self.assertTrue(command_lines, path)
            self.assertNotIn(" -g", command_lines[0])
            self.assertNotIn(" -y", command_lines[0])

    def test_public_entry_links_are_auditable_without_changing_package_links(self) -> None:
        local = (USER_SKILL / "SKILL.md").read_text(encoding="utf-8")
        public = self.by_key["skill/secondme/SKILL.md"].body().decode()
        relative_targets = re.findall(r"\]\((references/[^)]+)\)", local)

        self.assertTrue(relative_targets)
        self.assertNotIn("](references/", public)
        for target in relative_targets:
            expected = (
                "https://second-me.cn/.well-known/skills/secondme/" + target
            )
            self.assertIn(f"]({expected})", public)

        packaged = self.by_key[
            ".well-known/skills/secondme/SKILL.md"
        ].body().decode()
        self.assertEqual(packaged, local)

    def test_legacy_index_lists_every_public_skill_file(self) -> None:
        index = json.loads(self.by_key[".well-known/skills/index.json"].body())
        self.assertEqual(len(index["skills"]), 1)
        entry = index["skills"][0]
        self.assertEqual(entry["name"], "secondme")
        self.assertEqual(entry["files"], sync_skills_to_cos.skill_files(USER_SKILL))
        for relative in entry["files"]:
            self.assertIn(f".well-known/skills/secondme/{relative}", self.by_key)

    def test_immutable_releases_are_excluded_from_stale_cleanup(self) -> None:
        self.assertFalse(
            any(
                prefix.startswith(".well-known/agent-skills/")
                for prefix in self.stale_prefixes
            )
        )

    def test_release_artifact_is_published_before_latest_indexes(self) -> None:
        batches = sync_skills_to_cos.publication_batches(self.uploads)
        positions = {
            upload.key: batch_number
            for batch_number, batch in enumerate(batches)
            for upload in batch
        }
        self.assertLess(
            positions[self.release.archive_key],
            positions[self.release.index_key],
        )
        self.assertLess(
            positions[self.release.index_key],
            positions[".well-known/agent-skills/index.json"],
        )
        self.assertLess(
            positions[".well-known/skills/secondme/SKILL.md"],
            positions[".well-known/skills/index.json"],
        )

    def test_skills_do_not_reference_openclaw_credentials(self) -> None:
        forbidden_path = "~/" + ".openclaw/" + ".credentials"
        for path in (ROOT / "skills").rglob("*"):
            if path.is_file():
                self.assertNotIn(
                    forbidden_path,
                    path.read_text(encoding="utf-8"),
                    path,
                )

    def test_immutable_upload_skips_identical_remote_object(self) -> None:
        upload = sync_skills_to_cos.Upload(
            key="immutable.zip",
            content_type="application/zip",
            data=b"same",
            immutable=True,
        )
        with mock.patch.object(
            sync_skills_to_cos, "cos_request", return_value=b"same"
        ) as request:
            sync_skills_to_cos.put_object("id", "key", upload)

        request.assert_called_once_with("id", "key", "GET", "immutable.zip")

    def test_immutable_upload_rejects_changed_remote_object(self) -> None:
        upload = sync_skills_to_cos.Upload(
            key="immutable.zip",
            content_type="application/zip",
            data=b"new",
            cache_control=sync_skills_to_cos.IMMUTABLE_CACHE_CONTROL,
            immutable=True,
        )
        with mock.patch.object(
            sync_skills_to_cos, "cos_request", return_value=b"old"
        ):
            with self.assertRaisesRegex(SystemExit, "refusing to overwrite"):
                sync_skills_to_cos.put_object("id", "key", upload)

    def test_new_immutable_upload_forbids_overwrite(self) -> None:
        calls: list[tuple[str, dict[str, str] | None]] = []

        def fake_request(
            _secret_id: str,
            _secret_key: str,
            method: str,
            _key: str,
            *,
            params: dict[str, str] | None = None,
            data: bytes | None = None,
            headers: dict[str, str] | None = None,
        ) -> bytes:
            del params, data
            calls.append((method, headers))
            if method == "GET":
                raise SystemExit("GET failed with HTTP 404")
            return b""

        upload = sync_skills_to_cos.Upload(
            key="immutable.zip",
            content_type="application/zip",
            data=b"new",
            cache_control=sync_skills_to_cos.IMMUTABLE_CACHE_CONTROL,
            immutable=True,
        )
        with mock.patch.object(sync_skills_to_cos, "cos_request", fake_request):
            sync_skills_to_cos.put_object("id", "key", upload)

        self.assertEqual([method for method, _ in calls], ["GET", "PUT"])
        self.assertEqual(calls[-1][1]["x-cos-forbid-overwrite"], "true")
        self.assertEqual(
            calls[-1][1]["Cache-Control"],
            sync_skills_to_cos.IMMUTABLE_CACHE_CONTROL,
        )


if __name__ == "__main__":
    unittest.main()
