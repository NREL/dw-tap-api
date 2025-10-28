"use client";

import ThemeRegistry from "../src/ThemeRegistry";
import { UnitsProvider } from "../src/providers/UnitsProvider";

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeRegistry>
      <UnitsProvider>{children}</UnitsProvider>
    </ThemeRegistry>
  );
}
