import axios from "axios";

const API_URL = "http://localhost:8000";

export async function getStrategies() {
  const response = await axios.get(`${API_URL}/strategies`);
  return response.data.strategies;
}

export async function submitBacktest(config) {
  const response = await axios.post(`${API_URL}/backtest`, config);
  return response.data;
}

export async function getBacktest(id) {
  const response = await axios.get(`${API_URL}/backtest/${id}`);
  return response.data;
}

export async function generateStrategyFromDescription(description, validationTicker = "AAPL") {
  const response = await axios.post(`${API_URL}/strategies/from-description`, {
    description,
    validation_ticker: validationTicker,
  });
  return response.data;
}

export async function pollBacktest(id, onStatusUpdate, intervalMs = 1500, timeoutMs = 60000) {
  const startTime = Date.now();

  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const data = await getBacktest(id);

        if (onStatusUpdate) {
          onStatusUpdate(data.status);
        }

        if (data.status === "done" || data.status === "failed") {
          resolve(data);
          return;
        }

        if (Date.now() - startTime > timeoutMs) {
          reject(new Error("Backtest polling timed out"));
          return;
        }

        setTimeout(poll, intervalMs);
      } catch (error) {
        reject(error);
      }
    };

    poll();
  });
}

