import { useState } from "react";
import StrategySelector from "./components/StrategySelector";
import BacktestConfigForm from "./components/BacktestConfigForm";
import ResultsDashboard from "./components/ResultsDashboard";
import { submitBacktest, pollBacktest } from "./api/client";

function App() {
  const [strategy, setStrategy] = useState(null);
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  function clearRunState() {
    setResult(null);
    setError(null);
    setStatus(null);
  }

  function handleStrategyChosen(newStrategy) {
    setStrategy(newStrategy);
    clearRunState();
  }

  function handleModeChange() {
    setStrategy(null);
    clearRunState();
  }

  async function handleSubmit(config) {
    setError(null);
    setResult(null);
    try {
      const submission = await submitBacktest(config);
      setStatus(submission.status);

      const finalResult = await pollBacktest(submission.id, (newStatus) => {
        setStatus(newStatus);
      });

      if (finalResult.status === "done") {
        setResult(finalResult.config.results);
      } else {
        setError("Backtest failed. Please check your configuration and try again.");
      }
    } catch (err) {
      setError(err.message || "Something went wrong submitting the backtest.");
    }
  }

  return (
    <div style={{ maxWidth: "700px", margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>Backtesting Engine</h1>

      <StrategySelector onStrategyChosen={handleStrategyChosen} onModeChange={handleModeChange} />

      {strategy && (
        <BacktestConfigForm strategy={strategy} onSubmit={handleSubmit} />
      )}

      {status && status !== "done" && status !== "failed" && (
        <p style={{ marginTop: "1rem" }}>Status: {status}...</p>
      )}

      {error && <p style={{ color: "red", marginTop: "1rem" }}>{error}</p>}

      {result && (
        <ResultsDashboard
          results={result}
          biasCheck={strategy?.type === "nlp" ? strategy.biasCheck : null}
        />
      )}
    </div>
  );
}

export default App;
