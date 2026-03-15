"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Loader2, Sparkles, ArrowRight, Copy, Check } from "lucide-react";
import { cn } from "@repo/ui";

export function WaitlistForm() {
    const [email, setEmail] = useState("");
    const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
    const [result, setResult] = useState<{ position?: number; referral_code?: string } | null>(null);
    const [copied, setCopied] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!email) return;

        setStatus("loading");
        try {
            // Check for referral code in URL (simple implementation)
            const urlParams = new URLSearchParams(window.location.search);
            const referralCode = urlParams.get("ref");

            const API_URL = typeof window !== 'undefined'
                ? (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
                    ? 'http://localhost:8000'
                    : 'https://passive-income-application.onrender.com')
                : 'https://passive-income-application.onrender.com';

            const res = await fetch(`${API_URL}/waitlist/signup`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, referral_code: referralCode }),
            });

            const data = await res.json();
            if (res.ok) {
                setResult(data);
                setStatus("success");
            } else {
                setStatus("error");
            }
        } catch {
            setStatus("error");
        }
    };

    const copyToClipboard = () => {
        if (!result?.referral_code) return;
        const link = `${window.location.origin}?ref=${result.referral_code}`;
        navigator.clipboard.writeText(link);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (status === "success") {
        return (
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-md mx-auto bg-green-500/10 border border-green-500/20 rounded-2xl p-6 text-center"
            >
                <div className="flex justify-center mb-4">
                    <div className="p-3 bg-green-500/20 rounded-full">
                        <Sparkles className="w-8 h-8 text-green-400" />
                    </div>
                </div>
                <h3 className="text-2xl font-bold text-white mb-2">You&apos;re on the list!</h3>
                <p className="text-zinc-300 mb-6">
                    You are <span className="text-green-400 font-bold">#{result?.position}</span> in line.
                </p>

                <div className="bg-black/30 rounded-xl p-4 mb-4">
                    <p className="text-sm text-zinc-400 mb-2">Share to move up the queue:</p>
                    <div className="flex items-center gap-2 bg-black/50 rounded-lg p-2 border border-white/5">
                        <code className="flex-1 text-sm text-zinc-300 truncate">
                            {typeof window !== 'undefined' ? window.location.origin : ''}?ref={result?.referral_code}
                        </code>
                        <button
                            onClick={copyToClipboard}
                            className="p-2 hover:bg-white/10 rounded-md transition-colors"
                        >
                            {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4 text-white" />}
                        </button>
                    </div>
                </div>
            </motion.div>
        );
    }

    return (
        <div className="w-full max-w-md mx-auto">
            <form onSubmit={handleSubmit} className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
                <div className="relative flex items-center bg-zinc-900 rounded-xl p-2 border border-white/10">
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Enter your email..."
                        className="flex-1 bg-transparent px-4 py-3 text-white placeholder-zinc-500 focus:outline-none"
                        required
                        disabled={status === "loading"}
                    />
                    <button
                        type="submit"
                        disabled={status === "loading"}
                        className={cn(
                            "px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2",
                            status === "loading"
                                ? "bg-zinc-800 text-zinc-400 cursor-not-allowed"
                                : "bg-white text-black hover:bg-zinc-200"
                        )}
                    >
                        {status === "loading" ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                            <>
                                Join Waitlist <ArrowRight className="w-4 h-4" />
                            </>
                        )}
                    </button>
                </div>
            </form>
            {status === "error" && (
                <p className="text-red-400 text-sm mt-3 text-center">
                    Something went wrong. Please try again.
                </p>
            )}
            <p className="text-zinc-500 text-xs mt-4 text-center">
                Limited spots available for the beta.
            </p>
        </div>
    );
}
