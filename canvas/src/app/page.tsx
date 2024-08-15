"use client";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

export default function Home() {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (pathname === "/") {
      router.push("/search");
    }
  }, [pathname, router]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24"></main>
  );
}
