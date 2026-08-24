import { PrismaClient } from "@prisma/client";

// Ensure BigInt values can be serialized to JSON safely
(BigInt.prototype as any).toJSON = function () {
  const int = Number.parseInt(this.toString());
  return int ?? this.toString();
};

export let isDatabaseConnected = false;

export const prisma = new PrismaClient({
  log: ["error"],
});

export async function connectDatabase() {
  try {
    // Attempt with a fast 3-second timeout
    await Promise.race([
      prisma.$connect(),
      new Promise((_, reject) => setTimeout(() => reject(new Error("Connection timeout")), 3000))
    ]);
    isDatabaseConnected = true;
    console.log("✅ [Database] Connected successfully to Supabase PostgreSQL!");
  } catch (error: any) {
    isDatabaseConnected = false;
    console.warn("⚠️ [Database] Remote Supabase connection unreachable. Running in high-speed In-Memory Mode.");
  }
}
