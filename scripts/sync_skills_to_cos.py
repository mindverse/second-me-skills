#!/usr/bin/env python3
"""Sync SecondMe skills to Tencent COS and refresh CDN.

Uses only the Python standard library (request signing included) so CI needs
no pip install at all.
"""
from __future__ import annotations

import argparse
import base64
import configparser
import hashlib
import hmac
import io
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUCKET = "mindverseglobal-cos-1309544882"
REGION = "ap-shanghai"
COS_ENDPOINT = f"https://{BUCKET}.cos.{REGION}.myqcloud.com"
CDN_BASE_URL = "https://mindverseglobal-cos-cdn.mindverse.com"
PUBLIC_BASE_URL = "https://second-me.cn"
DISCOVERY_SCHEMA_V2 = "https://schemas.agentskills.io/discovery/0.2.0/schema.json"
# EdgeOne zones fronting the skill distribution; their edge cache (max-age up to
# 1y) must be purged on every deploy or second.me keeps serving stale skills.
EDGEONE_ZONES = {
    "zone-3hvat5bhdh1m": "second.me",
    "zone-3hv7vs8o265e": "second-me.cn",
}
TEXT_TYPE = "text/plain; charset=utf-8"
JSON_TYPE = "application/json; charset=utf-8"
ZIP_TYPE = "application/zip"
CACHE_CONTROL = "no-cache"
IMMUTABLE_CACHE_CONTROL = "public, max-age=31536000, immutable"
HTTP_ATTEMPTS = 3
HTTP_TIMEOUT = 30
UPLOAD_WORKERS = 8
VERIFY_ATTEMPTS = 6
VERIFY_TIMEOUT = 15


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


