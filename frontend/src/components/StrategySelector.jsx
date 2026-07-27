import { useState, useEffect } from "react";
import { getStrategies, generateStrategyFromDescription } from "../api/client";

function StrategySelector({ onStrategyChosen, onModeChange }) {
  const [mode, setMode] = useState("preset");
  const [presets, setPresets] = useState([]);
  const [selectedPresetId, setSelectedPresetId] = useState("");
  const [description, setDescription] = useState("");
  const [nlpLoading, setNlpLoading] = useState(false);
  const [nlpError, setNlpError] = useState(null);
  const [showCodeEditor, setShowCodeEditor] = useState(false);
  const [customCode, setCustomCode] = useState("");

  useEffect(() => {
    getStrategies().then(setPresets).catch(console.error);
  }, []);

  function handleModeSwitch(newMode) {
    setMode(newMode);
    setSelectedPresetId("");
    if (onModeChange) onModeChange();
  }

  function handlePresetSelect(presetId) {
    setSelectedPresetId(presetId);
    onStrategyChosen({ type: "preset", strategyId: presetId });
  }

  async function handleNlpSubmit() {
    setNlpLoading(true);
    setNlpError(null);
    try {
      const result = await generateStrategyFromDescription(description);
      if (result.accepted) {
        onStrategyChosen({
          type: "nlp",
          description,
          generatedCode: result.code,
          biasCheck: result.bias_check,
        });
      }
    } catch (error) {
      setNlpError(
        error.response?.data?.detail || "Strategy generation failed. Try rephrasing your description."
      );
    } finally {
      setNlpLoading(false);
    }
  }

  return (
    <div style={{ border: "1px solid #ccc", padding: "1rem", borderRadius: "8px" }}>
      <h2>1. Choose a Strategy</h2>

      <div style={{ marginBottom: "1rem" }}>
        <button onClick={() => handleModeSwitch("preset")} disabled={mode === "preset"}>
          Existing Strategy
        </button>
        <button onClick={() => handleModeSwitch("nlp")} disabled={mode === "nlp"}>
          Describe in Plain English
        </button>
      </div>

      {mode === "preset" && (
        <div>
          {presets.map((preset) => (
            <div key={preset.id} style={{ marginBottom: "0.5rem" }}>
              <label>
                <input
                  type="radio"
                  name="preset"
                  value={preset.id}
                  checked={selectedPresetId === preset.id}
                  onChange={() => handlePresetSelect(preset.id)}
                />
                <strong> {preset.name}</strong> — {preset.description}
              </label>
            </div>
          ))}
        </div>
      )}

      {mode === "nlp" && (
        <div>
          <textarea
            rows={3}
            style={{ width: "100%" }}
            placeholder="e.g. Buy when the closing price is higher than the previous day's close, sell when it's lower."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <button onClick={handleNlpSubmit} disabled={nlpLoading || !description}>
            {nlpLoading ? "Generating & Validating..." : "Generate Strategy"}
          </button>
          {nlpError && <p style={{ color: "red" }}>{nlpError}</p>}
        </div>
      )}

      <div style={{ marginTop: "1rem" }}>
        <label>
          <input
            type="checkbox"
            checked={showCodeEditor}
            onChange={(e) => setShowCodeEditor(e.target.checked)}
          />
          {" "}Advanced: write strategy code directly
        </label>
        {showCodeEditor && (
          <textarea
            rows={8}
            style={{ width: "100%", fontFamily: "monospace" }}
            placeholder="# Custom strategy code execution coming in a future update"
            value={customCode}
            onChange={(e) => setCustomCode(e.target.value)}
            disabled
          />
        )}
      </div>
    </div>
  );
}

export default StrategySelector;
