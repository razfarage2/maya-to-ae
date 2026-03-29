import { useState, useEffect, useRef } from 'react';
import './App.css';

declare global {
  interface Window { require: any; CSInterface: any; }
}

function App() {
  const [status, setStatus] = useState("Ready");
  const [logs, setLogs] = useState<string[]>([]);
  const [mayaPath, setMayaPath] = useState<string>("");

  const [startFrame, setStartFrame] = useState<number>(1);
  const [endFrame, setEndFrame] = useState<number>(1);
  const [isProcessing, setIsProcessing] = useState(false);
  const [frameProgress, setFrameProgress] = useState({ current: 0, total: 0 });

  const SCRIPT_PATH = "G:/maya-to-ae/maya_side/runner.py";
  const SCENE_FILE = "G:/maya-to-ae/data/test_aovs.ma";
  const JSON_OUTPUT_PATH = "G:/maya-to-ae/data/ae_temp_info.json";

  const logsEndRef = useRef<HTMLDivElement>(null);
  useEffect(() => { logsEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [logs]);

  useEffect(() => {
    const detected = findMayaPy();
    if (detected) {
      setMayaPath(detected);
      fetchMetadata(detected);
    }
    else { setStatus("Maya Not Found"); }
  }, []);

  const addLog = (msg: string) => setLogs(prev => [...prev, msg]);

  const findMayaPy = () => {
    const fs = window.require('fs');
    const path = window.require('path');
    const root = "C:\\Program Files\\Autodesk";
    if (!fs.existsSync(root)) return null;
    try {
      const folders = fs.readdirSync(root).filter((f: string) => f.startsWith("Maya20") && !f.includes("lt"));
      folders.sort().reverse();
      for (const f of folders) {
        const exe = path.join(root, f, "bin", "mayapy.exe");
        if (fs.existsSync(exe)) return exe;
      }
    } catch (e) { }
    return null;
  };

  const fetchMetadata = (exe: string) => {
    const { exec } = window.require('child_process');
    const fs = window.require('fs');
    exec(`"${exe}" -u "${SCRIPT_PATH}" "${SCENE_FILE}" --output "${JSON_OUTPUT_PATH}"`, () => {
      if (fs.existsSync(JSON_OUTPUT_PATH)) {
        try {
          const data = JSON.parse(fs.readFileSync(JSON_OUTPUT_PATH, 'utf-8'));
          const info = data.scene_data.scene_info;
          if (info?.frame_range) {
            setStartFrame(info.frame_range[0]);
            setEndFrame(info.frame_range[1]);
            setStatus("Ready");
          }
        } catch (e) { }
      }
    });
  };

  const handleSyncData = () => {
    if (!mayaPath) return;
    setStatus("Syncing 3D Data...");
    setIsProcessing(true);

    const { exec } = window.require('child_process');
    const cmd = `"${mayaPath}" -u "${SCRIPT_PATH}" "${SCENE_FILE}" --output "${JSON_OUTPUT_PATH}"`;

    exec(cmd, (error: any) => {
      if (error) {
        setStatus("Sync Failed");
        addLog("Error exporting data");
        setIsProcessing(false);
        return;
      }

      const cs = new window.CSInterface();
      const cleanPath = JSON_OUTPUT_PATH.replace(/\\/g, "\\\\");
      cs.evalScript(`importSceneData("${cleanPath}")`, (res: string) => {
        addLog(res);
        setStatus(res.includes("Error") ? "Sync Error" : "Data Synced");
        setIsProcessing(false);
      });
    });
  };

  const handleRenderPreview = () => {
    if (!mayaPath) return;
    setIsProcessing(true);
    setStatus("Generating Preview...");

    const totalFrames = (endFrame - startFrame) + 1;
    setFrameProgress({ current: 0, total: totalFrames });

    const { exec } = window.require('child_process');
    const cmd = `"${mayaPath}" -u "${SCRIPT_PATH}" --render --aov preview --start_frame ${startFrame} --end_frame ${endFrame} "${SCENE_FILE}"`;

    const process = exec(cmd);

    process.stdout.on('data', (data: string) => {
      if (data.includes("Rendering frame")) {
        const match = data.match(/Rendering frame (\d+)/);
        if (match) {
          const f = parseInt(match[1]);
          const current = (f - startFrame) + 1;
          setFrameProgress(prev => ({ ...prev, current: current }));
        }
      }
      if (data.includes("RENDER_COMPLETE:")) {
        const rawPath = data.split("RENDER_COMPLETE:")[1].trim();

        addLog(`Python Path: ${rawPath}`);

        const path = rawPath;
        const cs = new window.CSInterface();
        const clean = path.replace(/\\/g, "\\\\");

        cs.evalScript(`importAndOrganize("${clean}", "Maya_Preview")`, (res: string) => {
          addLog(`AE: ${res}`);
        });
      }
    });

    process.on('close', (code: number) => {
      setIsProcessing(false);
      if (code === 0) setStatus("Preview Ready");
      else setStatus("Finished");
    });
  };

  return (
    <div className="app-container">
      <div className="header">
        <div className="title">MAYA LIVE LINK</div>
        <div className={`status-dot ${mayaPath ? 'on' : 'off'}`}></div>
      </div>

      <div className="panel info-panel">
        <div className="file-name">{SCENE_FILE.split('/').pop()}</div>
        <div className="range-inputs">
          <input type="number" value={startFrame} onChange={e => setStartFrame(Number(e.target.value))} />
          <span>to</span>
          <input type="number" value={endFrame} onChange={e => setEndFrame(Number(e.target.value))} />
        </div>
      </div>

      <div className="action-area">
        <button className="primary-btn data-btn" disabled={isProcessing} onClick={handleSyncData}>
          <div className="icon">📡</div>
          <div className="btn-text">
            <span className="main">Sync Data</span>
            <span className="sub">Camera & Locators</span>
          </div>
        </button>

        <button className="primary-btn preview-btn" disabled={isProcessing} onClick={handleRenderPreview}>
          <div className="icon">▶️</div>
          <div className="btn-text">
            <span className="main">Get Preview</span>
            <span className="sub">Viewport Render</span>
          </div>
        </button>
      </div>

      {isProcessing && frameProgress.total > 0 && (
        <div className="progress-section">
          <div className="loader-text">
            Rendering Frame {frameProgress.current}/{frameProgress.total}
          </div>
          <div className="progress-bar">
            <div className="fill" style={{ width: `${(frameProgress.current / frameProgress.total) * 100}%` }}></div>
          </div>
        </div>
      )}

      <div className="status-bar">
        {status}
      </div>

      <div className="logs">
        {logs.slice(-3).map((l, i) => <div key={i}>{l}</div>)}
        <div ref={logsEndRef} />
      </div>
    </div>
  );
}

export default App;