import { useState } from "react";

function BacktestConfigForm({ strategy, onSubmit }) {
  const [ticker, setTicker] = useState("AAPL");
  const [startDate, setStartDate] = useState("2020-01-01");
  const [endDate, setEndDate] = useState("2024-01-01");
  const [startingCash, setStartingCash] = useState(10000);

  function handleSubmit() {
    const config = {
      strategy_id: strategy.type === "preset" ? strategy.strategyId : "custom_nlp",
      ticker,
      start_date: startDate,
      end_date: endDate,
      starting_cash: Number(startingCash),
      strategy_params: {},
      strategy_code: strategy.type === "nlp" ? strategy.generatedCode : null,
    };
    onSubmit(config);
  }

  const isReady = strategy && ticker && startDate && endDate && startingCash > 0;

  return (
    <div style={{ border: "1px solid #ccc", padding: "1rem", borderRadius: "8px", marginTop: "1rem" }}>
      <h2>2. Configure Backtest</h2>

      <div style={{ marginBottom: "0.5rem" }}>
        <label>Ticker: </label>
        <select value={ticker} onChange={(e) => setTicker(e.target.value)}>
          <option value="AAPL">AAPL</option>
          <option value="MSFT">MSFT</option>
          <option value="SPY">SPY</option>
        </select>
      </div>

      <div style={{ marginBottom: "0.5rem" }}>
        <label>Start Date: </label>
        <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
      </div>

      <div style={{ marginBottom: "0.5rem" }}>
        <label>End Date: </label>
        <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
      </div>

      <div style={{ marginBottom: "0.5rem" }}>
        <label>Starting Cash ($): </label>
        <input
          type="number"
          value={startingCash}
          onChange={(e) => setStartingCash(e.target.value)}
          min="100"
        />
      </div>

      <button onClick={handleSubmit} disabled={!isReady}>
        Run Backtest
      </button>
    </div>
  );
}

export default BacktestConfigForm;

