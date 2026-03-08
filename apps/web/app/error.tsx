"use client"; // Error boundaries must be Client Components

import { useEffect } from "react";
import { AlertOctagon, RotateCcw, Home } from "lucide-react";
import Link from "next/link";

export default function GlobalError({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        // Log the error to an error reporting service
        console.error("Critical React Boundary Error:", error);
    }, [error]);

    return (
        <div className="min-h-screen bg-[#050505] flex items-center justify-center p-4">
            <div className="max-w-md w-full bg-zinc-900 border border-zinc-800 rounded-3xl p-8 shadow-2xl space-y-8 relative overflow-hidden text-center">
                {/* Background glow */}
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-1/2 bg-red-500/10 blur-[100px] pointer-events-none" />

                <div className="flex justify-center relative z-10">
                    <div className="w-20 h-20 bg-red-500/10 rounded-full flex items-center justify-center border border-red-500/20 shadow-[0_0_30px_rgba(239,68,68,0.2)]">
                        <AlertOctagon className="w-10 h-10 text-red-500" />
                    </div>
                </div>

                <div className="space-y-3 relative z-10">
                    <h2 className="text-3xl font-black text-white tracking-tight">Something Went Wrong</h2>
                    <p className="text-zinc-400 text-sm">
                        An unexpected system error occurred. Our engineers have been notified.
                    </p>
                    <div className="bg-black/50 p-4 rounded-xl border border-zinc-800 mt-4 overflow-auto max-h-32">
                        <p className="text-red-400 font-mono text-xs text-left">
                            {error.message || "Unknown Runtime Error"}
                        </p>
                    </div>
                </div>

                <div className="flex flex-col gap-3 relative z-10 pt-4">
                    <button
                        onClick={() => reset()}
                        className="w-full flex items-center justify-center gap-2 py-3.5 bg-red-600 hover:bg-red-700 text-white font-bold rounded-xl transition-all shadow-[0_0_20px_rgba(239,68,68,0.2)] hover:shadow-[0_0_30px_rgba(239,68,68,0.4)]"
                    >
                        <RotateCcw className="w-5 h-5" />
                        Try Again
                    </button>
                    <Link
                        href="/"
                        className="w-full flex items-center justify-center gap-2 py-3.5 bg-zinc-800 hover:bg-zinc-700 text-white font-bold rounded-xl transition-all border border-zinc-700"
                    >
                        <Home className="w-5 h-5" />
                        Return Home
                    </Link>
                </div>
            </div>
        </div>
    );
}