def http_call(request: urllib.request.Request) -> bytes:
    for attempt in range(1, HTTP_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", "replace")
            if error.code < 500 or attempt == HTTP_ATTEMPTS:
                raise SystemExit(
                    f"{request.get_method()} {request.full_url} failed with HTTP {error.code}:\n{body}"
                )
        except OSError as error:
            if attempt == HTTP_ATTEMPTS:
                raise SystemExit(f"{request.get_method()} {request.full_url} failed: {error}")
        time.sleep(attempt)
    raise AssertionError("unreachable")


def cos_authorization(secret_id: str, secret_key: str, method: str, path: str) -> str:
    now = int(time.time())
    key_time = f"{now - 60};{now + 3600}"
    sign_key = hmac.new(secret_key.encode(), key_time.encode(), hashlib.sha1).hexdigest()
    http_string = f"{method.lower()}\n{path}\n\n\n"
    string_to_sign = f"sha1\n{key_time}\n{hashlib.sha1(http_string.encode()).hexdigest()}\n"
    signature = hmac.new(sign_key.encode(), string_to_sign.encode(), hashlib.sha1).hexdigest()
    return (
        "q-sign-algorithm=sha1"
        f"&q-ak={secret_id}"
        f"&q-sign-time={key_time}"
        f"&q-key-time={key_time}"
        "&q-header-list="
        "&q-url-param-list="
        f"&q-signature={signature}"
    )


def cos_request(
    secret_id: str,
    secret_key: str,
    method: str,
    key: str,
    *,
    params: dict[str, str] | None = None,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> bytes:
    path = "/" + urllib.parse.quote(key)
    url = COS_ENDPOINT + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    request_headers = dict(headers or {})
    request_headers["Authorization"] = cos_authorization(secret_id, secret_key, method, "/" + key)
    request = urllib.request.Request(url, data=data, method=method, headers=request_headers)
    return http_call(request)


def tencent_api(
    secret_id: str,
    secret_key: str,
    *,
    service: str,
    version: str,
    action: str,
    payload: dict,
) -> dict:
    host = f"{service}.tencentcloudapi.com"
    timestamp = int(time.time())
    date = time.strftime("%Y-%m-%d", time.gmtime(timestamp))
    body = json.dumps(payload).encode()
    canonical_request = (
        "POST\n/\n\n"
        f"content-type:{JSON_TYPE}\nhost:{host}\n\n"
        "content-type;host\n"
        f"{hashlib.sha256(body).hexdigest()}"
    )
    scope = f"{date}/{service}/tc3_request"
    string_to_sign = (
        f"TC3-HMAC-SHA256\n{timestamp}\n{scope}\n"
        f"{hashlib.sha256(canonical_request.encode()).hexdigest()}"
    )

    def digest(key: bytes, message: str) -> bytes:
        return hmac.new(key, message.encode(), hashlib.sha256).digest()

    signing_key = digest(digest(digest(("TC3" + secret_key).encode(), date), service), "tc3_request")
    signature = hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).hexdigest()
    request = urllib.request.Request(
        f"https://{host}/",
        data=body,
        method="POST",
        headers={
            "Authorization": (
                f"TC3-HMAC-SHA256 Credential={secret_id}/{scope}, "
                f"SignedHeaders=content-type;host, Signature={signature}"
            ),
            "Content-Type": JSON_TYPE,
            "X-TC-Action": action,
            "X-TC-Version": version,
            "X-TC-Timestamp": str(timestamp),
        },
    )
    response = json.loads(http_call(request))
    if "Error" in response.get("Response", {}):
        raise SystemExit(f"{service} API {action} failed: {json.dumps(response, ensure_ascii=False)}")
    return response


@dataclass(frozen=True)
class Upload:
    key: str
    content_type: str
    path: Path | None = None
    data: bytes | None = None
    cache_control: str = CACHE_CONTROL
    immutable: bool = False

    def body(self) -> bytes:
        if self.data is not None:
            return self.data
        if self.path is None:
            raise ValueError(f"upload {self.key} has neither data nor a source path")
        return self.path.read_bytes()


@dataclass(frozen=True)
class ReleaseArtifact:
    skill_dir: Path
    version: str
    prefix: str
    archive_key: str
    index_key: str
    archive_url: str
    digest: str
    data: bytes


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


def extract_version(skill_md: Path) -> str:
    lines = skill_md.read_text(encoding="utf-8").splitlines()
    in_metadata = False

    for line in lines:
        if line == "metadata:":
            in_metadata = True
            continue
        if in_metadata and line and not line[0].isspace():
            break
        if in_metadata and line.strip().startswith("version:"):
            version = line.split(":", 1)[1].strip().strip("\"'")
            if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
                raise ValueError(f"invalid release version in {skill_md}: {version!r}")
            return version

    raise ValueError(f"metadata.version is required in {skill_md}")


def skill_files(skill_dir: Path) -> list[str]:
    return sorted(
        path.relative_to(skill_dir).as_posix()
        for path in skill_dir.rglob("*")
        if path.is_file()
    )


def index_bytes(skills: list[Path]) -> bytes:
    payload = {
        "skills": [
            {
                "name": skill_dir.name,
                "description": extract_description(skill_dir / "SKILL.md"),
                "files": skill_files(skill_dir),
            }
            for skill_dir in skills
        ]
    }
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()


def deterministic_archive_bytes(skill_dir: Path) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, mode="w", compression=zipfile.ZIP_STORED) as archive:
        for relative in skill_files(skill_dir):
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (skill_dir / relative).read_bytes())
    return output.getvalue()


def build_release_artifact(skill_dir: Path) -> ReleaseArtifact:
    version = extract_version(skill_dir / "SKILL.md")
    prefix = f".well-known/agent-skills/releases/{skill_dir.name}/{version}"
    archive_key = f"{prefix}/{skill_dir.name}-{version}.zip"
    data = deterministic_archive_bytes(skill_dir)
    return ReleaseArtifact(
        skill_dir=skill_dir,
        version=version,
        prefix=prefix,
        archive_key=archive_key,
        index_key=f"{prefix}/.well-known/agent-skills/index.json",
        archive_url=f"{PUBLIC_BASE_URL}/{archive_key}",
        digest=f"sha256:{hashlib.sha256(data).hexdigest()}",
        data=data,
    )


def discovery_index_bytes(artifacts: list[ReleaseArtifact]) -> bytes:
    payload = {
        "$schema": DISCOVERY_SCHEMA_V2,
        "skills": [
            {
                "name": artifact.skill_dir.name,
                "type": "archive",
                "description": extract_description(artifact.skill_dir / "SKILL.md"),
                "url": artifact.archive_url,
                "digest": artifact.digest,
            }
            for artifact in sorted(artifacts, key=lambda item: item.skill_dir.name)
        ],
    }
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()


