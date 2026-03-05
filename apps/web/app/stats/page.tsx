"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { TrendingUp, Users, DollarSign, Activity, Zap, ArrowRight } from "lucide-react";
import Link from "next/link";


interface GlobalStats {
    total_payouts: number;
    total_content: number;
    active_curators: number;
}

interface ActivityItem {
    user: string;
    action: string;
    time: string;
    value?: number;
}

export default function PublicStatsPage() {
    const [stats, setStats] = useState<GlobalStats | null>(null);
    const [activity, setActivity] = useState<ActivityItem[]>([]);
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    useEffect(() => {
        const fetchData = async () => {
            try {
                const statsRes = await fetch(`${API_URL}/stats/global`);
                const statsData = await statsRes.json();
                setStats(statsData);

                const activityRes = await fetch(`${API_URL}/stats/activity`);
                const activityData = await activityRes.json();
                setActivity(activityData.activities);
            } catch (err) {
                console.error("Failed to load stats", err);
            }
        };

        fetchData();
        // Poll every 5 seconds for live feel
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="min-h-screen bg-[#050505] text-white selection:bg-blue-500/30 font-sans overflow-hidden relative">
            {/* Background Gradients */}
            <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-blue-500/20 rounded-full blur-[120px] -translate-x-1/2 -translate-y-1/2 pointer-events-none" />
            <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-purple-500/20 rounded-full blur-[120px] translate-x-1/2 translate-y-1/2 pointer-events-none" />

            <div className="relative z-10 container mx-auto px-4 py-20">
                {/* Header */}
                <div className="text-center mb-20 space-y-4">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-mono text-blue-400 mb-4"
                    >
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                        </span>
                        CORE SYSTEM LIVE
                    </motion.div>

                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="text-5xl md:text-7xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-gray-500"
                    >
                        NexusFlow Network
                    </motion.h1>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="text-xl text-zinc-400 max-w-2xl mx-auto"
                    >
                        Real-time visualization of the world's first AI-powered content curation economy.
                    </motion.p>
                </div>

                {/* Main Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-24 cursor-default">
                    <StatCard
                        label="Total Payouts Distributed"
                        value={stats ? `$${stats.total_payouts.toLocaleString(undefined, { maximumFractionDigits: 0 })}` : "..."}
                        icon={<DollarSign className="text-green-400" />}
                        delay={0.3}
                    />
                    <StatCard
                        label="Content Assets Optimized"
                        value={stats ? stats.total_content.toLocaleString() : "..."}
                        icon={<Zap className="text-yellow-400" />}
                        delay={0.4}
                    />
                    <StatCard
                        label="Active Curators"
                        value={stats ? stats.active_curators.toLocaleString() : "..."}
                        icon={<Users className="text-blue-400" />}
                        delay={0.5}
                    />
                </div>

                {/* Live Activity Feed */}
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                    className="max-w-3xl mx-auto"
                >
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-xl font-bold flex items-center gap-2">
                            <Activity className="w-5 h-5 text-blue-500" />
                            Live Network Activity
                        </h2>
                        <div className="text-xs font-mono text-zinc-500">REAL-TIME FEED</div>
                    </div>

                    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-6 relative overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-[#050505]/10 pointer-events-none" />

                        <div className="space-y-4">
                            {activity.map((item, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: i * 0.1 }}
                                    className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-500 to-purple-600 flex items-center justify-center font-bold text-xs">
                                            {item.user.charAt(0)}
                                        </div>
                                        <div>
                                            <div className="font-bold text-sm text-zinc-200">
                                                {item.user} <span className="text-zinc-500 font-normal">analysis complete</span>
                                            </div>
                                            <div className="text-xs text-blue-400 flex items-center gap-1">
                                                {item.action}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        {item.value && (
                                            <div className="font-mono font-bold text-green-400 text-sm">
                                                +${item.value.toFixed(2)}
                                            </div>
                                        )}
                                        <div className="text-[10px] text-zinc-600 uppercase font-bold tracking-wider">
                                            {item.time}
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                            {activity.length === 0 && (
                                <div className="text-center text-zinc-500 py-10">Connecting to Neural Net...</div>
                            )}
                        </div>
                    </div>
                </motion.div>

                {/* Call to Action */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.8 }}
                    className="text-center mt-24"
                >
                    <Link
                        href="/login"
                        className="inline-flex items-center gap-3 px-8 py-4 bg-white text-black rounded-full font-bold text-lg hover:scale-105 transition-transform shadow-[0_0_40px_-5px_rgba(255,255,255,0.3)]"
                    >
                        Join the Network <ArrowRight size={20} />
                    </Link>
                    <p className="mt-4 text-zinc-500 text-sm">Limited spots available for Phase 1 beta.</p>
                </motion.div>
            </div>
        </div>
    );
}

function StatCard({ label, value, icon, delay }: { label: string, value: string, icon: React.ReactNode, delay: number }) {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay, type: "spring" }}
            className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-sm relative group overflow-hidden"
        >
            <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="mb-4 p-3 bg-white/5 rounded-2xl w-fit">{icon}</div>
            <div className="text-4xl md:text-5xl font-black mb-2 tracking-tight group-hover:scale-105 transition-transform origin-left">
                {value}
            </div>
            <div className="text-sm font-bold text-zinc-500 uppercase tracking-widest">
                {label}
            </div>
        </motion.div>
    );
}
