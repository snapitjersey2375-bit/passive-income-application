"use client";

import React, { useState, useEffect } from "react";
import { Activity, Zap, DollarSign } from "lucide-react";
import { cn } from "./utils/cn";

interface ActivityItem {
    user: string;
    action: string;
    time: string;
    value?: number;
}

export function ActivityTicker() {
    const [activities, setActivities] = useState<ActivityItem[]>([]);
    const [currentIndex, setCurrentIndex] = useState(0);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    useEffect(() => {
        const fetchActivity = async () => {
            try {
                const res = await fetch(`${API_URL}/stats/activity`);
                if (res.ok) {
                    const data = await res.json();
                    setActivities(data.activities || []);
                }
            } catch (error) {
                console.error("Activity fetch failed", error);
            }
        };

        fetchActivity();
        const interval = setInterval(fetchActivity, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, []);

    // Rotate through activities every 4 seconds
    useEffect(() => {
        if (activities.length === 0) return;
        const rotateInterval = setInterval(() => {
            setCurrentIndex((prev) => (prev + 1) % activities.length);
        }, 4000);
        return () => clearInterval(rotateInterval);
    }, [activities.length]);

    if (activities.length === 0) {
        return null; // Don't show if no activity
    }

    const current = activities[currentIndex];

    return (
        <div className="fixed bottom-4 left-4 z-50 animate-in slide-in-from-bottom-4 duration-500">
            <div className="bg-black/80 backdrop-blur-lg border border-white/10 rounded-2xl px-4 py-3 shadow-2xl flex items-center gap-3 max-w-xs">
                <div className="relative">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center">
                        <Zap className="w-4 h-4 text-white" />
                    </div>
                    <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-green-400 rounded-full animate-ping" />
                    <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-green-400 rounded-full" />
                </div>

                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5">
                        <span className="text-white font-bold text-xs truncate">{current.user}</span>
                        <span className="text-zinc-500 text-[10px]">• {current.time}</span>
                    </div>
                    <p className="text-zinc-400 text-[10px] truncate leading-tight">
                        {current.action}
                    </p>
                </div>

                {current.value && (
                    <div className="flex items-center gap-0.5 text-green-400 text-xs font-bold shrink-0">
                        <DollarSign className="w-3 h-3" />
                        {current.value.toFixed(0)}
                    </div>
                )}
            </div>
        </div>
    );
}
