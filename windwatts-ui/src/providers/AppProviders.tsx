import React from "react";
import { SettingsProvider } from "./SettingsProvider";
import { UnitsProvider } from "./UnitsProvider";

interface AppProvidersProps {
  children: React.ReactNode;
}

export const AppProviders: React.FC<AppProvidersProps> = ({ children }) => {
  return (
    <SettingsProvider>
      <UnitsProvider>{children}</UnitsProvider>
    </SettingsProvider>
  );
};
