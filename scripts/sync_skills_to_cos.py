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
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUCKET = "mindverseglobal-cos-1309544882"
REGION = "ap-shanghai"
COS_ENDPOINT = f"https://{BUCKET}.cos.{REGION}.myqcloud.com"
CDN_BASE_URL = "https://mindverseglobal-cos-cdn.mindverse.com"
# EdgeOne zones fronting the skill distribution; their edge cache (max-age up to
# 1y) must be purged on every deploy or second.me keeps serving stale skills.
EDGEONE_ZONES = {
    "zone-3hvat5bhdh1m": "second.me",
    "zone-3hv7vs8o265e": "second-me.cn",
}
TEXT_TYPE = "text/plain; charset=utf-8"
JSON_TYPE = "application/json; charset=utf-8"
CACHE_CONTROL = "no-cache"
HTTP_ATTEMPTS = 3
HTTP_TIMEOUT = 30
UPLOAD_WORKERS = 8


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

    def body(self) -> bytes:
        return self.data if self.data is not None else self.path.read_bytes()


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


def index_bytes(skills: list[Path]) -> bytes:
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
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()


def content_type_for(path: Path) -> str:
    return JSON_TYPE if path.suffix == ".json" else TEXT_TYPE


def build_uploads() -> tuple[list[Upload], list[str]]:
    """Return the full upload list and the remote prefixes we own (for stale cleanup)."""
    skills = skill_dirs()
    dev_skill = ROOT / "skills" / "secondme-dev-assistant"
    uploads: list[Upload] = []

    # the dev skill ships only via develop-well-known (and its raw skill/ path):
    # the main well-known index drives `npx skills add https://second-me.cn`,
    # which must install the user skill alone
    user_skills = [skill_dir for skill_dir in skills if skill_dir != dev_skill]

    for skill_dir in skills:
        for file in sorted(path for path in skill_dir.rglob("*") if path.is_file()):
            relative = file.relative_to(skill_dir).as_posix()
            content_type = content_type_for(file)
            uploads.append(Upload(key=f"skill/{skill_dir.name}/{relative}", content_type=content_type, path=file))
            if skill_dir != dev_skill:
                uploads.append(
                    Upload(key=f".well-known/skills/{skill_dir.name}/{relative}", content_type=content_type, path=file)
                )
            if skill_dir == dev_skill:
                uploads.append(
                    Upload(
                        key=f"develop-well-known/skills/{skill_dir.name}/{relative}",
                        content_type=content_type,
                        path=file,
                    )
                )

    uploads.append(Upload(key=".well-known/skills/index.json", content_type=JSON_TYPE, data=index_bytes(user_skills)))
    uploads.append(
        Upload(key="develop-well-known/skills/index.json", content_type=JSON_TYPE, data=index_bytes([dev_skill]))
    )

    prefixes = [f"skill/{skill_dir.name}/" for skill_dir in skills]
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
    headers = {
        "Content-Type": upload.content_type,
        "Cache-Control": CACHE_CONTROL,
        "Content-MD5": base64.b64encode(hashlib.md5(body).digest()).decode(),
    }
    cos_request(secret_id, secret_key, "PUT", upload.key, data=body, headers=headers)
    print(f"uploaded {upload.key}")


def sync_to_cos(*, dry_run: bool) -> None:
    uploads, prefixes = build_uploads()

    if dry_run:
        for upload in uploads:
            print(f"+ PUT {upload.key} ({upload.content_type})")
        for prefix in prefixes:
            print(f"+ delete stale objects under {prefix}")
        return

    secret_id = secret_value("TENCENT_COS_SECRET_ID", "secret_id")
    secret_key = secret_value("TENCENT_COS_SECRET_KEY", "secret_key")
    if not secret_id or not secret_key:
        raise SystemExit("TENCENT_COS_SECRET_ID and TENCENT_COS_SECRET_KEY are required")

    with ThreadPoolExecutor(max_workers=UPLOAD_WORKERS) as pool:
        list(pool.map(lambda upload: put_object(secret_id, secret_key, upload), uploads))
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
            ("purge_prefix", [f"https://{domain}/.well-known/skills/", f"https://{domain}/skill/"]),
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync SecondMe skills to Tencent COS and refresh CDN.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned requests without sending them.")
    parser.add_argument("--skip-upload", action="store_true", help="Skip uploading to COS.")
    parser.add_argument("--skip-cdn", action="store_true", help="Skip Tencent CDN purge.")
    args = parser.parse_args()

    if not args.skip_upload:
        sync_to_cos(dry_run=args.dry_run)
    if not args.skip_cdn:
        refresh_cdn(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
