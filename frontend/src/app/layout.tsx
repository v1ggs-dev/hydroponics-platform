import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Hydroponics Monitoring & Control Platform",
  description: "Minimalist Real-Time Hydroponics IoT Dashboard with Supabase Persistence & Automated Safety Controls",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#f8fafc] text-[#0f172a] min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
