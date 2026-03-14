"use client";

import React, { useState, useEffect } from "react";
import { DashboardShell } from "@repo/ui";
import { Shield, Monitor, Key, Save, AlertCircle, Link2, Unlink, CheckCircle2, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";

interface SocialConnection {
    id: string;
    platform: string;
    account_name: string;
    is_active: boolean;
    created_at: string | null;
}

export default function SettingsPage() {
    const [riskTolerance, setRiskTolerance] = useState(0.5);
    const [isGrandmaMode, setIsGrandmaMode] = useState(false);

    // Economy State
    const [balance, setBalance] = useState(0.0);
    const [referralCode, setReferralCode] = useState("");
    const [referralInput, setReferralInput] = useState("");
    const [isClaiming, setIsClaiming] = useState(false);

    // Social Connections State
    const [connections, setConnections] = useState<SocialConnection[]>([]);
    const [connectingPlatform, setConnectingPlatform] = useState<string | null>(null);

    const { user, logout, requireAuth } = useAuth();
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [message, setMessage] = useState({ type: "", text: "" });
    const router = useRouter();

    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    useEffect(() => {
        requireAuth();
        if (user) {
            fetchSettings();
            fetchConnections();
        }
    }, [user]);

    const fetchSettings = async () => {
        setIsLoading(true);
        try {
            const token = localStorage.getItem("nexus_token");
            const res = await fetch(`${API_URL}/user/settings`, {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });
            if (res.status === 401) {
                logout();
                return;
            }
            if (res.ok) {
                const data = await res.json();
                setRiskTolerance(data.risk_tolerance);
                setIsGrandmaMode(data.is_grandma_mode);
                setBalance(data.wallet_balance || 0.0);
                setReferralCode(data.referral_code || "");
            }
        } catch (error) {
            console.error("Failed to fetch settings:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const fetchConnections = async () => {
        try {
            const token = localStorage.getItem("nexus_token");
            const res = await fetch(`${API_URL}/social/connections`, {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });
            if (res.status === 401) {
                logout();
                return;
            }
            if (res.ok) {
                const data = await res.json();
                setConnections(data.connections || []);
            }
        } catch (error) {
            console.error("Failed to fetch connections:", error);
        }
    };

    const handleConnect = async (platform: string) => {
        setConnectingPlatform(platform);
        try {
            const token = localStorage.getItem("nexus_token");
            const res = await fetch(`${API_URL}/social/connect/${platform}`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });
            if (res.status === 401) {
                logout();
                return;
            }
            if (res.ok) {
                const data = await res.json();
                setMessage({ type: "success", text: `Connected to ${platform}! Account: ${data.account_name}` });
                fetchConnections();
            } else {
                throw new Error("Failed to connect");
            }
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (error: unknown) {
            setMessage({ type: "error", text: (error as Error).message });
        } finally {
            setConnectingPlatform(null);
        }
    };

    const handleDisconnect = async (platform: string) => {
        setConnectingPlatform(platform);
        try {
            const token = localStorage.getItem("nexus_token");
            const res = await fetch(`${API_URL}/social/disconnect/${platform}`, {
                method: "DELETE",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });
            if (res.status === 401) {
                logout();
                return;
            }
            if (res.ok) {
                setMessage({ type: "success", text: `Disconnected from ${platform}` });
                fetchConnections();
            } else {
                throw new Error("Failed to disconnect");
            }
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (error: unknown) {
            setMessage({ type: "error", text: (error as Error).message });
        } finally {
            setConnectingPlatform(null);
        }
    };

    const isConnected = (platform: string) => {
        return connections.some(c => c.platform === platform && c.is_active);
    };

    const handleManualConnect = async (platform: string, tokenData: string) => {
        setConnectingPlatform(platform);
        try {
            const token = localStorage.getItem("nexus_token");
            const res = await fetch(`${API_URL}/social/connect/manual`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    platform,
                    access_token: tokenData,
                    account_name: `@manual_${platform}`
                })
            });
            if (res.status === 401) {
                logout();
                return;
            }
            if (res.ok) {
                setMessage({ type: "success", text: `Manually connected to ${platform}!` });
                fetchConnections();
            } else {
                throw new Error("Failed to connect manually");
            }
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (error: unknown) {
            setMessage({ type: "error", text: (error as Error).message });
        } finally {
            setConnectingPlatform(null);
        }
    };

    const getConnection = (platform: string) => {
        return connections.find(c => c.platform === platform && c.is_active);
    };

    const handleClaimReferral = async () => {
        setIsClaiming(true);
        try {
            const storedUser = localStorage.getItem("nexus_user");
            const token = localStorage.getItem("nexus_token");

            if (!storedUser || !token) {
                setMessage({ type: "error", text: "Session info not found. Please relogin." });
                return;
            }

            const user = JSON.parse(storedUser);

            const res = await fetch(`${API_URL}/user/referral/claim`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    user_id: user.id,
                    code: referralInput
                }),
            });

            if (res.status === 401) {
                logout();
                return;
            }

            if (res.ok) {
                const data = await res.json();
                setMessage({ type: "success", text: `Connected! Referred by ${data.referrer_email}` });
                setReferralInput("");
            } else {
                const err = await res.json();
                throw new Error(err.detail || "Failed to claim");
            }
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (error: unknown) {
            setMessage({ type: "error", text: (error as Error).message });
        } finally {
            setIsClaiming(false);
        }
    };

    const handleSave = async () => {
        setIsSaving(true);
        setMessage({ type: "", text: "" });
        try {
            const token = localStorage.getItem("nexus_token");
            const res = await fetch(`${API_URL}/user/settings`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    risk_tolerance: riskTolerance,
                    is_grandma_mode: isGrandmaMode
                }),
            });

            if (res.status === 401) {
                logout();
                return;
            }
            if (res.ok) {
                setMessage({ type: "success", text: "Settings saved successfully!" });
                setTimeout(() => setMessage({ type: "", text: "" }), 3000);
            } else {
                throw new Error("Failed to save settings");
            }
        } catch (error) {
            setMessage({ type: "error", text: "Failed to save settings. Please try again." });
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) {
        return (
            <DashboardShell>
                <div className="flex items-center justify-center h-screen">
                    <p className="text-gray-600">Loading settings...</p>
                </div>
            </DashboardShell>
        );
    }

    const platforms = [
        { id: "tiktok", name: "TikTok", color: "bg-black", icon: "🎵" },
        { id: "youtube", name: "YouTube", color: "bg-red-600", icon: "▶️" },
        { id: "shopify", name: "Shopify", color: "bg-green-600", icon: "🛍️" },
    ];

    return (
        <DashboardShell>
            <div className="max-w-4xl mx-auto p-6 space-y-8">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Supervisor Settings</h1>
                    <p className="text-gray-500 mt-2">Manage your platform defaults and agent behavior.</p>
                </div>

                {message.text && (
                    <div className={`p-4 rounded-xl flex items-center gap-3 ${message.type === "success" ? "bg-green-50 text-green-700 border border-green-100" : "bg-red-50 text-red-700 border border-red-100"}`}>
                        <AlertCircle size={20} />
                        <p className="font-medium">{message.text}</p>
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Social Connections */}
                    <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 space-y-6 md:col-span-2">
                        <div className="flex items-center gap-3">
                            <Key size={24} className="text-blue-600" />
                            <h2 className="text-xl font-bold text-gray-800">Connected Accounts</h2>
                            <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">Publisher</span>
                        </div>
                        <p className="text-sm text-gray-500">Connect your social accounts to keep links handy for manual publishing.</p>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {platforms.map((platform) => {
                                const connected = isConnected(platform.id);
                                const conn = getConnection(platform.id);
                                const isConnecting = connectingPlatform === platform.id;
                                return (
                                    <div key={platform.id} className={`p-4 rounded-xl border-2 transition-all ${connected ? "border-green-200 bg-green-50" : "border-gray-100 bg-gray-50 hover:border-gray-200"}`}>
                                        <div className="flex items-center gap-3 mb-3">
                                            <div className={`w-10 h-10 ${platform.color} rounded-lg flex items-center justify-center text-white text-lg`}>{platform.icon}</div>
                                            <div>
                                                <p className="font-bold text-gray-800">{platform.name}</p>
                                                {connected && conn && (<p className="text-xs text-green-600 font-medium">{conn.account_name}</p>)}
                                            </div>
                                        </div>
                                        {connected ? (
                                            <button onClick={() => handleDisconnect(platform.id)} disabled={isConnecting} className="w-full flex items-center justify-center gap-2 py-2 px-4 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-600 hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition-all disabled:opacity-50">
                                                {isConnecting ? <Loader2 size={16} className="animate-spin" /> : <><Unlink size={14} /> Disconnect</>}
                                            </button>
                                        ) : (
                                            <div className="space-y-2">
                                                <button onClick={() => handleConnect(platform.id)} disabled={isConnecting} className="w-full flex items-center justify-center gap-2 py-2 px-4 bg-blue-600 text-white rounded-lg text-sm font-bold hover:bg-blue-700 transition-all disabled:opacity-50">
                                                    {isConnecting ? <Loader2 size={16} className="animate-spin" /> : <><Link2 size={14} /> Mock Connect</>}
                                                </button>
                                                <div className="h-px bg-gray-200 my-2" />
                                                <div className="flex gap-1">
                                                    <input type="password" placeholder="API Token" id={`token-${platform.id}`} className="flex-1 text-xs p-2 border border-gray-200 rounded focus:ring-1 focus:ring-blue-500 outline-none" />
                                                    <button onClick={() => { const input = document.getElementById(`token-${platform.id}`) as HTMLInputElement; if (input.value) handleManualConnect(platform.id, input.value); }} className="p-2 bg-gray-800 text-white rounded-lg hover:bg-black transition"><Save size={14} /></button>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* AI Credits */}
                    <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 space-y-6 md:col-span-2">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3 text-green-600">
                                <h2 className="text-xl font-bold text-gray-800">AI Credit Balance</h2>
                                <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">Live</span>
                            </div>
                            <div className="text-right">
                                <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Available Generation Credits</p>
                                <p className="text-4xl font-black text-gray-900">${balance.toFixed(2)}</p>
                            </div>
                        </div>
                        <div className="h-px bg-gray-100 w-full" />
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="space-y-4">
                                <h3 className="font-bold text-gray-800">Your Referral Code</h3>
                                <div className="flex gap-2">
                                    <div className="flex-1 bg-gray-50 border-2 border-dashed border-gray-200 rounded-xl p-3 text-center font-mono font-bold text-xl tracking-widest text-gray-700 select-all">{referralCode || "LOADING..."}</div>
                                    <button onClick={() => { navigator.clipboard.writeText(referralCode); setMessage({ type: "success", text: "Code copied to clipboard!" }); }} className="px-4 bg-gray-100 hover:bg-gray-200 rounded-xl font-bold text-gray-600 transition">Copy</button>
                                </div>
                            </div>
                            <div className="space-y-4">
                                <h3 className="font-bold text-gray-800">Have a Code?</h3>
                                <div className="flex gap-2">
                                    <input type="text" placeholder="ENTER-CODE" value={referralInput} onChange={(e) => setReferralInput(e.target.value.toUpperCase())} className="flex-1 bg-white border border-gray-200 rounded-xl p-3 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 uppercase" />
                                    <button onClick={handleClaimReferral} disabled={isClaiming || !referralInput} className="px-4 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 transition disabled:opacity-50 text-sm">{isClaiming ? "..." : "Claim"}</button>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Agent Risk Tolerance */}
                    <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 space-y-6">
                        <div className="flex items-center gap-3 text-blue-600">
                            <Shield size={24} />
                            <h2 className="text-xl font-bold text-gray-800">Agent Strategy</h2>
                        </div>
                        <div className="space-y-4">
                            <label className="block">
                                <span className="text-sm font-semibold text-gray-700 flex justify-between">Risk Tolerance <span className="text-blue-600">{(riskTolerance * 100).toFixed(0)}%</span></span>
                                <input type="range" min="0" max="1" step="0.05" value={riskTolerance} onChange={(e) => setRiskTolerance(parseFloat(e.target.value))} className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer mt-4 accent-blue-600" />
                            </label>
                        </div>
                    </div>

                    {/* UI Preferences */}
                    <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 space-y-6">
                        <div className="flex items-center gap-3 text-purple-600">
                            <Monitor size={24} />
                            <h2 className="text-xl font-bold text-gray-800">Interface Defaults</h2>
                        </div>
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <div><p className="font-semibold text-gray-700">Grandma Mode</p><p className="text-xs text-gray-500">High contrast, larger text.</p></div>
                                <label className="relative inline-flex items-center cursor-pointer">
                                    <input type="checkbox" className="sr-only peer" checked={isGrandmaMode} onChange={(e) => setIsGrandmaMode(e.target.checked)} />
                                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                                </label>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex justify-end gap-4 mt-8">
                    <button onClick={() => router.push("/dashboard")} className="px-6 py-2 text-gray-600 font-semibold hover:text-gray-900 transition">Cancel</button>
                    <button onClick={handleSave} disabled={isSaving} className="flex items-center gap-2 px-8 py-2 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 transition shadow-lg shadow-blue-200 disabled:opacity-50">
                        {isSaving ? "Saving..." : <><Save size={18} /> Save Changes</>}
                    </button>
                </div>
            </div>
        </DashboardShell>
    );
}
