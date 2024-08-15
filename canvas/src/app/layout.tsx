"use client";
import Link from "next/link";
import { Inter as FontSans } from "next/font/google";
import "react-datasheet-grid/dist/style.css";
import "../styles/globals.css";
import { cn } from "@/src/lib/utils";
import { ThemeProvider } from "@/src/components/theme-provider";
import { Announcement } from "@/src/components/announcement";
import { WidgetsNav } from "@/src/components/widgets-nav";
import {
  PageActions,
  PageHeader,
  PageHeaderDescription,
  PageHeaderHeading,
} from "@/src/components/page-header";
import { buttonVariants } from "@/src/components/ui/button";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ModeToggle } from "@/src/components/theme-toggle";

const fontSans = FontSans({ subsets: ["latin"], variable: "--font-sans" });

interface HomeLayoutProps {
  children: React.ReactNode;
}

const queryClient = new QueryClient();

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={cn(
          "min-h-screen bg-background font-sans antialiased cpg",
          fontSans.variable
        )}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <QueryClientProvider client={queryClient}>
            <div className="bg-background container relative">
              <PageHeader>
                <Announcement />
                <PageHeaderHeading className="hidden md:block">
                  Cell Painting Gallery Tools
                </PageHeaderHeading>
                <PageHeaderHeading className="md:hidden">
                  Cell Painting Gallery Tools
                </PageHeaderHeading>
                <PageHeaderDescription>
                  This alpha release contains a metadata searching tool that will search across metadata
                  files in the Cell Painting Gallery. Stay tuned for more tools in future releases.
                </PageHeaderDescription>
                <PageActions>
                  <Link
                    href="https://broadinstitute.github.io/cellpainting-gallery/overview.html"
                    className={cn(buttonVariants(), "rounded-[6px]")}
                  >
                    Docs
                  </Link>
                  <ModeToggle />
                </PageActions>
              </PageHeader>
              <WidgetsNav className="[&>a:first-child]:text-primary" />
              <section>
                <div className="overflow-hidden rounded-[0.5rem] border bg-background">
                  {children}
                </div>
              </section>
            </div>
          </QueryClientProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
