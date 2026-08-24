import { WebSocketServer, WebSocket } from "ws";
import { Server } from "http";

export class WebSocketService {
  private static instance: WebSocketService;
  private wss: WebSocketServer | null = null;
  private clients: Set<WebSocket> = new Set();

  private constructor() {}

  public static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService();
    }
    return WebSocketService.instance;
  }

  public init(server: Server) {
    this.wss = new WebSocketServer({ server, path: "/ws" });

    this.wss.on("connection", (ws: WebSocket) => {
      this.clients.add(ws);
      console.log(`🔌 [WebSocket] Client connected. Total active clients: ${this.clients.size}`);

      // Send initial welcome/ready handshake
      ws.send(JSON.stringify({ type: "connection", status: "CONNECTED", timestamp: new Date().toISOString() }));

      ws.on("close", () => {
        this.clients.delete(ws);
        console.log(`🔌 [WebSocket] Client disconnected. Active clients: ${this.clients.size}`);
      });

      ws.on("error", (error) => {
        console.error("🔌 [WebSocket] Client error:", error);
        this.clients.delete(ws);
      });
    });

    console.log("🚀 [WebSocket] Realtime WebSocket server initialized on path /ws");
  }

  public broadcast(event: string, data: any) {
    if (!this.wss || this.clients.size === 0) return;

    const payload = JSON.stringify({
      event,
      data,
      timestamp: new Date().toISOString(),
    });

    for (const client of this.clients) {
      if (client.readyState === WebSocket.OPEN) {
        client.send(payload);
      }
    }
  }
}

export const wsService = WebSocketService.getInstance();
