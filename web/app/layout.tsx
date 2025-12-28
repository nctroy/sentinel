import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Sentinel Command Center",
  description: "Multi-Agent Orchestration Dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-slate-50 min-h-screen`}>
        <Sidebar />
        <main className="pl-64 min-h-screen">
          <div className="container mx-auto p-8 max-w-7xl">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}
