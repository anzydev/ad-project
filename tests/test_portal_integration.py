"""Tests for 3D Telemetry and VR Cardboard portal integration."""

import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

try:
    from ad_project.api.app import app
except RuntimeError as exc:
    if "prisma" in str(exc).lower():
        pytest.skip("Prisma client not generated in this environment", allow_module_level=True)
    raise

from ad_project.cli import parse_args


def test_cli_portal_argument():
    args = parse_args(["--portal"])
    assert args.portal is True


def test_live_metrics_api_endpoint():
    client = TestClient(app)
    response = client.get("/api/v1/metrics/live")
    assert response.status_code == 200
    data = response.json()
    assert "cpu" in data
    assert "overall_percent" in data["cpu"]
    assert "memory" in data
    assert "ram_percent" in data["memory"]
    assert "disk" in data
    assert "network" in data
    assert "top_processes" in data


def test_portal_html_serving():
    client = TestClient(app)
    response = client.get("/portal")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Telemetry Portal 3D" in response.text
    assert "VR Touch" in response.text


def test_portal_root_endpoint():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Telemetry Portal 3D" in response.text


def test_isd_unity_and_blender_assets_exist():
    base_dir = Path(__file__).resolve().parent.parent
    blend_file = base_dir / "ISD" / "Blender" / "TelemetryCore.blend"
    fbx_file = base_dir / "ISD" / "Unity" / "Assets" / "Art" / "TelemetryCore.fbx"
    scene_file = base_dir / "ISD" / "Unity" / "Assets" / "Generated" / "TelemetryPortal.unity"
    app_bundle = base_dir / "ISD" / "Unity" / "Builds" / "TelemetryPortal.app"

    assert blend_file.is_file(), "Blender TelemetryCore.blend model must exist"
    assert fbx_file.is_file(), "Exported FBX TelemetryCore.fbx must exist"
    assert scene_file.is_file(), "Generated Unity scene must exist"
    assert app_bundle.is_dir(), "Built Standalone macOS app TelemetryPortal.app must exist"
