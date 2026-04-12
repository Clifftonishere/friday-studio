import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Friday Studio",
  description: "AI-powered animated video production",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[#FAF6F1] text-[#1a1a1a]">
        <header className="border-b border-[#E8E0D6] bg-white px-6 py-4">
          <a href="/" className="text-xl font-bold tracking-tight text-[#6B5B4E]">
            Friday Studio
          </a>
        </header>
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