def public_skill_entry_bytes(skill_dir: Path) -> bytes:
    """Make relative reference links auditable when SKILL.md is served at /skill.md."""
    content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    audit_base = f"{PUBLIC_BASE_URL}/.well-known/skills/{skill_dir.name}/"
    content = re.sub(
        r"\]\((references/[^)]+)\)",
        lambda match: f"]({urllib.parse.urljoin(audit_base, match.group(1))})",
        content,
    )
    return content.encode()


def content_type_for(path: Path) -> str:
    return JSON_TYPE if path.suffix == ".json" else TEXT_TYPE


def build_uploads() -> tuple[list[Upload], list[str]]:
    """Return the full upload list and the remote prefixes we own (for stale cleanup)."""
    skills = skill_dirs()
    dev_skill = ROOT / "skills" / "secondme-dev-assistant"
    uploads: list[Upload] = []

    # The dev skill ships only via develop-well-known (and its raw skill/ path).
    # Both public discovery indexes must expose the user skill alone.
    user_skills = [skill_dir for skill_dir in skills if skill_dir != dev_skill]
    releases = [build_release_artifact(skill_dir) for skill_dir in user_skills]

    for skill_dir in skills:
        for file in sorted(path for path in skill_dir.rglob("*") if path.is_file()):
            relative = file.relative_to(skill_dir).as_posix()
            content_type = content_type_for(file)
            raw_data = (
                public_skill_entry_bytes(skill_dir)
                if skill_dir in user_skills and relative == "SKILL.md"
                else None
            )
            uploads.append(
                Upload(
                    key=f"skill/{skill_dir.name}/{relative}",
                    content_type=content_type,
                    path=None if raw_data is not None else file,
                    data=raw_data,
                )
            )
            if skill_dir != dev_skill:
                uploads.append(
                    Upload(
                        key=f".well-known/skills/{skill_dir.name}/{relative}",
                        content_type=content_type,
                        path=file,
                    )
                )
            if skill_dir == dev_skill:
                uploads.append(
                    Upload(
                        key=f"develop-well-known/skills/{skill_dir.name}/{relative}",
                        content_type=content_type,
                        path=file,
                    )
                )

    uploads.append(
        Upload(
            key=".well-known/skills/index.json",
            content_type=JSON_TYPE,
            data=index_bytes(user_skills),
        )
    )
    uploads.append(
        Upload(
            key=".well-known/agent-skills/index.json",
            content_type=JSON_TYPE,
            data=discovery_index_bytes(releases),
        )
    )
    for release in releases:
        uploads.extend(
            [
                Upload(
                    key=release.archive_key,
                    content_type=ZIP_TYPE,
                    data=release.data,
                    cache_control=IMMUTABLE_CACHE_CONTROL,
                    immutable=True,
                ),
                Upload(
                    key=release.index_key,
                    content_type=JSON_TYPE,
                    data=discovery_index_bytes([release]),
                    cache_control=IMMUTABLE_CACHE_CONTROL,
                    immutable=True,
                ),
            ]
        )
    uploads.append(
        Upload(
            key="develop-well-known/skills/index.json",
            content_type=JSON_TYPE,
            data=index_bytes([dev_skill]),
        )
    )

    prefixes = [f"skill/{skill_dir.name}/" for skill_dir in skills]
    # Do not stale-clean .well-known/agent-skills/: it contains immutable historical releases.
    prefixes += [".well-known/skills/", "develop-well-known/skills/"]
    return uploads, prefixes


def list_remote_keys(secret_id: str, secret_key: str, prefix: str) -> set[str]:
    keys: set[str] = set()
    marker = ""
    while True:
        params = {"prefix": prefix, "max-keys": "1000"}
        if marker:
            params["marker"] = marker
        root = ET.fromstring(cos_request(secret_id, secret_key, "GET", "", params=params))
        for element in root.iter():
            element.tag = element.tag.split("}")[-1]
        contents = root.findall("Contents")
        for entry in contents:
            key = entry.findtext("Key")
            if key:
                keys.add(key)
        if (root.findtext("IsTruncated") or "false").lower() != "true":
            return keys
        marker = root.findtext("NextMarker") or (contents[-1].findtext("Key") if contents else "")
        if not marker:
            return keys


