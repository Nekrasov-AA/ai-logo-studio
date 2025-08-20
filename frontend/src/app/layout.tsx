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
  title: "AI Logo Studio",
  description: "Generate logos with AI, SVG and palettes",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <header style={{padding:12, borderBottom:'1px solid #eee'}}>
          <a href="/" style={{marginRight:16}}>Home</a>
          <a href="/generate">Generate</a>
        </header>
        {children}
      </body>
    </html>
  );
}
