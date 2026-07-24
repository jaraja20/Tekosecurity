/**
 * Real-time metrics streaming via Server-Sent Events (SSE)
 * Connects to /api/mikrotiks/{name}/metrics-stream and updates in real-time (every 3 seconds)
 */

export class MetricsStream {
  constructor(deviceName, apiBase, token, onData, onError) {
    this.deviceName = deviceName;
    this.apiBase = apiBase;
    this.token = token;
    this.onData = onData;
    this.onError = onError;
    this.eventSource = null;
  }

  connect() {
    const url = `${this.apiBase}/api/mikrotiks/${this.deviceName}/metrics-stream`;

    console.log(`[MetricsStream] Connecting to ${url}`);

    this.eventSource = new EventSource(url, {
      headers: {
        Authorization: `Bearer ${this.token}`,
        "bypass-tunnel-reminder": "true",
      },
    });

    // Handle incoming metrics
    this.eventSource.addEventListener("message", (event) => {
      try {
        const metrics = JSON.parse(event.data);
        if (this.onData) {
          this.onData(metrics);
        }
      } catch (error) {
        console.error("[MetricsStream] Parse error:", error);
        if (this.onError) {
          this.onError(error);
        }
      }
    });

    // Handle errors
    this.eventSource.addEventListener("error", (error) => {
      console.error("[MetricsStream] Connection error:", error);
      if (this.onError) {
        this.onError(error);
      }
      this.disconnect();
    });

    // Initial connection log
    this.eventSource.addEventListener("open", () => {
      console.log("[MetricsStream] Connected");
    });
  }

  disconnect() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
      console.log("[MetricsStream] Disconnected");
    }
  }

  isConnected() {
    return this.eventSource !== null;
  }
}
