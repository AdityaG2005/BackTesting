import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

function ResultsDashboard({ results }) {
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

  return (
    <div style={{ border: "1px solid #ccc", padding: "1rem", borderRadius: "8px", marginTop: "1rem" }}>
      <h2>3. Results</h2>

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
        <div>
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
    </div>
  );
}

export default ResultsDashboard;

