import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { cn } from "@/shadcn/utils";
import { Providers } from "./providers";
import { Toaster } from "@/components/ui/toaster";

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
    <html lang="en" className="bg-[#eee]">
      <link rel="icon" href="/broad.svg" sizes="any" />
      <body
        className={cn("min-h-screen font-sans antialiased", inter.variable)}
      >
        <Providers>{children}</Providers>
        <Toaster />
      </body>
    </html>
  );
}
