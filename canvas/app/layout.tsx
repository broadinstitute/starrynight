import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { cn } from "@/shadcn/utils";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "Starrynight",
  description: "Starrynight",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <link rel="icon" href="/broad.svg" sizes="any" />
      <body
        className={cn("min-h-screen font-sans antialiased", inter.variable)}
      >
        {children}
      </body>
    </html>
  );
}
