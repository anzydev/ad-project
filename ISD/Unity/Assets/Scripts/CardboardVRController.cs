using System;
using UnityEngine;

namespace TelemetryPortal
{
    public class CardboardVRController : MonoBehaviour
    {
        [Header("Cameras")]
        public Camera monoCamera;
        public Camera leftEyeCamera;
        public Camera rightEyeCamera;
        public GameObject vrRig;

        [Header("VR Settings")]
        public bool isVRMode = false;
        public float interPupillaryDistance = 0.064f; // 64mm standard IPD
        public float lookSensitivity = 2.5f;

        private float pitch = 0f;
        private float yaw = 0f;

        void Start()
        {
            ApplyMode();
        }

        void Update()
        {
            // 'V' key toggles Google Cardboard VR touch mode
            if (Input.GetKeyDown(KeyCode.V))
            {
                ToggleVR();
            }

            if (isVRMode)
            {
                HandleVRHeadLook();
            }
        }

        public void ToggleVR()
        {
            isVRMode = !isVRMode;
            ApplyMode();
        }

        public void SetVRMode(bool enable)
        {
            isVRMode = enable;
            ApplyMode();
        }

        private void ApplyMode()
        {
            if (monoCamera != null)
            {
                monoCamera.enabled = !isVRMode;
            }

            if (leftEyeCamera != null && rightEyeCamera != null)
            {
                leftEyeCamera.enabled = isVRMode;
                rightEyeCamera.enabled = isVRMode;

                if (isVRMode)
                {
                    // Split screen: left eye takes left half [0, 0, 0.5, 1], right takes right half [0.5, 0, 0.5, 1]
                    leftEyeCamera.rect = new Rect(0.0f, 0.0f, 0.5f, 1.0f);
                    rightEyeCamera.rect = new Rect(0.5f, 0.0f, 0.5f, 1.0f);

                    // Position eyes according to IPD
                    leftEyeCamera.transform.localPosition = new Vector3(-interPupillaryDistance * 0.5f, 0f, 0f);
                    rightEyeCamera.transform.localPosition = new Vector3(interPupillaryDistance * 0.5f, 0f, 0f);
                }
            }
        }

        private void HandleVRHeadLook()
        {
            if (Input.GetMouseButton(0) || Input.GetMouseButton(1))
            {
                yaw += Input.GetAxis("Mouse X") * lookSensitivity;
                pitch -= Input.GetAxis("Mouse Y") * lookSensitivity;
                pitch = Mathf.Clamp(pitch, -80f, 80f);

                if (vrRig != null)
                {
                    vrRig.transform.localRotation = Quaternion.Euler(pitch, yaw, 0f);
                }
            }
        }
    }
}

