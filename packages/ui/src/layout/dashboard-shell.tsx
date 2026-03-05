"use client";

import React from "react";
import { cn } from "../utils/cn";

interface DashboardShellProps {
    children: React.ReactNode;
    headerContent?: React.ReactNode;
    className?: string;
}

export function DashboardShell({ children, headerContent, className }: DashboardShellProps) {
    return (
        <div className="min-h-screen font-sans text-slate-800">
            {/* Glass Header */}
            <header className="fixed top-0 w-full z-50 glass border-b-0">
                <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold shadow-lg shadow-blue-500/30">
                            N
                        </div>
                        <span className="font-bold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-700 to-indigo-700">
                            NexusFlow
                        </span>
                    </div>
                    <div>{headerContent}</div>
                </div>
            </header>

            <main className="pt-24 pb-12 max-w-7xl mx-auto px-4">
                {children}
            </main>
        </div>
    );
}
