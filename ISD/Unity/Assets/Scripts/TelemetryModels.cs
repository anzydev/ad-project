using System;
using System.Collections.Generic;
using UnityEngine;

namespace TelemetryPortal
{
    [Serializable]
    public class TelemetrySnapshot
    {
        public float cpuPercent = 25.0f;
        public float memoryPercent = 42.0f;
        public float swapPercent = 12.0f;
        public float diskPercent = 58.0f;
        public float uploadSpeedKbps = 120.0f;
        public float downloadSpeedKbps = 850.0f;
        public float batteryPercent = 88.0f;
        public bool batteryCharging = true;
        public int processCount = 184;
        public List<ProcessItem> topProcesses = new List<ProcessItem>();
    }

    [Serializable]
    public class ProcessItem
    {
        public string name = "system";
        public float cpuPercent = 5.0f;
        public float memPercent = 2.0f;

        public ProcessItem(string n, float cpu, float mem)
        {
            name = n;
            cpuPercent = cpu;
            memPercent = mem;
        }
    }
}

