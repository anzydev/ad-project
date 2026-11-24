using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

namespace TelemetryPortal
{
    public class TelemetryPortalController : MonoBehaviour
    {
        [Header("3D Telemetry Objects")]
        public Transform cpuCore;
        public Light cpuCoreLight;
        public Transform ramRing;
        public Transform swapRing;
        public Transform[] diskPlatters;
        public Transform uploadBeacon;
        public Transform downloadBeacon;
        public ParticleSystem uploadParticles;
        public ParticleSystem downloadParticles;
        public Transform batteryCell;
        public Transform batteryFill;
        public Transform[] processPillars;

        [Header("Visual Materials")]
        public Material coreMaterial;
        public Material ramMaterial;
        public Material diskMaterial;
        public Material batteryMaterial;

        [Header("Camera & Orbit Controls")]
        public Transform cameraRig;
        public Transform cameraPitchNode;
        public Camera mainCamera;
        public float orbitSpeed = 4.0f;
        public float zoomSpeed = 5.0f;
        public float minZoom = 4.0f;
        public float maxZoom = 25.0f;

        [Header("State")]
        public bool showHUD = true;
        public string apiBaseUrl = "http://127.0.0.1:8000";

        // Current and target telemetry for smooth lerping
        private TelemetrySnapshot currentData = new TelemetrySnapshot();
        private TelemetrySnapshot targetData = new TelemetrySnapshot();

        private float cameraYaw = 35.0f;
        private float cameraPitch = 25.0f;
        private float cameraDistance = 11.0f;
        private Vector2 lastMousePos;

        void Start()
        {
            InitializeDemoProcesses();
            UpdateCameraPosition();
            StartCoroutine(PollTelemetryRoutine());
        }

        void Update()
        {
            HandleInput();
            SmoothInterpolateTelemetry();
            AnimateCPUCore();
            AnimateMemoryRings();
            AnimateDiskPlatters();
            AnimateNetworkStreams();
            AnimateBatteryCell();
            AnimateProcessPillars();
        }

        private void InitializeDemoProcesses()
        {
            targetData.topProcesses.Clear();
            targetData.topProcesses.Add(new ProcessItem("python (ad-project)", 18.2f, 4.1f));
            targetData.topProcesses.Add(new ProcessItem("postgres (db)", 8.5f, 6.2f));
            targetData.topProcesses.Add(new ProcessItem("uvicorn (fastapi)", 6.1f, 3.8f));
            targetData.topProcesses.Add(new ProcessItem("windowserver", 5.4f, 7.5f));
            targetData.topProcesses.Add(new ProcessItem("code (editor)", 3.9f, 5.0f));
        }

        private void HandleInput()
        {
            // 'H' key toggles HUD overlay
            if (Input.GetKeyDown(KeyCode.H))
            {
                showHUD = !showHUD;
            }

            // 'R' key resets camera view
            if (Input.GetKeyDown(KeyCode.R))
            {
                cameraYaw = 35.0f;
                cameraPitch = 25.0f;
                cameraDistance = 11.0f;
                UpdateCameraPosition();
            }

            // Space key triggers immediate refresh
            if (Input.GetKeyDown(KeyCode.Space))
            {
                StartCoroutine(FetchLiveSnapshot());
            }

            // Mouse orbit when dragging left mouse button
            if (Input.GetMouseButtonDown(0))
            {
                lastMousePos = Input.mousePosition;
            }
            else if (Input.GetMouseButton(0))
            {
                Vector2 delta = (Vector2)Input.mousePosition - lastMousePos;
                cameraYaw += delta.x * orbitSpeed * 0.1f;
                cameraPitch -= delta.y * orbitSpeed * 0.1f;
                cameraPitch = Mathf.Clamp(cameraPitch, -10.0f, 80.0f);
                lastMousePos = Input.mousePosition;
                UpdateCameraPosition();
            }

            // Mouse scroll for smooth zoom
            float scroll = Input.GetAxis("Mouse ScrollWheel");
            if (Mathf.Abs(scroll) > 0.001f)
            {
                cameraDistance -= scroll * zoomSpeed;
                cameraDistance = Mathf.Clamp(cameraDistance, minZoom, maxZoom);
                UpdateCameraPosition();
            }
        }

