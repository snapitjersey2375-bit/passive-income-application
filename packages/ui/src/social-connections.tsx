"use client";

import React, { useState, useEffect } from "react";
import { Check, Link, Unlink, Loader2 } from "lucide-react";
import { cn } from "./utils/cn";

interface Connection {
    id: string;
    platform: string;
    account_name: string;
    is_active: boolean;
}

interface Platform {
    id: string;
    name: string;
    color: string;
    icon: string;
}

const PLATFORMS: Platform[] = [
    { id: "tiktok", name: "TikTok", color: "bg-black", icon: "🎵" },
    { id: "youtube", name: "YouTube", color: "bg-red-600", icon: "📺" },
    { id: "instagram", name: "Instagram", color: "bg-gradient-to-br from-purple-500 via-pink-500 to-orange-400", icon: "📷" },
];

export function SocialConnections() {
    const [connections, setConnections] = useState<Connection[]>([]);
    const [loading, setLoading] = useState<string | null>(null);

    const API_URL = typeof window !== 'undefined'
        ? (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
            ? 'http://localhost:8000'
            : 'https://passive-income-application.onrender.com')
        : 'https://passive-income-application.onrender.com';

    useEffect(() => {
        fetchConnections();
    }, []);

    const fetchConnections = async () => {
        try {
            const res = await fetch(`${API_URL}/social/connections`);
            if (res.ok) {
                const data = await res.json();
                setConnections(data.connections || []);
            }
        } catch (error) {
            console.error("Failed to fetch connections:", error);
        }
    };

    const connectPlatform = async (platform: string) => {
        setLoading(platform);
        try {
            const res = await fetch(`${API_URL}/social/connect/${platform}`, { method: "POST" });
            if (res.ok) {
                await fetchConnections();
            }
        } catch (error) {
            console.error("Connect failed:", error);
        } finally {
            setLoading(null);
        }
    };

    const disconnectPlatform = async (platform: string) => {
        setLoading(platform);
        try {
            const res = await fetch(`${API_URL}/social/disconnect/${platform}`, { method: "DELETE" });
            if (res.ok) {
                await fetchConnections();
            }
        } catch (error) {
            console.error("Disconnect failed:", error);
        } finally {
            setLoading(null);
        }
    };

    const getConnectionForPlatform = (platformId: string) => {
        return connections.find(c => c.platform === platformId && c.is_active);
    };

    return (
        <div className="space-y-4">
            <h4 className="text-xs font-bold text-gray-500 uppercase tracking-widest">Connected Accounts</h4>
            <div className="space-y-2">
                {PLATFORMS.map((platform) => {
                    const connection = getConnectionForPlatform(platform.id);
                    const isLoading = loading === platform.id;
                    const isConnected = !!connection;

                    return (
                        <div
                            key={platform.id}
                            className={cn(
                                "flex items-center justify-between p-3 rounded-xl border transition-all",
                                isConnected
                                    ? "border-green-500/30 bg-green-500/5"
                                    : "border-white/10 bg-white/5"
                            )}
                        >
                            <div className="flex items-center gap-3">
                                <div className={cn(
                                    "w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm",
                                    platform.color
                                )}>
                                    {platform.icon}
                                </div>
                                <div>
                                    <div className="font-bold text-sm text-white">{platform.name}</div>
                                    {connection && (
                                        <div className="text-[10px] text-green-400 font-medium">
                                            {connection.account_name}
                                        </div>
                                    )}
                                </div>
                            </div>

                            <button
                                onClick={() => isConnected ? disconnectPlatform(platform.id) : connectPlatform(platform.id)}
                                disabled={isLoading}
                                className={cn(
                                    "px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5",
                                    isConnected
                                        ? "bg-red-500/10 text-red-400 hover:bg-red-500/20"
                                        : "bg-blue-500/10 text-blue-400 hover:bg-blue-500/20"
                                )}
                            >
                                {isLoading ? (
                                    <Loader2 className="w-3 h-3 animate-spin" />
                                ) : isConnected ? (
                                    <>
                                        <Unlink className="w-3 h-3" />
                                        Disconnect
                                    </>
                                ) : (
                                    <>
                                        <Link className="w-3 h-3" />
                                        Connect
                                    </>
                                )}
                            </button>
                        </div>
                    );
                })}
            </div>

            {connections.filter(c => c.is_active).length > 0 && (
                <div className="text-[10px] text-green-400/70 flex items-center gap-1 pt-2">
                    <Check className="w-3 h-3" />
                    Connect accounts for easy copying to clipboard
                </div>
            )}
        </div>
    );
}
