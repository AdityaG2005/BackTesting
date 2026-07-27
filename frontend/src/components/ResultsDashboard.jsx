import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

function ResultsDashboard({ results, biasCheck }) {
  const metrics = [
    { label: "Final Value", value: `$${results.final_value.toLocaleString(undefined, { maximumFractionDigits: 2 })}` },
    { label: "CAGR", value: `${(results.cagr * 100).toFixed(2)}%` },
    { label: "Sharpe Ratio", value: results.sharpe.toFixed(2) },
    { label: "Sortino Ratio", value: results.sortino.toFixed(2) },
    { label: "Max Drawdown", value: `${(results.max_drawdown * 100).toFixed(2)}%` },
    { label: "Win Rate", value: `${(results.win_rate * 100).toFixed(2)}%` },
    { label: "Total Trades", value: results.total_trades },
  ];

  const chartData = (results.equity_curve || []).map((point) => ({
    date: point.timestamp.split("T")[0],
    value: point.value,
  }));

  const trades = results.trades || [];

  return (
    <div style={{ border: "1px solid #ccc", padding: "1rem", borderRadius: "8px", marginTop: "1rem" }}>
      <h2>3. Results</h2>

      {biasCheck && (
        <div
          style={{
            padding: "0.5rem 0.75rem",
            borderRadius: "6px",
            marginBottom: "1rem",
            backgroundColor: biasCheck.passed ? "#e6f4ea" : "#fdecea",
            color: biasCheck.passed ? "#1e7e34" : "#c0392b",
            fontWeight: "bold",
          }}
        >
          Lookahead-Bias Check: {biasCheck.passed ? "PASS" : "FAIL"}
          {" "}({biasCheck.checked_points} points checked)
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "0.75rem", marginBottom: "1.5rem" }}>
        {metrics.map((metric) => (
          <div
            key={metric.label}
            style={{ border: "1px solid #eee", borderRadius: "6px", padding: "0.75rem", textAlign: "center" }}
          >
            <div style={{ fontSize: "0.85rem", color: "#666" }}>{metric.label}</div>
            <div style={{ fontSize: "1.25rem", fontWeight: "bold" }}>{metric.value}</div>
          </div>
        ))}
      </div>

      {chartData.length > 0 && (
        <div style={{ marginBottom: "1.5rem" }}>
          <h3>Equity Curve</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#2563eb" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {trades.length > 0 && (
        <div>
          <h3>Trade Log</h3>
          <div style={{ maxHeight: "300px", overflowY: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
              <thead>
                <tr style={{ borderBottom: "2px solid #ccc", textAlign: "left" }}>
                  <th style={{ padding: "0.4rem" }}>Entry Date</th>
                  <th style={{ padding: "0.4rem" }}>Exit Date</th>
                  <th style={{ padding: "0.4rem" }}>Qty</th>
                  <th style={{ padding: "0.4rem" }}>Entry Price</th>
                  <th style={{ padding: "0.4rem" }}>Exit Price</th>
                  <th style={{ padding: "0.4rem" }}>P&L</th>
                </tr>
              </thead>
              <tbody>
                {trades.map((trade, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #eee" }}>
                    <td style={{ padding: "0.4rem" }}>{trade.entry_timestamp?.split("T")[0]}</td>
                    <td style={{ padding: "0.4rem" }}>
                      {trade.is_open ? "OPEN" : trade.exit_timestamp?.split("T")[0]}
                    </td>
                    <td style={{ padding: "0.4rem" }}>{trade.quantity}</td>
                    <td style={{ padding: "0.4rem" }}>${trade.entry_price.toFixed(2)}</td>
                    <td style={{ padding: "0.4rem" }}>
                      {trade.exit_price ? `$${trade.exit_price.toFixed(2)}` : "—"}
                    </td>
                    <td
                      style={{
                        padding: "0.4rem",
                        color: trade.pnl == null ? "#666" : trade.pnl >= 0 ? "#1e7e34" : "#c0392b",
                        fontWeight: "bold",
                      }}
                    >
                      {trade.pnl != null ? `$${trade.pnl.toFixed(2)}` : "N/A"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default ResultsDashboard;
