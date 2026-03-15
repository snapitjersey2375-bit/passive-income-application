"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { getApiUrl } from "@/lib/api-url";
import { Mail, ArrowRight, Users, Trophy, Copy, Check, Sparkles } from "lucide-react";
import Link from "next/link";

interface SignupResult {
    status: string;
    position: number;
    referral_code: string;
    message?: string;
}

interface LeaderboardEntry {
    email: string;
    priority_score: number;
    effective_position: number;
}

export default function WaitlistPage() {
    const [email, setEmail] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState<SignupResult | null>(null);
    const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
    const [copied, setCopied] = useState(false);
    const [refCode, setRefCode] = useState<string | null>(null);

    const API_URL = getApiUrl();

    useEffect(() => {
        // Check URL for referral code
        const params = new URLSearchParams(window.location.search);
        const ref = params.get("ref");
        if (ref) setRefCode(ref);

        // Fetch leaderboard
        fetch(`${API_URL}/waitlist/leaderboard`)
            .then(res => res.json())
            .then(data => setLeaderboard(data.leaderboard || []))
            .catch(console.error);
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!email || isLoading) return;

        setIsLoading(true);
        try {
            const res = await fetch(`${API_URL}/waitlist/signup`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, referral_code: refCode })
            });
            const data = await res.json();
            setResult(data);
        } catch (err) {
            console.error("Signup failed", err);
        } finally {
            setIsLoading(false);
        }
    };

    const copyReferralLink = () => {
        if (result?.referral_code) {
            navigator.clipboard.writeText(`${window.location.origin}/waitlist?ref=${result.referral_code}`);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    return (
        <div className="min-h-screen bg-[#050505] text-white font-sans relative overflow-hidden">
            {/* Background */}
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-transparent to-transparent pointer-events-none" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-purple-500/10 rounded-full blur-[150px] pointer-events-none" />

            <div className="relative z-10 container mx-auto px-4 py-20 max-w-4xl">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-16"
                >
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-white/10 text-sm mb-6">
                        <Sparkles className="w-4 h-4 text-yellow-400" />
                        <span className="font-mono">EXCLUSIVE EARLY ACCESS</span>
                    </div>

                    <h1 className="text-5xl md:text-7xl font-black tracking-tighter mb-6 bg-clip-text text-transparent bg-gradient-to-r from-white via-blue-100 to-purple-200">
                        Join the Swarm
                    </h1>
                    <p className="text-xl text-zinc-400 max-w-xl mx-auto leading-relaxed">
                        Be among the first to access AI-powered content curation that turns your ideas into revenue.
                    </p>
                </motion.div>

                {/* Signup Form / Result */}
                <AnimatePresence mode="wait">
                    {!result ? (
                        <motion.form
                            key="form"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            onSubmit={handleSubmit}
                            className="max-w-md mx-auto mb-20"
                        >
                            <div className="relative group">
                                <div className="absolute -inset-1 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition-opacity" />
                                <div className="relative flex bg-white/5 border border-white/10 rounded-2xl p-2">
                                    <div className="flex items-center pl-4 text-zinc-500">
                                        <Mail className="w-5 h-5" />
                                    </div>
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        placeholder="Enter your email"
                                        className="flex-1 bg-transparent px-4 py-4 outline-none text-white placeholder-zinc-500"
                                        required
                                    />
                                    <button
                                        type="submit"
                                        disabled={isLoading}
                                        className="bg-white text-black px-6 py-4 rounded-xl font-bold hover:scale-105 transition-transform disabled:opacity-50 flex items-center gap-2"
                                    >
                                        {isLoading ? "..." : "Join"} <ArrowRight size={18} />
                                    </button>
                                </div>
                            </div>

                            {refCode && (
                                <p className="text-center text-sm text-green-400 mt-4">
                                    ✨ Referred by code: <span className="font-mono font-bold">{refCode}</span>
                                </p>
                            )}
                        </motion.form>
                    ) : (
                        <motion.div
                            key="result"
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="max-w-md mx-auto mb-20 text-center"
                        >
                            <div className="bg-gradient-to-br from-green-500/20 to-blue-500/20 border border-green-500/30 rounded-3xl p-8">
                                <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-6">
                                    <Check className="w-8 h-8 text-black" />
                                </div>
                                <h2 className="text-2xl font-black mb-2">You&apos;re In!</h2>
                                <p className="text-zinc-400 mb-6">
                                    You&apos;re <span className="text-white font-bold">#{result.position}</span> in line.
                                    {result.message}
                                </p>

                                <div className="bg-black/30 rounded-2xl p-4 mb-4">
                                    <p className="text-xs text-zinc-500 uppercase tracking-widest mb-2">Your Referral Code</p>
                                    <div className="flex items-center justify-center gap-3">
                                        <span className="text-2xl font-mono font-black text-blue-400">{result.referral_code}</span>
                                        <button
                                            onClick={copyReferralLink}
                                            className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
                                        >
                                            {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                                        </button>
                                    </div>
                                </div>

                                <p className="text-sm text-zinc-500">
                                    Each referral moves you up <span className="text-white">10 spots</span>!
                                </p>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Leaderboard */}
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                >
                    <div className="flex items-center justify-center gap-2 mb-6">
                        <Trophy className="w-5 h-5 text-yellow-400" />
                        <h3 className="text-lg font-bold">Top Referrers</h3>
                    </div>

                    <div className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden">
                        {leaderboard.length > 0 ? (
                            leaderboard.slice(0, 5).map((entry, i) => (
                                <div
                                    key={i}
                                    className="flex items-center justify-between p-4 border-b border-white/5 last:border-0"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs ${i === 0 ? 'bg-yellow-500 text-black' : i === 1 ? 'bg-gray-400 text-black' : i === 2 ? 'bg-amber-700 text-white' : 'bg-zinc-800'}`}>
                                            {i + 1}
                                        </div>
                                        <span className="font-mono text-zinc-300">{entry.email}</span>
                                    </div>
                                    <div className="text-right">
                                        <div className="font-bold text-green-400">+{entry.priority_score} pts</div>
                                        <div className="text-xs text-zinc-500">#{entry.effective_position}</div>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="p-8 text-center text-zinc-500">
                                <Users className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                <p>Be the first on the leaderboard!</p>
                            </div>
                        )}
                    </div>
                </motion.div>

                {/* Footer Link */}
                <div className="text-center mt-12">
                    <Link href="/stats" className="text-sm text-zinc-500 hover:text-white transition-colors">
                        View Live Network Stats →
                    </Link>
                </div>
            </div>
        </div>
    );
}
