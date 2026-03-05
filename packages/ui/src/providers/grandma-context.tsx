"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

interface GrandmaContextType {
    isGrandmaMode: boolean;
    toggleGrandmaMode: () => void;
}

const GrandmaContext = createContext<GrandmaContextType | undefined>(undefined);

export function GrandmaProvider({ children }: { children: React.ReactNode }) {
    const [isGrandmaMode, setIsGrandmaMode] = useState(false);

    // Persist preference
    useEffect(() => {
        const saved = localStorage.getItem("grandma-mode");
        if (saved === "true") setIsGrandmaMode(true);
    }, []);

    const toggleGrandmaMode = () => {
        setIsGrandmaMode((prev) => {
            const newValue = !prev;
            localStorage.setItem("grandma-mode", String(newValue));
            return newValue;
        });
    };

    // Apply class to body for global styling
    useEffect(() => {
        if (isGrandmaMode) {
            document.documentElement.classList.add("grandma-mode");
            document.body.style.fontSize = "150%";
        } else {
            document.documentElement.classList.remove("grandma-mode");
            document.body.style.fontSize = "100%";
        }
    }, [isGrandmaMode]);

    return (
        <GrandmaContext.Provider value={{ isGrandmaMode, toggleGrandmaMode }}>
            {children}
        </GrandmaContext.Provider>
    );
}

export function useGrandma() {
    const context = useContext(GrandmaContext);
    if (context === undefined) {
        throw new Error("useGrandma must be used within a GrandmaProvider");
    }
    return context;
}