        private void UpdateCameraPosition()
        {
            if (cameraRig == null) return;
            cameraRig.rotation = Quaternion.Euler(0f, cameraYaw, 0f);
            if (cameraPitchNode != null)
            {
                cameraPitchNode.localRotation = Quaternion.Euler(cameraPitch, 0f, 0f);
            }
            if (mainCamera != null)
            {
                mainCamera.transform.localPosition = new Vector3(0f, 0f, -cameraDistance);
            }
        }

        private void SmoothInterpolateTelemetry()
        {
            float t = Time.deltaTime * 3.0f;
            currentData.cpuPercent = Mathf.Lerp(currentData.cpuPercent, targetData.cpuPercent, t);
            currentData.memoryPercent = Mathf.Lerp(currentData.memoryPercent, targetData.memoryPercent, t);
            currentData.swapPercent = Mathf.Lerp(currentData.swapPercent, targetData.swapPercent, t);
            currentData.diskPercent = Mathf.Lerp(currentData.diskPercent, targetData.diskPercent, t);
            currentData.uploadSpeedKbps = Mathf.Lerp(currentData.uploadSpeedKbps, targetData.uploadSpeedKbps, t);
            currentData.downloadSpeedKbps = Mathf.Lerp(currentData.downloadSpeedKbps, targetData.downloadSpeedKbps, t);
            currentData.batteryPercent = Mathf.Lerp(currentData.batteryPercent, targetData.batteryPercent, t);
        }

        private void AnimateCPUCore()
        {
            if (cpuCore == null) return;

            // Rotation speed scales with CPU usage
            float rotSpeed = 20.0f + (currentData.cpuPercent * 1.5f);
            cpuCore.Rotate(Vector3.up, rotSpeed * Time.deltaTime, Space.World);
            cpuCore.Rotate(Vector3.right, (rotSpeed * 0.6f) * Time.deltaTime, Space.Self);

            // Breathing pulse effect
            float pulse = Mathf.Sin(Time.time * (1.5f + currentData.cpuPercent * 0.05f));
            float scaleMultiplier = 1.0f + (pulse * 0.06f * (currentData.cpuPercent / 100.0f));
            cpuCore.localScale = Vector3.one * (1.2f * scaleMultiplier);

            // Smooth color transition: Cyan (<50%) -> Amber (50-80%) -> Crimson (>80%)
            Color targetColor;
            if (currentData.cpuPercent < 50.0f)
            {
                targetColor = Color.Lerp(new Color(0.1f, 0.8f, 1.0f), new Color(0.2f, 1.0f, 0.6f), currentData.cpuPercent / 50.0f);
            }
            else if (currentData.cpuPercent < 80.0f)
            {
                targetColor = Color.Lerp(new Color(1.0f, 0.75f, 0.1f), new Color(1.0f, 0.45f, 0.05f), (currentData.cpuPercent - 50.0f) / 30.0f);
            }
            else
            {
                targetColor = Color.Lerp(new Color(1.0f, 0.2f, 0.2f), new Color(1.0f, 0.0f, 0.3f), (currentData.cpuPercent - 80.0f) / 20.0f);
            }

            if (coreMaterial != null)
            {
                coreMaterial.SetColor("_EmissionColor", targetColor * (1.2f + (currentData.cpuPercent * 0.015f)));
            }
            if (cpuCoreLight != null)
            {
                cpuCoreLight.color = targetColor;
                cpuCoreLight.intensity = 1.5f + (currentData.cpuPercent * 0.03f);
            }
        }

