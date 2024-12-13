import { usePathname, useRouter, useSearchParams } from "next/navigation";
import React from "react";

export function useUpdateSearchParams() {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();

  const update = React.useCallback(
    (queries: Record<string, string>) => {
      const currentSearchparams = new URLSearchParams(
        Array.from(searchParams.entries())
      );

      Object.entries(queries).forEach(([key, value]) => {
        if (value === "") {
          currentSearchparams.delete(key);
        } else {
          currentSearchparams.set(key, value);
        }
      });

      router.push(`${pathname}?${currentSearchparams.toString()}`);
    },
    [pathname, searchParams, router]
  );

  return {
    update,
  };
}
