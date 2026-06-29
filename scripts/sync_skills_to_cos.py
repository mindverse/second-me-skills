#!/usr/bin/env python3
from __future__ import annotations

import argparse
import configparser
import json
import os
import shutil
import site
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUCKET = "mindverseglobal-cos-1309544882"
REGION = "ap-shanghai"
CDN_BASE_URL = "https://mindverseglobal-cos-cdn.mindverse.com"
TEXT_HEADERS = '{"Content-Type":"text/plain; charset=utf-8","Cache-Control":"no-cache"}'
JSON_HEADERS = '{"Content-Type":"application/json; charset=utf-8","Cache-Control":"no-cache"}'


def run(command: list[str], *, dry_run: bool = False) -> None:
    printable = ["***" if item in redacted_values() else item for item in command]
    print("+ " + " ".join(printable))
    if dry_run:
        return
    subprocess.run(command, cwd=ROOT, check=True)


def redacted_values() -> set[str]:
    return {
        value
        for value in (
            os.environ.get("TENCENT_COS_SECRET_ID"),
            os.environ.get("TENCENT_COS_SECRET_KEY"),
            os.environ.get("TENCENT_CDN_SECRET_ID"),
            os.environ.get("TENCENT_CDN_SECRET_KEY"),
            tccli_credential("secret_id"),
            tccli_credential("secret_key"),
        )
        if value
    }


def tccli_credential(key: str) -> str | None:
    credential_path = Path.home() / ".tccli" / "default.credential"
    if not credential_path.is_file():
        return None

    text = credential_path.read_text(encoding="utf-8").strip()
    if text.startswith("{"):
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return None
        json_key = {"secret_id": "secretId", "secret_key": "secretKey"}.get(key, key)
        value = data.get(json_key)
        return str(value) if value else None

    parser = configparser.ConfigParser()
    try:
        parser.read_string(text)
    except configparser.Error:
        return None
    if not parser.has_section("default") or not parser.has_option("default", key):
        return None
    return parser.get("default", key)


def secret_value(env_name: str, tccli_key: str) -> str | None:
    return os.environ.get(env_name) or tccli_credential(tccli_key)


def coscmd_command() -> str:
    found = shutil.which("coscmd")
    if found:
        return found

    candidates = [
        Path(site.USER_BASE) / "bin" / "coscmd",
        Path.home() / ".local" / "bin" / "coscmd",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)

    return "coscmd"


def skill_dirs() -> list[Path]:
    return sorted(path for path in (ROOT / "skills").iterdir() if (path / "SKILL.md").is_file())


def extract_description(skill_md: Path) -> str:
    lines = skill_md.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return ""

    for line in lines[1:]:
        if line == "---":
            break
        if line.startswith("description:"):
            value = line.split(":", 1)[1].strip()
            return value.strip('"')
    return ""


def markdown_files(skill_dir: Path) -> list[str]:
    return sorted(path.relative_to(skill_dir).as_posix() for path in skill_dir.rglob("*.md"))


