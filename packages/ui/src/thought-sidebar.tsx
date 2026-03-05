"use client";

import React, { useEffect, useState } from 'react';
import { X, Terminal, Cpu, Check } from 'lucide-react';
import { cn } from './utils/cn';
import { SocialConnections } from './social-connections';

interface LogEntry {
    timestamp: string;
    level: string;
    agent: string;
    message: string;
}

interface ThoughtSidebarProps {
    isOpen: boolean;
    onClose: () => void;
    // New Props for Settings
    currentPersona?: string;
    onPersonaChange?: (personaId: string) => void;
    riskTolerance?: number;
    onRiskChange?: (risk: number) => void;
}

export function ThoughtSidebar({
    isOpen,
    onClose,
    currentPersona = "grandma",
    onPersonaChange,
    riskTolerance = 0.5,
    onRiskChange
}: ThoughtSidebarProps) {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [activeTab, setActiveTab] = useState<"logs" | "settings">("logs");

    useEffect(() => {
        if (isOpen) {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            fetch(`${API_URL}/logs`)
                .then(res => res.json())
                .then(data => setLogs(data))
                .catch(err => console.error("Failed to load logs:", err));
        }
    }, [isOpen]);

    return (
        <>
            {/* Backdrop */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 transition-opacity"
                    onClick={onClose}
                />
            )}

            {/* Sidebar */}
            <div className={cn(
                "fixed inset-y-0 right-0 z-50 w-96 bg-[#0c0c0e] border-l border-white/10 shadow-2xl transform transition-transform duration-300 ease-in-out flex flex-col",
                isOpen ? "translate-x-0" : "translate-x-full"
            )}>
                {/* Header with Tabs */}
                <div className="bg-[#050505] border-b border-white/10">
                    <div className="p-4 flex justify-between items-center">
                        <div className="flex items-center gap-2 text-blue-400">
                            <Cpu className="w-5 h-5" />
                            <h2 className="font-semibold text-sm uppercase tracking-wider">Control Center</h2>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-1 text-zinc-500 hover:text-white transition-colors"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    <div className="flex px-4 gap-4 pb-2">
                        <button
                            onClick={() => setActiveTab("logs")}
                            className={cn(
                                "text-[10px] font-bold uppercase tracking-widest pb-2 transition-all",
                                activeTab === "logs" ? "text-blue-400 border-b-2 border-blue-400" : "text-zinc-500 hover:text-zinc-300"
                            )}
                        >
                            Agent Thoughts
                        </button>
                        <button
                            onClick={() => setActiveTab("settings")}
                            className={cn(
                                "text-[10px] font-bold uppercase tracking-widest pb-2 transition-all",
                                activeTab === "settings" ? "text-blue-400 border-b-2 border-blue-400" : "text-zinc-500 hover:text-zinc-300"
                            )}
                        >
                            System Settings
                        </button>
                    </div>
                </div>

                {/* Content Area */}
                <div className="flex-1 overflow-y-auto">
                    {activeTab === "logs" ? (
                        <div className="p-4 space-y-4 font-mono text-xs">
                            {/* Logs Stream (Existing Logic) */}
                            {logs.length === 0 ? (
                                <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
                                    <div className="relative">
                                        <Cpu className="w-12 h-12 text-zinc-800" />
                                        <div className="absolute inset-0 w-12 h-12 bg-blue-500/10 rounded-full animate-ping" />
                                    </div>
                                    <div className="space-y-1">
                                        <p className="text-zinc-400 font-medium">Neural Link Active</p>
                                        <p className="text-zinc-600 text-[10px] max-w-[200px] leading-relaxed">
                                            Awaiting agent signals from the network...
                                        </p>
                                    </div>
                                </div>
                            ) : (
                                logs.map((log, i) => (
                                    <div key={i} className="flex gap-3 animate-in fade-in slide-in-from-right-4 duration-300">
                                        <span className="text-zinc-600 shrink-0">
                                            {new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                                        </span>
                                        <div className="space-y-1">
                                            <span className={cn(
                                                "font-bold uppercase text-[10px] px-1.5 py-0.5 rounded border",
                                                log.agent === "ContentSwarm" ? "text-purple-400 border-purple-500/30 bg-purple-500/10" :
                                                    log.agent === "PolicyAgent" ? "text-yellow-400 border-yellow-500/30 bg-yellow-500/10" :
                                                        log.agent === "TrafficAgent" ? "text-green-400 border-green-500/30 bg-green-500/10" :
                                                            "text-blue-400 border-blue-500/30 bg-blue-500/10"
                                            )}>
                                                {log.agent}
                                            </span>
                                            <p className="text-zinc-300 leading-relaxed">
                                                {log.message}
                                            </p>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    ) : (
                        <div className="p-6 space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
                            {/* Persona Selector Integration */}
                            <div>
                                <h4 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">Curation Vibe</h4>
                                <div className="grid grid-cols-1 gap-2">
                                    {["grandma", "degen", "corporate"].map((p) => (
                                        <button
                                            key={p}
                                            onClick={() => onPersonaChange?.(p)}
                                            className={cn(
                                                "w-full p-4 rounded-xl border text-left transition-all",
                                                currentPersona === p
                                                    ? "bg-blue-500/10 border-blue-500/50 text-blue-400"
                                                    : "bg-white/5 border-white/10 text-zinc-400 hover:bg-white/10"
                                            )}
                                        >
                                            <div className="flex items-center justify-between">
                                                <span className="font-bold capitalize">{p}</span>
                                                {currentPersona === p && <Check className="w-4 h-4" />}
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Risk Tolerance Slider */}
                            <div className="space-y-4">
                                <div className="flex justify-between items-center">
                                    <h4 className="text-xs font-bold text-gray-500 uppercase tracking-widest">Risk Tolerance</h4>
                                    <span className="text-blue-400 font-mono text-xs">{(riskTolerance * 100).toFixed(0)}%</span>
                                </div>
                                <input
                                    type="range"
                                    min="0"
                                    max="1"
                                    step="0.1"
                                    value={riskTolerance}
                                    onChange={(e) => onRiskChange?.(parseFloat(e.target.value))}
                                    className="w-full h-1 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
                                />
                                <div className="flex justify-between text-[8px] text-zinc-600 uppercase font-black tracking-tighter">
                                    <span>Conservative</span>
                                    <span>Moonshot</span>
                                </div>
                            </div>

                            {/* Social Connections */}
                            <div className="border-t border-white/10 pt-6">
                                <SocialConnections />
                            </div>
                        </div>
                    )}
                </div>

                <div className="p-3 border-t border-white/10 bg-[#050505] text-[10px] text-zinc-500 flex justify-between">
                    <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                        System Logic: {currentPersona.toUpperCase()}
                    </div>
                    <span>v0.3.0-growth</span>
                </div>
            </div>
        </>
    );
}
