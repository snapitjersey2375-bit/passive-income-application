"use client";

import { useEffect, useState } from "react";
import { motion, useSpring, useTransform } from "framer-motion";

interface Stats {
    total_payouts: number;
    total_content: number;
    active_curators: number;
}

export function StatsTicker() {
    const [stats, setStats] = useState<Stats>({
        total_payouts: 0,
        total_content: 0,
        active_curators: 0,
    });

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const API_URL = typeof window !== 'undefined'
                    ? (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
                        ? 'http://localhost:8000'
                        : 'https://passive-income-application.onrender.com')
                    : 'https://passive-income-application.onrender.com';
                const res = await fetch(`${API_URL}/stats/global`);
                const data = await res.json();
                setStats(data);
            } catch (error) {
                console.error("Failed to fetch stats", error);
            }
        };

        fetchStats();
        const interval = setInterval(fetchStats, 5000); // Poll every 5s for live effect
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-5xl mx-auto py-12 px-4">
            <StatCard
                label="Total Payouts"
                value={stats.total_payouts}
                prefix="$"
                decimals={2}
            />
            <StatCard
                label="Content Generated"
                value={stats.total_content}
                suffix="+"
            />
            <StatCard
                label="Active Curators"
                value={stats.active_curators}
            />
        </div>
    );
}

function StatCard({
    label,
    value,
    prefix = "",
    suffix = "",
    decimals = 0
}: {
    label: string;
    value: number;
    prefix?: string;
    suffix?: string;
    decimals?: number;
}) {
    const spring = useSpring(value, { mass: 0.8, stiffness: 75, damping: 15 });
    const display = useTransform(spring, (current) =>
        `${prefix}${current.toLocaleString("en-US", {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        })}${suffix}`
    );

    useEffect(() => {
        spring.set(value);
    }, [value, spring]);

    return (
        <div className="flex flex-col items-center justify-center p-6 bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl hover:bg-white/10 transition-colors">
            <motion.span className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
                {display}
            </motion.span>
            <span className="text-sm md:text-base text-zinc-400 mt-2 font-medium tracking-wide uppercase">
                {label}
            </span>
        </div>
    );
}
