# ISD — 3D Telemetry Portal & VR Experience

An uncluttered, minimalist 3D animation and Virtual Reality portal visualizing all system usages present in the **AD Project** real-time monitoring engine.

---

## 1. System Usages Visualized

Every metric captured by `ad-project` is translated into a clean, aesthetic 3D element:

| Metric | 3D Visual Element | Animation Behavior |
| :--- | :--- | :--- |
| **CPU Usage** | Central Faceted Crystal Core | Rotates smoothly around multiple axes (speed $\propto$ CPU %). Emits breathing pulse and transitions color from cool Cyan ($<50\%$) to warm Amber ($50\text{--}80\%$) to Crimson ($>80\%$). |
| **RAM Memory** | Concentric Outer Torus Ring | Rotates horizontally around the core, expanding and glowing with RAM utilization %. |
| **Swap Memory** | Inner Tilted Torus Ring | Contra-rotates along an inclined plane proportional to Swap usage. |
| **Disk Storage** | Tiered Cylindrical Platters | Hover gently beneath the core with subtle sine-wave float and radial leveling. |
| **Network I/O** | Dual Beacon Pillars & Particle Streams | Left pillar: Upload stream (ascending blue particles). Right pillar: Download stream (descending green particles). Stream speeds scale with bandwidth. |
| **Battery Power** | Floating Energy Capsule | Hovering cylindrical cell whose illuminated fill matches battery charge percentage. |
| **Active Processes** | Holographic Process Pillars | Five sleek pillars in an arc representing the top CPU-consuming processes. |

---

## 2. Interactive & VR Controls

The portal provides an uncluttered experience with interactive camera controls and Google Cardboard VR touch:

- **Orbit Camera (Default):**
  - **Left Click + Drag:** Smooth 3D orbital camera rotation around the core.
  - **Mouse Scroll:** Zoom in and out.
  - **[R]:** Reset camera to default perspective.
- **VR Touch (Google Cardboard Mode):**
  - **[V] or "VR Touch" button:** Instantly toggles between standard single-camera orbit and stereoscopic dual-camera split-screen mode for Google Cardboard VR headsets.
- **Clean Art / HUD Toggle:**
  - **[H] or "Toggle HUD" button:** Hides the diagnostic data overlay to enjoy a pure, distraction-free 3D art visualization.

---

## 3. How to Launch

### Option A: Web 3D Portal (Instant Browser Launch)
Run with the CLI `--portal` flag to open the 3D portal in your default browser:
```bash
python main.py --portal
```
Or with FastAPI running (`uvicorn ad_project.api.app:app`):
Visit [http://127.0.0.1:8000/portal](http://127.0.0.1:8000/portal) or [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

### Option B: Unity Standalone macOS Application
Launch the precompiled Unity 6 standalone application:
```bash
open ISD/Unity/Builds/TelemetryPortal.app
```

---

## 4. Rebuilding Assets

- **Blender 3D Asset:**
  ```bash
  /Applications/Blender.app/Contents/MacOS/Blender --background --python ISD/Blender/create_telemetry_core.py
  ```
- **Unity 6 Application Build:**
  ```bash
  /Applications/Unity/Hub/Editor/6000.6.0f1/Unity.app/Contents/MacOS/Unity -batchmode -quit -projectPath ISD/Unity -executeMethod BuildTelemetryPortal.GenerateSceneAndBuild -logFile unity_build.log
  ```

