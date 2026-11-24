using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using TelemetryPortal;

public static class BuildTelemetryPortal
{
    private const string ScenePath = "Assets/Generated/TelemetryPortal.unity";
    private const string BuildPath = "Builds/TelemetryPortal.app";

    static Material CreateMat(string name, Color color, float metallic = 0.5f, float gloss = 0.5f, Color? emission = null)
    {
        string matPath = "Assets/Generated/" + name + ".mat";
        Material mat = AssetDatabase.LoadAssetAtPath<Material>(matPath);
        if (mat == null)
        {
            mat = new Material(Shader.Find("Standard"));
            AssetDatabase.CreateAsset(mat, matPath);
        }
        mat.color = color;
        mat.SetFloat("_Metallic", metallic);
        mat.SetFloat("_Glossiness", gloss);
        if (emission.HasValue)
        {
            mat.EnableKeyword("_EMISSION");
            mat.SetColor("_EmissionColor", emission.Value);
        }
        EditorUtility.SetDirty(mat);
        return mat;
    }

    [MenuItem("TelemetryPortal/Build Scene and App")]
    public static void GenerateSceneAndBuild()
    {
        Debug.Log("Generating TelemetryPortal 3D Scene...");
        if (!Directory.Exists("Assets/Generated")) Directory.CreateDirectory("Assets/Generated");
        if (!Directory.Exists("Builds")) Directory.CreateDirectory("Builds");

        Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

        // 1. Materials
        Material matVoid = CreateMat("MatVoid", new Color(0.04f, 0.05f, 0.08f), 0.1f, 0.1f);
        Material matCore = CreateMat("MatCpuCore", new Color(0.1f, 0.8f, 1.0f), 0.7f, 0.8f, new Color(0.1f, 0.8f, 1.0f) * 1.5f);
        Material matRam = CreateMat("MatRamRing", new Color(0.2f, 0.9f, 0.7f), 0.8f, 0.8f, new Color(0.2f, 0.9f, 0.7f) * 0.8f);
        Material matSwap = CreateMat("MatSwapRing", new Color(0.7f, 0.3f, 1.0f), 0.8f, 0.8f, new Color(0.7f, 0.3f, 1.0f) * 0.8f);
        Material matDisk = CreateMat("MatDisk", new Color(0.15f, 0.2f, 0.28f), 0.9f, 0.7f);
        Material matBeacon = CreateMat("MatBeacon", new Color(0.1f, 0.6f, 0.9f), 0.6f, 0.6f, new Color(0.1f, 0.6f, 0.9f) * 1.2f);
        Material matBattery = CreateMat("MatBattery", new Color(0.2f, 0.9f, 0.4f), 0.5f, 0.8f, new Color(0.2f, 0.9f, 0.4f) * 1.0f);
        Material matProcess = CreateMat("MatProcess", new Color(0.25f, 0.35f, 0.5f), 0.8f, 0.7f);

        // 2. Lighting & Sky
        GameObject dirLightGo = new GameObject("Directional Light");
        Light dirLight = dirLightGo.AddComponent<Light>();
        dirLight.type = LightType.Directional;
        dirLight.intensity = 0.8f;
        dirLight.color = new Color(0.85f, 0.9f, 1.0f);
        dirLightGo.transform.rotation = Quaternion.Euler(45f, -30f, 0f);

        // 3. Dark Void Pedestal Floor
        GameObject floor = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        floor.name = "VoidPedestal";
        floor.transform.position = new Vector3(0f, -0.05f, 0f);
        floor.transform.localScale = new Vector3(14f, 0.1f, 14f);
        floor.GetComponent<Renderer>().sharedMaterial = matVoid;

        // 4. Central CPU Core
        GameObject cpuCore = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        cpuCore.name = "CpuCore";
        cpuCore.transform.position = new Vector3(0f, 2.5f, 0f);
        cpuCore.transform.localScale = Vector3.one * 1.2f;
        cpuCore.GetComponent<Renderer>().sharedMaterial = matCore;

        GameObject coreLightGo = new GameObject("CorePointLight");
        coreLightGo.transform.parent = cpuCore.transform;
        coreLightGo.transform.localPosition = Vector3.zero;
        Light coreLight = coreLightGo.AddComponent<Light>();
        coreLight.type = LightType.Point;
        coreLight.range = 10f;
        coreLight.intensity = 2.0f;
        coreLight.color = new Color(0.1f, 0.8f, 1.0f);

        // 5. Memory Rings (RAM & Swap)
        GameObject ramRing = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        ramRing.name = "RamRing";
        ramRing.transform.position = new Vector3(0f, 2.5f, 0f);
        ramRing.transform.localScale = new Vector3(3.6f, 0.04f, 3.6f);
        ramRing.GetComponent<Renderer>().sharedMaterial = matRam;

        GameObject swapRing = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        swapRing.name = "SwapRing";
        swapRing.transform.position = new Vector3(0f, 2.5f, 0f);
        swapRing.transform.rotation = Quaternion.Euler(45f, 25f, 0f);
        swapRing.transform.localScale = new Vector3(2.6f, 0.03f, 2.6f);
        swapRing.GetComponent<Renderer>().sharedMaterial = matSwap;

        // 6. Disk Platters
        GameObject[] diskPlatters = new GameObject[3];
        for (int i = 0; i < 3; i++)
        {
            GameObject platter = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            platter.name = "DiskPlatter_" + i;
            platter.transform.position = new Vector3(0f, 0.25f + (i * 0.35f), 0f);
            float radius = 4.2f - (i * 0.4f);
            platter.transform.localScale = new Vector3(radius, 0.12f, radius);
            platter.GetComponent<Renderer>().sharedMaterial = matDisk;
            diskPlatters[i] = platter;
        }

        // 7. Network Beacons and Particles
        GameObject upBeacon = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        upBeacon.name = "NetUploadBeacon";
        upBeacon.transform.position = new Vector3(-3.5f, 1.5f, 0f);
        upBeacon.transform.localScale = new Vector3(0.25f, 1.5f, 0.25f);
        upBeacon.GetComponent<Renderer>().sharedMaterial = matBeacon;

        GameObject upParticlesGo = new GameObject("UploadParticles");
        upParticlesGo.transform.parent = upBeacon.transform;
        upParticlesGo.transform.localPosition = new Vector3(0f, -0.9f, 0f);
        upParticlesGo.transform.localRotation = Quaternion.Euler(-90f, 0f, 0f);
        ParticleSystem upPs = upParticlesGo.AddComponent<ParticleSystem>();
        var upMain = upPs.main;
        upMain.startSpeed = 2.5f;
        upMain.startSize = 0.08f;
        upMain.startColor = new Color(0.2f, 0.8f, 1.0f);
        upMain.startLifetime = 1.2f;

        GameObject downBeacon = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        downBeacon.name = "NetDownloadBeacon";
        downBeacon.transform.position = new Vector3(3.5f, 1.5f, 0f);
        downBeacon.transform.localScale = new Vector3(0.25f, 1.5f, 0.25f);
        downBeacon.GetComponent<Renderer>().sharedMaterial = matBeacon;

        GameObject downParticlesGo = new GameObject("DownloadParticles");
        downParticlesGo.transform.parent = downBeacon.transform;
        downParticlesGo.transform.localPosition = new Vector3(0f, 0.9f, 0f);
        downParticlesGo.transform.localRotation = Quaternion.Euler(90f, 0f, 0f);
        ParticleSystem downPs = downParticlesGo.AddComponent<ParticleSystem>();
        var downMain = downPs.main;
        downMain.startSpeed = 2.5f;
        downMain.startSize = 0.08f;
        downMain.startColor = new Color(0.2f, 1.0f, 0.5f);
        downMain.startLifetime = 1.2f;

        // 8. Battery Power Cell
        GameObject batteryGo = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        batteryGo.name = "BatteryCell";
        batteryGo.transform.position = new Vector3(0f, 1.0f, -2.8f);
        batteryGo.transform.localScale = new Vector3(0.6f, 0.8f, 0.6f);
        batteryGo.GetComponent<Renderer>().sharedMaterial = matBattery;

        GameObject batteryFillGo = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        batteryFillGo.name = "BatteryFill";
        batteryFillGo.transform.parent = batteryGo.transform;
        batteryFillGo.transform.localPosition = Vector3.zero;
        batteryFillGo.transform.localScale = new Vector3(0.9f, 0.8f, 0.9f);
        batteryFillGo.GetComponent<Renderer>().sharedMaterial = matBattery;

        // 9. Process Pillars (5 in a clean arc)
        GameObject[] procPillars = new GameObject[5];
        for (int i = 0; i < 5; i++)
        {
            float angle = Mathf.Lerp(-60f, 60f, i / 4.0f) * Mathf.Deg2Rad;
            float px = Mathf.Sin(angle) * 3.8f;
            float pz = Mathf.Cos(angle) * 3.8f;

            GameObject pillar = GameObject.CreatePrimitive(PrimitiveType.Cube);
            pillar.name = "ProcessPillar_" + i;
            pillar.transform.position = new Vector3(px, 0.5f, pz);
            pillar.transform.localScale = new Vector3(0.35f, 0.8f, 0.35f);
            pillar.GetComponent<Renderer>().sharedMaterial = matProcess;
            procPillars[i] = pillar;
        }

        // 10. Cameras & VR Rig
        GameObject camRigGo = new GameObject("CameraRig");
        camRigGo.transform.position = new Vector3(0f, 2.0f, 0f);

        GameObject camPitchGo = new GameObject("CameraPitch");
        camPitchGo.transform.parent = camRigGo.transform;
        camPitchGo.transform.localPosition = Vector3.zero;

        // Main Desktop Orbit Camera
        GameObject monoCamGo = new GameObject("MainCamera");
        monoCamGo.transform.parent = camPitchGo.transform;
        monoCamGo.transform.localPosition = new Vector3(0f, 0f, -11.0f);
        Camera monoCam = monoCamGo.AddComponent<Camera>();
        monoCam.backgroundColor = new Color(0.04f, 0.05f, 0.08f);
        monoCam.clearFlags = CameraClearFlags.SolidColor;
        monoCam.nearClipPlane = 0.2f;
        monoCamGo.tag = "MainCamera";

        // Google Cardboard Stereo VR Rig
        GameObject vrRigGo = new GameObject("CardboardVRRig");
        vrRigGo.transform.parent = camPitchGo.transform;
        vrRigGo.transform.localPosition = new Vector3(0f, 0f, -11.0f);

        GameObject leftEyeGo = new GameObject("LeftEyeCamera");
        leftEyeGo.transform.parent = vrRigGo.transform;
        leftEyeGo.transform.localPosition = new Vector3(-0.032f, 0f, 0f);
        Camera leftCam = leftEyeGo.AddComponent<Camera>();
        leftCam.backgroundColor = new Color(0.04f, 0.05f, 0.08f);
        leftCam.clearFlags = CameraClearFlags.SolidColor;
        leftCam.rect = new Rect(0.0f, 0.0f, 0.5f, 1.0f);
        leftCam.enabled = false;

        GameObject rightEyeGo = new GameObject("RightEyeCamera");
        rightEyeGo.transform.parent = vrRigGo.transform;
        rightEyeGo.transform.localPosition = new Vector3(0.032f, 0f, 0f);
        Camera rightCam = rightEyeGo.AddComponent<Camera>();
        rightCam.backgroundColor = new Color(0.04f, 0.05f, 0.08f);
        rightCam.clearFlags = CameraClearFlags.SolidColor;
        rightCam.rect = new Rect(0.5f, 0.0f, 0.5f, 1.0f);
        rightCam.enabled = false;

        // 11. Controller Components
        GameObject controllerGo = new GameObject("TelemetryPortalManager");
        TelemetryPortalController controller = controllerGo.AddComponent<TelemetryPortalController>();
        controller.cpuCore = cpuCore.transform;
        controller.cpuCoreLight = coreLight;
        controller.ramRing = ramRing.transform;
        controller.swapRing = swapRing.transform;
        controller.diskPlatters = new Transform[] { diskPlatters[0].transform, diskPlatters[1].transform, diskPlatters[2].transform };
        controller.uploadBeacon = upBeacon.transform;
        controller.downloadBeacon = downBeacon.transform;
        controller.uploadParticles = upPs;
        controller.downloadParticles = downPs;
        controller.batteryCell = batteryGo.transform;
        controller.batteryFill = batteryFillGo.transform;
        controller.processPillars = new Transform[] {
            procPillars[0].transform, procPillars[1].transform, procPillars[2].transform,
            procPillars[3].transform, procPillars[4].transform
        };
        controller.cameraRig = camRigGo.transform;
        controller.cameraPitchNode = camPitchGo.transform;
        controller.mainCamera = monoCam;
        controller.coreMaterial = matCore;
        controller.ramMaterial = matRam;
        controller.diskMaterial = matDisk;
        controller.batteryMaterial = matBattery;

        CardboardVRController vrCtrl = controllerGo.AddComponent<CardboardVRController>();
        vrCtrl.monoCamera = monoCam;
        vrCtrl.leftEyeCamera = leftCam;
        vrCtrl.rightEyeCamera = rightCam;
        vrCtrl.vrRig = vrRigGo;

        // Save Scene
        EditorSceneManager.SaveScene(scene, ScenePath);
        Debug.Log("Scene saved cleanly at " + ScenePath);

        // Build Application
        BuildPlayerOptions buildOptions = new BuildPlayerOptions();
        buildOptions.scenes = new string[] { ScenePath };
        buildOptions.locationPathName = BuildPath;
        buildOptions.target = BuildTarget.StandaloneOSX;
        buildOptions.options = BuildOptions.None;

        Debug.Log("Starting Unity Player Build to " + BuildPath + "...");
        UnityEditor.Build.Reporting.BuildReport report = BuildPipeline.BuildPlayer(buildOptions);
        if (report.summary.result != UnityEditor.Build.Reporting.BuildResult.Succeeded)
        {
            throw new Exception("Build failed with result: " + report.summary.result + " (Errors: " + report.summary.totalErrors + ")");
        }

        Debug.Log("SUCCESS: TelemetryPortal.app built successfully at " + BuildPath);
    }
}