def write_index(target: Path, skills: list[Path]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "skills": [
            {
                "name": skill_dir.name,
                "description": extract_description(skill_dir / "SKILL.md"),
                "files": markdown_files(skill_dir),
            }
            for skill_dir in skills
        ]
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare_well_known() -> tuple[Path, Path]:
    well_known = ROOT / ".tmp-sync-well-known" / "skills"
    develop = ROOT / ".tmp-sync-develop-well-known" / "skills"
    shutil.rmtree(well_known.parent, ignore_errors=True)
    shutil.rmtree(develop.parent, ignore_errors=True)

    skills = skill_dirs()
    write_index(well_known / "index.json", skills)
    for skill_dir in skills:
        shutil.copytree(skill_dir, well_known / skill_dir.name, dirs_exist_ok=True)

    dev_skill = ROOT / "skills" / "secondme-dev-assistant"
    write_index(develop / "index.json", [dev_skill])
    shutil.copytree(dev_skill, develop / "secondme-dev-assistant", dirs_exist_ok=True)

    return well_known, develop


def configure_cos(dry_run: bool) -> None:
    secret_id = secret_value("TENCENT_COS_SECRET_ID", "secret_id")
    secret_key = secret_value("TENCENT_COS_SECRET_KEY", "secret_key")
    if not secret_id or not secret_key:
        raise SystemExit("TENCENT_COS_SECRET_ID and TENCENT_COS_SECRET_KEY are required")

    run(
        [
            coscmd_command(),
            "config",
            "-a",
            secret_id,
            "-s",
            secret_key,
            "-b",
            BUCKET,
            "-r",
            REGION,
        ],
        dry_run=dry_run,
    )


def upload_dir(local_dir: Path, remote_prefix: str, *, headers: str, dry_run: bool) -> None:
    run(
        [
            coscmd_command(),
            "upload",
            "-r",
            "-s",
            "--delete",
            "-f",
            "-y",
            "-H",
            headers,
            str(local_dir) + "/",
            remote_prefix,
        ],
        dry_run=dry_run,
    )


def upload_file(local_file: Path, remote_path: str, *, headers: str, dry_run: bool) -> None:
    run(
        [
            coscmd_command(),
            "upload",
            "-f",
            "-y",
            "-H",
            headers,
            str(local_file),
            remote_path,
        ],
        dry_run=dry_run,
    )


def sync_to_cos(well_known: Path, develop: Path, *, dry_run: bool) -> None:
    configure_cos(dry_run)

    upload_dir(ROOT / "skills" / "secondme", "skill/secondme/", headers=TEXT_HEADERS, dry_run=dry_run)
    upload_dir(
        ROOT / "skills" / "secondme-dev-assistant",
        "skill/secondme-dev-assistant/",
        headers=TEXT_HEADERS,
        dry_run=dry_run,
    )
    upload_dir(well_known, ".well-known/skills/", headers=TEXT_HEADERS, dry_run=dry_run)
    upload_file(well_known / "index.json", ".well-known/skills/index.json", headers=JSON_HEADERS, dry_run=dry_run)
    upload_dir(develop, "develop-well-known/skills/", headers=TEXT_HEADERS, dry_run=dry_run)
    upload_file(
        develop / "index.json",
        "develop-well-known/skills/index.json",
        headers=JSON_HEADERS,
        dry_run=dry_run,
    )


def refresh_cdn(*, dry_run: bool) -> None:
    paths = [
        f"{CDN_BASE_URL}/skill/secondme/",
        f"{CDN_BASE_URL}/skill/secondme-dev-assistant/",
        f"{CDN_BASE_URL}/.well-known/skills/",
        f"{CDN_BASE_URL}/develop-well-known/skills/",
    ]

    if dry_run:
        print("+ purge CDN paths " + ", ".join(paths))
        return

    secret_id = secret_value("TENCENT_CDN_SECRET_ID", "secret_id") or secret_value(
        "TENCENT_COS_SECRET_ID", "secret_id"
    )
    secret_key = secret_value("TENCENT_CDN_SECRET_KEY", "secret_key") or secret_value(
        "TENCENT_COS_SECRET_KEY", "secret_key"
    )
    if not secret_id or not secret_key:
        print("No Tencent CDN credentials configured. Skipping CDN refresh.")
        return

    from tencentcloud.cdn.v20180606 import cdn_client, models
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile

    cred = credential.Credential(secret_id, secret_key)
    http_profile = HttpProfile(endpoint="cdn.tencentcloudapi.com")
    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile
    client = cdn_client.CdnClient(cred, "", client_profile)

    request = models.PurgePathCacheRequest()
    request.from_json_string(json.dumps({"Paths": paths, "FlushType": "flush"}))
    response = client.PurgePathCache(request)
    print(response.to_json_string())


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync SecondMe skills to Tencent COS and refresh CDN.")
    parser.add_argument("--dry-run", action="store_true", help="Generate artifacts and print commands without uploading.")
    parser.add_argument("--skip-upload", action="store_true", help="Generate artifacts without uploading to COS.")
    parser.add_argument("--skip-cdn", action="store_true", help="Skip Tencent CDN purge.")
    parser.add_argument("--keep-temp", action="store_true", help="Keep generated temporary directories.")
    args = parser.parse_args()

    well_known, develop = prepare_well_known()
    try:
        print(f"Prepared {well_known.relative_to(ROOT)}")
        print(f"Prepared {develop.relative_to(ROOT)}")
        if not args.skip_upload:
            sync_to_cos(well_known, develop, dry_run=args.dry_run)
        if not args.skip_cdn:
            refresh_cdn(dry_run=args.dry_run)
    finally:
        if not args.keep_temp:
            shutil.rmtree(ROOT / ".tmp-sync-well-known", ignore_errors=True)
            shutil.rmtree(ROOT / ".tmp-sync-develop-well-known", ignore_errors=True)


if __name__ == "__main__":
    main()