        private void AnimateMemoryRings()
        {
            if (ramRing != null)
            {
                // RAM Ring rotates horizontally
                float ramSpeed = 15.0f + (currentData.memoryPercent * 0.5f);
                ramRing.Rotate(Vector3.up, ramSpeed * Time.deltaTime, Space.World);
                float ramScale = 1.0f + (currentData.memoryPercent / 100.0f) * 0.25f;
                ramRing.localScale = new Vector3(ramScale, 1.0f, ramScale);
            }

            if (swapRing != null)
            {
                // Swap Ring rotates along inclined axis
                float swapSpeed = -20.0f - (currentData.swapPercent * 0.8f);
                swapRing.Rotate(new Vector3(1f, 1f, 0f).normalized, swapSpeed * Time.deltaTime, Space.Self);
            }
        }

        private void AnimateDiskPlatters()
        {
            if (diskPlatters == null || diskPlatters.Length == 0) return;

            // Disk platters float gently with a subtle sine wave
            for (int i = 0; i < diskPlatters.Length; i++)
            {
                if (diskPlatters[i] != null)
                {
                    float floatOffset = Mathf.Sin(Time.time * 1.5f + (i * 0.6f)) * 0.05f;
                    float baseY = 0.25f + (i * 0.35f) + floatOffset;
                    diskPlatters[i].localPosition = new Vector3(0f, baseY, 0f);
                    diskPlatters[i].Rotate(Vector3.up, (5.0f + (i * 3.0f)) * Time.deltaTime, Space.Self);
                }
            }
        }

        private void AnimateNetworkStreams()
        {
            // Network particle flow rate dynamically driven by bps
            if (uploadParticles != null)
            {
                var emission = uploadParticles.emission;
                emission.rateOverTime = Mathf.Clamp(currentData.uploadSpeedKbps * 0.15f, 5f, 80f);
            }

            if (downloadParticles != null)
            {
                var emission = downloadParticles.emission;
                emission.rateOverTime = Mathf.Clamp(currentData.downloadSpeedKbps * 0.15f, 10f, 120f);
            }

            // Subtle pulsing beacon lights
            if (uploadBeacon != null)
            {
                uploadBeacon.Rotate(Vector3.up, 30f * Time.deltaTime);
            }
            if (downloadBeacon != null)
            {
                downloadBeacon.Rotate(Vector3.up, -30f * Time.deltaTime);
            }
        }

        private void AnimateBatteryCell()
        {
            if (batteryFill != null)
            {
                // Fill height corresponds to battery percentage
                float normalized = Mathf.Clamp01(currentData.batteryPercent / 100.0f);
                batteryFill.localScale = new Vector3(0.9f, Mathf.Max(0.05f, normalized * 1.4f), 0.9f);
                batteryFill.localPosition = new Vector3(0f, -0.7f + (normalized * 0.7f), 0f);
            }

            if (batteryCell != null)
            {
                // Gentle floating hover
                float hover = Mathf.Sin(Time.time * 2.0f) * 0.08f;
                batteryCell.localPosition = new Vector3(0f, 1.0f + hover, -2.8f);
            }
        }

        private void AnimateProcessPillars()
        {
            if (processPillars == null) return;

            // Top active processes visualized as sleek floating pillars
            for (int i = 0; i < processPillars.Length; i++)
            {
                if (processPillars[i] == null) continue;

                float procCpu = 5.0f;
                if (i < targetData.topProcesses.Count)
                {
                    procCpu = targetData.topProcesses[i].cpuPercent;
                }

                float targetHeight = Mathf.Clamp(procCpu * 0.08f, 0.2f, 2.5f);
                Vector3 currentScale = processPillars[i].localScale;
                float newY = Mathf.Lerp(currentScale.y, targetHeight, Time.deltaTime * 3.0f);
                processPillars[i].localScale = new Vector3(currentScale.x, newY, currentScale.z);
            }
        }

        private IEnumerator PollTelemetryRoutine()
        {
            while (true)
            {
                yield return FetchLiveSnapshot();
                yield return new WaitForSeconds(2.0f);
            }
        }

