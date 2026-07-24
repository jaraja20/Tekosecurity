/**
 * Real-time metrics streaming via fetch + ReadableStream
 * Connects to /api/mikrotiks/{name}/metrics-stream and updates in real-time (every 1 second)
 * Uses fetch instead of EventSource because EventSource doesn't support custom headers (needed for localtunnel)
 */

export class MetricsStream {
  constructor(deviceName, apiBase, token, onData, onError) {
    this.deviceName = deviceName;
    this.apiBase = apiBase;
    this.token = token;
    this.onData = onData;
    this.onError = onError;
    this.abortController = null;
  }

  async connect() {
    const url = `${this.apiBase}/api/mikrotiks/${this.deviceName}/metrics-stream`;

    console.log(`[MetricsStream] Connecting to ${url}`);

    this.abortController = new AbortController();

    try {
      const response = await fetch(url, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${this.token}`,
          "bypass-tunnel-reminder": "true",
          Accept: "text/event-stream",
        },
        signal: this.abortController.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      console.log("[MetricsStream] Connected");

      // Read the stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");

        // Keep the last incomplete line in the buffer
        buffer = lines[lines.length - 1];

        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i].trim();

          if (line.startsWith("data: ")) {
            const jsonStr = line.slice(6);
            try {
              const metrics = JSON.parse(jsonStr);
              if (this.onData) {
                this.onData(metrics);
              }
            } catch (error) {
              console.error("[MetricsStream] Parse error:", error);
              if (this.onError) {
                this.onError(error);
              }
            }
          }
        }
      }
    } catch (error) {
      if (error.name !== "AbortError") {
        console.error("[MetricsStream] Connection error:", error);
        if (this.onError) {
          this.onError(error);
        }
      }
    } finally {
      this.disconnect();
    }
  }

  disconnect() {
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
      console.log("[MetricsStream] Disconnected");
    }
  }

  isConnected() {
    return this.abortController !== null;
  }
}