def put_object(secret_id: str, secret_key: str, upload: Upload) -> None:
    body = upload.body()
    if upload.immutable:
        existing = get_remote_object(secret_id, secret_key, upload.key)
        if existing is not None:
            if existing == body:
                print(f"immutable object already exists {upload.key}")
                return
            raise SystemExit(
                f"refusing to overwrite immutable release object with different content: {upload.key}"
            )

    headers = {
        "Content-Type": upload.content_type,
        "Cache-Control": upload.cache_control,
        "Content-MD5": base64.b64encode(hashlib.md5(body).digest()).decode(),
    }
    if upload.immutable:
        headers["x-cos-forbid-overwrite"] = "true"

    try:
        cos_request(secret_id, secret_key, "PUT", upload.key, data=body, headers=headers)
    except SystemExit as error:
        if upload.immutable and "HTTP 409" in str(error):
            existing = get_remote_object(secret_id, secret_key, upload.key)
            if existing == body:
                print(f"immutable object concurrently published {upload.key}")
                return
            raise SystemExit(
                f"immutable release object appeared with different content: {upload.key}"
            ) from error
        raise
    print(f"uploaded {upload.key}")


def get_remote_object(secret_id: str, secret_key: str, key: str) -> bytes | None:
    try:
        return cos_request(secret_id, secret_key, "GET", key)
    except SystemExit as error:
        if "HTTP 404" in str(error):
            return None
        raise


def publication_batches(uploads: list[Upload]) -> list[list[Upload]]:
    immutable_archives = [
        upload
        for upload in uploads
        if upload.immutable and upload.content_type == ZIP_TYPE
    ]
    immutable_indexes = [
        upload
        for upload in uploads
        if upload.immutable and upload.content_type == JSON_TYPE
    ]
    latest_index_keys = {
        ".well-known/agent-skills/index.json",
        ".well-known/skills/index.json",
        "develop-well-known/skills/index.json",
    }
    mutable_content = [
        upload
        for upload in uploads
        if not upload.immutable and upload.key not in latest_index_keys
    ]
    latest_indexes = [upload for upload in uploads if upload.key in latest_index_keys]
    return [immutable_archives, immutable_indexes, mutable_content, latest_indexes]


def sync_to_cos(*, dry_run: bool) -> None:
    uploads, prefixes = build_uploads()
    batches = publication_batches(uploads)

    if dry_run:
        for batch in batches:
            for upload in batch:
                mode = "PUT-if-absent" if upload.immutable else "PUT"
                print(f"+ {mode} {upload.key} ({upload.content_type})")
        for prefix in prefixes:
            print(f"+ delete stale objects under {prefix}")
        return

    secret_id = secret_value("TENCENT_COS_SECRET_ID", "secret_id")
    secret_key = secret_value("TENCENT_COS_SECRET_KEY", "secret_key")
    if not secret_id or not secret_key:
        raise SystemExit("TENCENT_COS_SECRET_ID and TENCENT_COS_SECRET_KEY are required")

    for batch in batches:
        with ThreadPoolExecutor(max_workers=UPLOAD_WORKERS) as pool:
            list(pool.map(lambda upload: put_object(secret_id, secret_key, upload), batch))
    print(f"{len(uploads)} objects uploaded")

    uploaded_keys = {upload.key for upload in uploads}
    stale = sorted(
        key
        for prefix in prefixes
        for key in list_remote_keys(secret_id, secret_key, prefix)
        if key not in uploaded_keys
    )
    for key in stale:
        cos_request(secret_id, secret_key, "DELETE", key)
        print(f"deleted stale {key}")
    if not stale:
        print("no stale objects")


