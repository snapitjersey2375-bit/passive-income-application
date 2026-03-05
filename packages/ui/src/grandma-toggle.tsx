"use client";

import React from "react";
import { useGrandma } from "./providers/grandma-context";
import { Glasses } from "lucide-react";
import { cn } from "./utils/cn";

export function GrandmaToggle({ className }: { className?: string }) {
    const { isGrandmaMode, toggleGrandmaMode } = useGrandma();

    return (
        <button
            onClick={toggleGrandmaMode}
            className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-full transition-all duration-300 shadow-md border-2",
                isGrandmaMode
                    ? "bg-yellow-100 border-yellow-500 text-yellow-900 text-xl font-bold"
                    : "bg-white border-gray-200 text-gray-700 hover:bg-gray-50",
                className
            )}
            aria-label="Toggle Grandma Mode"
        >
            <Glasses className={cn("w-5 h-5", isGrandmaMode && "w-8 h-8")} />
            <span>{isGrandmaMode ? "GRANDMA SAYS: HI DEAR!" : "Grandma Mode"}</span>
        </button>
    );
}
