"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Trophy, Crown, TrendingUp } from "lucide-react";

interface LeaderboardEntry {
    email: string;
    priority_score: number;
    effective_position: number;
}

export function ReferralLeaderboard() {
    const [entries, setEntries] = useState<LeaderboardEntry[]>([]);

    useEffect(() => {
        const fetchLeaderboard = async () => {
            try {
                const API_URL = typeof window !== 'undefined'
                    ? (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
                        ? 'http://localhost:8000'
                        : 'https://passive-income-application.onrender.com')
                    : 'https://passive-income-application.onrender.com';
                const res = await fetch(`${API_URL}/waitlist/leaderboard`);
                const data = await res.json();
                setEntries(data.leaderboard || []);
            } catch (error) {
                console.error("Failed to fetch leaderboard", error);
            }
        };

        fetchLeaderboard();
    }, []);

    if (entries.length === 0) return null;

    return (
        <div className="w-full max-w-sm mx-auto bg-black/20 backdrop-blur-md rounded-2xl border border-white/5 p-6">
            <div className="flex items-center gap-2 mb-6">
                <Trophy className="w-5 h-5 text-yellow-500" />
                <h3 className="text-lg font-semibold text-white">Top Referrers</h3>
            </div>

            <div className="space-y-4">
                {entries.slice(0, 5).map((entry, index) => (
                    <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="flex items-center gap-4 p-3 bg-white/5 rounded-xl border border-white/5"
                    >
                        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-white/10 text-sm font-bold text-white">
                            {index + 1}
                        </div>
                        <div className="flex-1">
                            <div className="text-sm font-medium text-zinc-200">{entry.email}</div>
                            <div className="text-xs text-zinc-500 flex items-center gap-1">
                                <TrendingUp className="w-3 h-3" />
                                Boosted {entry.priority_score} pts
                            </div>
                        </div>
                        {index === 0 && <Crown className="w-5 h-5 text-yellow-500" />}
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
