import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ErgoFlow AI — Autonomous Health Agent for Engineers",
  description:
    "AI-powered occupational health agent that monitors your physical well-being and autonomously schedules personalized recovery routines.",
  keywords: ["ergonomics", "health", "AI", "agent", "developer", "wellness"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
