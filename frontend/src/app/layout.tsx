import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Scout — AI-Powered Candidate Ranking Engine",
  description:
    "Scout is a deterministic, evidence-based candidate ranking engine that distinguishes genuine AI/ML talent from keyword-stuffed resumes.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-zinc-950 text-zinc-50 antialiased`}>
        <Navbar />
        <main>{children}</main>
      </body>
    </html>
  );
}
