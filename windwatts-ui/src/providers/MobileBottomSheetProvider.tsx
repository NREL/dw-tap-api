import React, { createContext, useContext, useRef, useCallback } from "react";
import { MobileBottomSheetRef } from "../components/mobile-view";

interface MobileBottomSheetContextType {
  clearSearchInput: () => void;
  expandDrawer: () => void;
  setBottomSheetRef: (ref: MobileBottomSheetRef | null) => void;
}

const MobileBottomSheetContext =
  createContext<MobileBottomSheetContextType | null>(null);

// eslint-disable-next-line react-refresh/only-export-components
export const useMobileBottomSheet = () => {
  const context = useContext(MobileBottomSheetContext);
  if (!context) {
    throw new Error(
      "useMobileBottomSheet must be used within a MobileBottomSheetProvider"
    );
  }
  return context;
};

interface MobileBottomSheetProviderProps {
  children: React.ReactNode;
}

export const MobileBottomSheetProvider: React.FC<
  MobileBottomSheetProviderProps
> = ({ children }) => {
  const bottomSheetRef = useRef<MobileBottomSheetRef>(null);

  const setBottomSheetRef = useCallback((ref: MobileBottomSheetRef | null) => {
    bottomSheetRef.current = ref;
  }, []);

  const clearSearchInput = () => {
    bottomSheetRef.current?.clearSearchInput();
  };

  const expandDrawer = () => {
    bottomSheetRef.current?.expandDrawer();
  };

  return (
    <MobileBottomSheetContext.Provider
      value={{ clearSearchInput, expandDrawer, setBottomSheetRef }}
    >
      {children}
    </MobileBottomSheetContext.Provider>
  );
};