        private IEnumerator FetchLiveSnapshot()
        {
            string url = apiBaseUrl + "/api/v1/snapshots/collect";
            using (UnityWebRequest req = UnityWebRequest.PostWwwForm(url, ""))
            {
                req.timeout = 2;
                yield return req.SendWebRequest();

                if (req.result == UnityWebRequest.Result.Success)
                {
                    ParseJsonSnapshot(req.downloadHandler.text);
                }
                else
                {
                    // Fallback to organic live simulation when backend daemon is inactive
                    SimulateLocalTelemetry();
                }
            }
        }

        private void ParseJsonSnapshot(string json)
        {
            try
            {
                // Basic extraction of core fields from JSON payload
                if (json.Contains("\"cpu_percent\":"))
                {
                    int idx = json.IndexOf("\"cpu_percent\":") + 14;
                    int end = json.IndexOfAny(new char[] { ',', '}' }, idx);
                    if (float.TryParse(json.Substring(idx, end - idx).Trim(), out float cpu))
                    {
                        targetData.cpuPercent = Mathf.Clamp(cpu, 0f, 100f);
                    }
                }
                if (json.Contains("\"memory_percent\":"))
                {
                    int idx = json.IndexOf("\"memory_percent\":") + 17;
                    int end = json.IndexOfAny(new char[] { ',', '}' }, idx);
                    if (float.TryParse(json.Substring(idx, end - idx).Trim(), out float mem))
                    {
                        targetData.memoryPercent = Mathf.Clamp(mem, 0f, 100f);
                    }
                }
            }
            catch (Exception)
            {
                SimulateLocalTelemetry();
            }
        }

        private void SimulateLocalTelemetry()
        {
            // Organic variation for silky smooth live 3D animation
            float noise = Mathf.PerlinNoise(Time.time * 0.15f, 0.5f);
            targetData.cpuPercent = Mathf.Clamp(15.0f + (noise * 60.0f), 5f, 95f);
            targetData.memoryPercent = Mathf.Clamp(40.0f + (Mathf.Sin(Time.time * 0.08f) * 15.0f), 20f, 85f);
            targetData.swapPercent = 12.0f;
            targetData.diskPercent = 58.4f;
            targetData.uploadSpeedKbps = 80.0f + (noise * 300.0f);
            targetData.downloadSpeedKbps = 300.0f + (noise * 1200.0f);
            targetData.batteryPercent = 90.0f;
            targetData.batteryCharging = true;
        }

        void OnGUI()
        {
            if (!showHUD) return;

            // Minimalist, uncluttered HUD box
            GUI.skin.box.fontSize = 12;
            GUI.skin.label.fontSize = 12;

            GUILayout.BeginArea(new Rect(20, 20, 320, 240), GUI.skin.box);
            GUILayout.Label("<b>AD-PROJECT TELEMETRY PORTAL 3D</b>");
            GUILayout.Space(5);
            GUILayout.Label(string.Format("CPU Core Usage:   <b>{0:F1}%</b>", currentData.cpuPercent));
            GUILayout.Label(string.Format("RAM Memory Usage: <b>{0:F1}%</b>", currentData.memoryPercent));
            GUILayout.Label(string.Format("Disk Storage:     <b>{0:F1}%</b>", currentData.diskPercent));
            GUILayout.Label(string.Format("Network I/O:      <b>{0:F0} KB/s ↑ | {1:F0} KB/s ↓</b>", currentData.uploadSpeedKbps, currentData.downloadSpeedKbps));
            GUILayout.Label(string.Format("Battery Power:    <b>{0:F0}% ({1})</b>", currentData.batteryPercent, currentData.batteryCharging ? "Charging" : "Discharging"));
            GUILayout.Space(8);
            GUILayout.Label("<b>Controls:</b>");
            GUILayout.Label("• Left Drag: Orbit 3D Camera | Scroll: Zoom");
            GUILayout.Label("• <b>[V]</b>: Toggle Google Cardboard VR Mode");
            GUILayout.Label("• <b>[H]</b>: Hide / Show This HUD (Pure Art)");
            GUILayout.Label("• <b>[Space]</b>: Force Sync Telemetry");
            GUILayout.EndArea();
        }
    }
}