def refresh_cdn(*, dry_run: bool) -> None:
    paths = [
        f"{CDN_BASE_URL}/skill/secondme/",
        f"{CDN_BASE_URL}/skill/secondme-dev-assistant/",
        f"{CDN_BASE_URL}/.well-known/agent-skills/",
        f"{CDN_BASE_URL}/.well-known/skills/",
        f"{CDN_BASE_URL}/develop-well-known/skills/",
    ]

    if dry_run:
        print("+ purge CDN paths " + ", ".join(paths))
        print("+ purge EdgeOne skill paths on " + ", ".join(EDGEONE_ZONES.values()))
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

    response = tencent_api(
        secret_id,
        secret_key,
        service="cdn",
        version="2018-06-06",
        action="PurgePathCache",
        payload={"Paths": paths, "FlushType": "flush"},
    )
    print(json.dumps(response, ensure_ascii=False))

    refresh_edgeone(secret_id, secret_key)


def refresh_edgeone(secret_id: str, secret_key: str) -> None:
    for zone_id, domain in EDGEONE_ZONES.items():
        for purge_type, targets in [
            ("purge_url", [f"https://{domain}/skill.md", f"https://{domain}/dev-skill.md"]),
            (
                "purge_prefix",
                [
                    f"https://{domain}/.well-known/agent-skills/",
                    f"https://{domain}/.well-known/skills/",
                    f"https://{domain}/skill/",
                ],
            ),
        ]:
            response = tencent_api(
                secret_id,
                secret_key,
                service="teo",
                version="2022-09-01",
                action="CreatePurgeTask",
                payload={"ZoneId": zone_id, "Type": purge_type, "Targets": targets},
            )
            job_id = response.get("Response", {}).get("JobId", "")
            print(f"edgeone purge {domain} {purge_type}: {job_id}")


def expected_public_objects() -> dict[str, bytes]:
    uploads, _ = build_uploads()
    by_key = {upload.key: upload for upload in uploads}
    expected = {
        f"{PUBLIC_BASE_URL}/{key}": upload.body()
        for key, upload in by_key.items()
        if key.startswith(".well-known/skills/")
        or key.startswith(".well-known/agent-skills/")
    }
    expected[f"{PUBLIC_BASE_URL}/skill.md"] = by_key[
        "skill/secondme/SKILL.md"
    ].body()
    return expected


def verify_public_distribution(*, dry_run: bool) -> None:
    expected = expected_public_objects()
    if dry_run:
        for url in expected:
            print(f"+ verify GET {url}")
        return

    failures: dict[str, str] = {}
    for attempt in range(1, VERIFY_ATTEMPTS + 1):
        failures = {}
        for url, expected_body in expected.items():
            request = urllib.request.Request(
                url,
                headers={
                    "Cache-Control": "no-cache",
                    "User-Agent": "secondme-skill-publish-verifier/1.0",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=VERIFY_TIMEOUT) as response:
                    actual_body = response.read()
            except (OSError, urllib.error.HTTPError) as error:
                failures[url] = str(error)
                continue

            if actual_body != expected_body:
                expected_digest = hashlib.sha256(expected_body).hexdigest()[:12]
                actual_digest = hashlib.sha256(actual_body).hexdigest()[:12]
                failures[url] = (
                    f"content mismatch (expected sha256 {expected_digest}, got {actual_digest})"
                )

        if not failures:
            print(f"verified {len(expected)} public distribution objects")
            return
        if attempt < VERIFY_ATTEMPTS:
            time.sleep(min(attempt, 3))

    details = "\n".join(f"- {url}: {reason}" for url, reason in failures.items())
    raise SystemExit(f"public distribution verification failed:\n{details}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync SecondMe skills to Tencent COS and refresh CDN.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned requests without sending them.")
    parser.add_argument("--skip-upload", action="store_true", help="Skip uploading to COS.")
    parser.add_argument("--skip-cdn", action="store_true", help="Skip Tencent CDN purge.")
    parser.add_argument("--skip-verify", action="store_true", help="Skip public distribution verification.")
    args = parser.parse_args()

    if not args.skip_upload:
        sync_to_cos(dry_run=args.dry_run)
    if not args.skip_cdn:
        refresh_cdn(dry_run=args.dry_run)
    if not args.skip_verify and not args.skip_upload:
        verify_public_distribution(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
