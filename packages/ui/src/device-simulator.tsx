"use client";

import React from "react";
import { motion } from "framer-motion";
import { cn } from "./utils/cn";

interface DeviceSimulatorProps {
    children: React.ReactNode;
    orientation?: "portrait" | "landscape";
    className?: string;
}

export function DeviceSimulator({
    children,
    orientation = "portrait",
    className,
}: DeviceSimulatorProps) {
    const isLandscape = orientation === "landscape";

    return (
        <div className={cn("relative flex items-center justify-center transition-all duration-700", className)}>
            <motion.div
                animate={{
                    rotate: isLandscape ? 90 : 0,
                    width: isLandscape ? 600 : 320,
                    height: isLandscape ? 320 : 600,
                }}
                transition={{ type: "spring", stiffness: 200, damping: 25 }}
                className={cn(
                    "relative border-[8px] border-slate-900 rounded-[3rem] shadow-[0_50px_100px_-20px_rgba(0,0,0,0.5)] overflow-hidden bg-black",
                    "before:absolute before:top-0 before:left-1/2 before:-translate-x-1/2 before:w-32 before:h-6 before:bg-slate-900 before:rounded-b-2xl before:z-50"
                )}
            >
                {/* Inner Screen */}
                <div className="absolute inset-0 w-full h-full overflow-hidden bg-slate-950">
                    {/* Glass Overlay for depth */}
                    <div className="absolute inset-0 bg-gradient-to-tr from-white/5 to-transparent pointer-events-none z-10" />

                    <div className="w-full h-full flex items-center justify-center p-0">
                        {children}
                    </div>
                </div>

                {/* Home Bar */}
                <div className="absolute bottom-1.5 left-1/2 -translate-x-1/2 w-24 h-1 bg-white/20 rounded-full z-20" />
            </motion.div>
        </div>
    );
}
