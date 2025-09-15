import type { Metadata } from "next";
import "./globals.css";
import Providers from "@/app/providers";
import Link from "next/link";

export const metadata: Metadata = {
  title: "AI Digital Dietician",
  description: "What should I cook?",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-neutral-950 text-neutral-100 antialiased">
        <Providers>
          <header className="border-b border-neutral-800">
            <nav className="max-w-5xl mx-auto p-4 flex items-center gap-6">
              <Link href="/" className="font-semibold">Home</Link>
              <Link href="/pantry" className="opacity-80 hover:opacity-100">Pantry</Link>
              <Link href="/plan" className="opacity-80 hover:opacity-100">Plan</Link>
            </nav>
          </header>
          {children}
        </Providers>
      </body>
    </html>
  );
}
