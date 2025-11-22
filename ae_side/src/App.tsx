import { useState, useEffect } from 'react';

declare global {
  interface Window {
    require: any;
    CSInterface: any;
  }
}

function App() {
  const [status, setStatus] = useState("Ready");
  const [logs, setLogs] = useState<string[]>([]);
  const [mayaPath, setMayaPath] = useState<string>("");

  const SCRIPT_PATH = "G:/maya-to-ae/maya_side/runner.py";
  const SCENE_FILE = "G:/maya-to-ae/data/test_aovs.ma";

  useEffect(() => {
    const detectedPath = findMayaPy();
    if (detectedPath) {
      setMayaPath(detectedPath);
      addLog(`✓ Auto-detected Maya at: ${detectedPath}`);
    } else {
      setStatus("Maya Not Found");
      addLog("Error: Could not find Maya in default locations.");
    }
  }, []);

  const findMayaPy = () => {
    const fs = window.require('fs');
    const path = window.require('path');

    const autodeskDir = "C:\\Program Files\\Autodesk";

    if (!fs.existsSync(autodeskDir)) return null;

    try {
      const folders = fs.readdirSync(autodeskDir);

      const mayaFolders = folders.filter((f: string) => f.startsWith("Maya20") && !f.includes("lt"));
      mayaFolders.sort().reverse();

      for (const folder of mayaFolders) {
        const exePath = path.join(autodeskDir, folder, "bin", "mayapy.exe");
        if (fs.existsSync(exePath)) {
          return exePath;
        }
      }
    } catch (e: any) {
      addLog("Error searching for Maya: " + e.message);
    }
    return null;
  };

  const handleRender = () => {
    if (!mayaPath) {
      addLog("Cannot render: Maya path not found.");
      return;
    }

    setStatus("Initializing Render...");

    const { exec } = window.require('child_process');
    const command = `"${mayaPath}" -u "${SCRIPT_PATH}" --render --aov diffuse --frame 1 "${SCENE_FILE}"`;

    addLog(`Running Command...`);

    exec(command, (error: any, stdout: string, stderr: string) => {
      const allOutput = stdout + "\n" + stderr;

      if (stdout) addLog(`Python Out: ${stdout}`);
      if (stderr) addLog(`Python Err: ${stderr}`);
      if (error) addLog(`Process Exit Code: ${error.code} (Likely ADP crash - ignoring if render worked)`);

      if (allOutput.includes("RENDER_COMPLETE:")) {
        setStatus("Importing to AE...");

        const lines = allOutput.split('\n');
        const successLine = lines.find((line: string) => line.includes("RENDER_COMPLETE:"));

        if (successLine) {
          const filePath = successLine.split("RENDER_COMPLETE:")[1].trim();

          const csInterface = new window.CSInterface();
          const cleanPath = filePath.replace(/\\/g, "\\\\");

          addLog(`Importing: ${cleanPath}`);

          csInterface.evalScript(`importExrFile("${cleanPath}")`, (result: string) => {
            addLog(`AE Result: ${result}`);
            setStatus("Done!");
          });
          return;
        }
      }

      if (error) {
        setStatus("Failed");
        addLog("Critical: Render failed and no output image was confirmed.");
      }
    });
  };

  const addLog = (msg: string) => {
    setLogs(prev => [...prev, msg]);
    console.log(msg);
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif', color: '#ffffff', background: '#232323', minHeight: '100vh' }}>
      <h2>Maya Bridge</h2>

      <div style={{ marginBottom: '20px' }}>
        <button
          onClick={handleRender}
          disabled={!mayaPath}
          style={{
            padding: '10px 20px',
            fontSize: '16px',
            cursor: mayaPath ? 'pointer' : 'not-allowed',
            backgroundColor: mayaPath ? '#00a8ff' : '#555',
            border: 'none',
            borderRadius: '4px',
            color: 'white'
          }}
        >
          {mayaPath ? "Render Diffuse (Test)" : "Maya Not Found"}
        </button>
      </div>

      <div style={{ border: '1px solid #444', padding: '10px', borderRadius: '4px', background: '#333', maxHeight: '300px', overflowY: 'auto' }}>
        <strong>Status:</strong> {status}
        <hr style={{ borderColor: '#555' }} />
        <div style={{ fontSize: '11px', fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
          {logs.map((log, i) => <div key={i} style={{ marginBottom: '5px', borderBottom: '1px solid #444' }}>{log}</div>)}
        </div>
      </div>
    </div>
  );
}

export default App;