"use client";

import React, { useState, useEffect } from "react";
import {
    DashboardShell,
    GrandmaToggle,
    SwipeCard,
    SlotMachine,
    ViralLineChart,
    RevenueBarChart,
    TopicSelector,
    ThoughtSidebar,
    LedgerView,
    DeviceSimulator,
    ReferralPanel,
    ActivityTicker,
    FounderMindset,
    useGrandma,
    useToast,
    VideoPlayer,
    RemixModal
} from "@repo/ui";
import { useAuth } from "@/hooks/use-auth";
import { getApiUrl } from "@/lib/api-url";
import { Check, X, Eye, Heart, MessageCircle, Share2, TrendingUp, Settings as SettingsIcon, LogOut, MessageSquare, Zap, Wallet } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AnimatePresence } from "framer-motion";

interface AnalyticsData {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    viral_trends: any[];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    revenue_projections: any[];
    summary: {
        total_views: number;
        total_revenue: number;
        approved_count: number;
    };
}

interface ContentItem {
    id: string;
    title: string;
    description?: string;
    confidence_score: number;
    status: string;
    thumbnail_url: string;
    view_count: number;
    like_count: number;
    comment_count: number;
    share_count: number;
    viral_potential: number;
    monetization_potential: number;
    video_url?: string;
}

export default function DashboardPage() {
    const { user, isLoading: authLoading, logout, requireAuth } = useAuth();
    const { isGrandmaMode } = useGrandma();
    const { success, error: showError } = useToast();
    const router = useRouter();
    const [streak, setStreak] = useState(0);
    const [cards, setCards] = useState<ContentItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const [showAgentThoughts, setShowAgentThoughts] = useState(false);
    const [showBrokeModal, setShowBrokeModal] = useState(false);
    const [remixItem, setRemixItem] = useState<ContentItem | null>(null);
    const [isRequestingBudget, setIsRequestingBudget] = useState(false);
    const [activeTab, setActiveTab] = useState<"queue" | "stats" | "wallet">("queue");
    const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
    const [selectedTopic, setSelectedTopic] = useState("General");
    const [searchQuery, setSearchQuery] = useState("");
    const [orientation, setOrientation] = useState<"portrait" | "landscape">("portrait");
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const [settings, setSettings] = useState<any>(null); // Added for setSettings in requestAdditionalBudget

    useEffect(() => {
        // Only redirect if auth has finished loading and there's no user
        if (!authLoading && !user) {
            // Double-check localStorage before redirecting
            const storedUser = localStorage.getItem("nexus_user");
            const storedToken = localStorage.getItem("nexus_token");

            if (!storedUser || !storedToken) {
                router.push("/login");
            }
        } else if (user) {
            fetchQueue();
            fetchSettings();
            fetchAnalytics();
        }
    }, [user, authLoading]);

    const fetchSettings = async () => {
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
                setSettings(data);
            }
        } catch (error) {
            console.error("Failed to fetch settings:", error);
        }
    };

    const fetchAnalytics = async () => {
        try {
            const token = localStorage.getItem("nexus_token");
            const res = await fetch(`${API_URL}/analytics/stats`, {
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
                setAnalytics(data);
            }
        } catch (error) {
            console.error("Failed to fetch analytics:", error);
        }
    };

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const updateUserSettings = async (newSettings: any) => {
        // Optimistic update
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        setSettings((prev: any) => ({ ...prev, ...newSettings }));

        try {
            const token = localStorage.getItem("nexus_token");
            const res = await fetch(`${API_URL}/user/settings`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    risk_tolerance: newSettings?.risk_tolerance ?? settings?.risk_tolerance ?? 0.5,
                    is_grandma_mode: newSettings?.is_grandma_mode ?? settings?.is_grandma_mode ?? false,
                    persona: newSettings?.persona ?? settings?.persona ?? "grandma",
                    ...newSettings
                })
            });
            if (res.status === 401) {
                logout();
                return;
            }
            if (!res.ok) throw new Error("Update failed");
            success("System Reconfigured");
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: unknown) {
            showError("Failed to update settings");
            fetchSettings(); // Rollback
        }
    };

    const API_URL = getApiUrl();

    const fetchQueue = async () => {
        setIsLoading(true);
        try {
            const token = localStorage.getItem("nexus_token");
            const endpoint = searchQuery
                ? `${API_URL}/content/search?q=${encodeURIComponent(searchQuery)}`
                : `${API_URL}/queue/daily`;

            const res = await fetch(endpoint, {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });
            if (res.status === 401) {
                logout();
                return;
            }
            const data = await res.json();
            setCards(searchQuery ? data.results : data.queue || []);
        } catch (error) {
            console.error("Failed to fetch queue:", error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (user && activeTab === "queue") {
            const timeoutId = setTimeout(() => {
                fetchQueue();
            }, 300); // debounce search
            return () => clearTimeout(timeoutId);
        }
    }, [searchQuery]);

    const handleSwipe = async (direction: "left" | "right") => {
        // Get the current card (top of the stack is the last element)
        if (cards.length === 0) return;
        const currentCard = cards[cards.length - 1];

        // Optimistic UI update
        const newCards = cards.slice(0, -1);
        setCards(newCards);

        try {
            const token = localStorage.getItem("nexus_token");
            if (direction === "right") {
                setStreak((s) => s + 1);
                // Blocking wait to catch errors
                const res = await fetch(`${API_URL}/queue/${currentCard.id}/approve`, {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                });
                if (!res.ok) {
                    if (res.status === 402) {
                        setShowBrokeModal(true);
                        throw new Error("Insufficient Funds");
                    }
                    if (res.status === 429 || res.status === 503) {
                        const data = await res.json();
                        throw new Error(data.detail || "Circuit Breaker Tripped");
                    }
                    throw new Error("Server Error");
                }
                success(isGrandmaMode ? "That&apos;s lovely, dear! It&apos;s official! 🧶" : "Content Approved! 🚀");
            } else {
                setStreak(0);
                const res = await fetch(`${API_URL}/queue/${currentCard.id}/reject`, {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                });
                if (!res.ok) {
                    throw new Error("Rejection Failed");
                }
                success(isGrandmaMode ? "Right into the bin, dear! 🗑️" : "Content Discarded");
            }
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: unknown) {
            console.error("Action failed", err);
            const msg = isGrandmaMode ? `Oh dear! ${(err as Error).message || "Something went wrong"}` : ((err as Error).message || "Action failed");
            showError(msg);
            // Rolling back optimistic update (simple reload for Phase 1)
            fetchQueue();
        }
    };

    // Keyboard Shortcuts for Power Users
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            // Only trigger if not typing in an input
            if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
            // Only active on queue tab
            if (activeTab !== "queue" || cards.length === 0 || isLoading) return;

            if (e.key === "ArrowRight" || e.key === " ") {
                e.preventDefault();
                handleSwipe("right");
            } else if (e.key === "ArrowLeft") {
                e.preventDefault();
                handleSwipe("left");
            } else if (e.key === "Escape") {
                setShowBrokeModal(false);
                setIsSidebarOpen(false);
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [activeTab, cards, isLoading]);

    useEffect(() => {
        if (activeTab === "stats") {
            fetchAnalytics();
        }
    }, [activeTab]);

    const handleGenerate = async () => {
        setIsLoading(true);
        // Trigger Swarm with selected topic
        try {
            const token = localStorage.getItem("nexus_token");
            const res = await fetch(`${API_URL}/content/swarm?niche=${selectedTopic}`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });
            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || "Generation failed");
            }
            success(isGrandmaMode ? "Grandma is thinking of something fun! 🥧" : `New ${selectedTopic} ideas generated!`);
            // Refresh queue after generating
            await fetchQueue();
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: unknown) {
            console.error("Failed to generate content:", err);
            const msg = isGrandmaMode ? `Oh dear! ${(err as Error).message || "The thinking machine is tired"}` : ((err as Error).message || "Failed to generate content");
            showError(msg);
        }
    };

    const handleSaveRemix = async (id: string, newTitle: string, newDesc: string) => {
        try {
            const token = localStorage.getItem("nexus_token");
            const res = await fetch(`${API_URL}/content/${id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ title: newTitle, description: newDesc })
            });
            if (!res.ok) throw new Error("Failed to save changes");

            // Optimistically update the card in the local state
            setCards(prev => prev.map(c => c.id === id ? { ...c, title: newTitle, description: newDesc } : c));
            success("Content updated successfully ✨");
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: unknown) {
            showError("Failed to save your edits");
        }
    };

    const handleSimulate = async () => {
        setIsLoading(true);
        try {
            const token = localStorage.getItem("nexus_token");
            await fetch(`${API_URL}/analytics/simulate`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });
            await fetchAnalytics();
        } catch (error) {
            console.error("Simulation failed:", error);
        } finally {
            setIsLoading(false);
        }
    };
    const requestAdditionalBudget = async () => {
        setIsRequestingBudget(true);
        try {
            const token = localStorage.getItem("nexus_token");
            const res = await fetch(`${API_URL}/user/capital/inject`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });
            if (!res.ok) throw new Error("Injection failed");
            success(isGrandmaMode ? "Here is some pocket money, dear! 🍬" : "Capital Injection Successful! +$50");
            setShowBrokeModal(false);
            // Refresh settings to see new balance
            const settingsRes = await fetch(`${API_URL}/user/settings`, {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });
            if (settingsRes.ok) {
                const settingsData = await settingsRes.json();
                setSettings(settingsData);
            }
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: unknown) {
            showError((err as Error).message || "Failed to inject capital");
        } finally {
            setIsRequestingBudget(false);
        }
    };

    if (authLoading || !user) {
        return (
            <div className="min-h-screen bg-[#050505] flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
                    <p className="text-zinc-500 text-sm font-medium tracking-widest uppercase">Initializing Security...</p>
                </div>
            </div>
        );
    }

    return (
        <DashboardShell
            headerContent={
                <div className="flex items-center gap-4">
                    {/* Topic Selector in Header */}
                    <div className="hidden md:block">
                        <TopicSelector
                            selectedTopic={selectedTopic}
                            onSelect={setSelectedTopic}
                        />
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="hidden md:flex relative">
                            <input
                                type="text"
                                placeholder="Search content..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="pl-9 pr-4 py-1.5 rounded-lg text-sm bg-white/50 backdrop-blur-md border border-white/50 shadow-inner focus:outline-none focus:ring-2 focus:ring-blue-500/50 w-48 transition-all"
                            />
                            <div className="absolute left-3 top-2 text-gray-500 opacity-70">
                                🔍
                            </div>
                        </div>

                        <div className="flex bg-white/50 backdrop-blur-md border border-white/50 p-1 rounded-xl shadow-inner">
                            <button
                                onClick={() => setActiveTab("queue")}
                                className={`px-4 py-1.5 rounded-lg text-sm font-semibold transition-all duration-200 ${activeTab === "queue"
                                    ? "bg-white shadow-sm text-blue-600 ring-1 ring-black/5"
                                    : "text-gray-500 hover:text-gray-700 hover:bg-white/30"
                                    }`}
                            >
                                {isGrandmaMode ? "The Waiting Room" : "Review Queue"}
                            </button>
                            <button
                                onClick={() => setActiveTab("stats")}
                                className={`px-4 py-1.5 rounded-lg text-sm font-semibold transition-all duration-200 ${activeTab === "stats"
                                    ? "bg-white shadow-sm text-blue-600 ring-1 ring-black/5"
                                    : "text-gray-500 hover:text-gray-700 hover:bg-white/30"
                                    }`}
                            >
                                {isGrandmaMode ? "My Success Book" : "Analytics"}
                            </button>
                            <button
                                onClick={() => setActiveTab("wallet")}
                                className={`px-4 py-1.5 rounded-lg text-sm font-semibold transition-all duration-200 ${activeTab === "wallet"
                                    ? "bg-white shadow-sm text-blue-600 ring-1 ring-black/5"
                                    : "text-gray-500 hover:text-gray-700 hover:bg-white/30"
                                    }`}
                            >
                                {isGrandmaMode ? "My Checkbook" : "Ledger"}
                            </button>
                        </div>
                    </div>

                    <SlotMachine value={`Streak: ${streak} 🔥`} key={streak} />
                    <Link
                        href="/dashboard/settings"
                        className="p-2 bg-white/50 backdrop-blur-md border border-white/50 rounded-xl shadow-sm hover:bg-white/80 transition-all text-gray-600 hover:text-blue-600"
                        title="Settings"
                    >
                        <SettingsIcon size={20} />
                    </Link>

                    <button
                        onClick={() => setIsSidebarOpen(true)}
                        className="p-2 bg-white/50 backdrop-blur-md border border-white/50 rounded-xl shadow-sm hover:bg-blue-50 hover:text-blue-600 transition-all"
                        title="Agent Thoughts"
                    >
                        <MessageSquare size={20} />
                    </button>

                    <button
                        onClick={() => setOrientation(o => o === "portrait" ? "landscape" : "portrait")}
                        className="p-2 bg-white/50 backdrop-blur-md border border-white/50 rounded-xl shadow-sm hover:bg-blue-50 hover:text-blue-600 transition-all"
                        title="Rotate Device"
                    >
                        <Zap size={20} className={orientation === "landscape" ? "rotate-90" : ""} />
                    </button>

                    <button
                        onClick={logout}
                        className="p-2 bg-white/50 backdrop-blur-md border border-white/50 rounded-xl shadow-sm hover:bg-red-50 hover:text-red-600 transition-all"
                        title="Logout"
                    >
                        <LogOut size={20} />
                    </button>

                    <GrandmaToggle />
                </div>
            }
        >
            {activeTab === "queue" ? (
                <div className="flex flex-col items-center justify-center min-h-[70vh] gap-8">
                    <div className="relative w-full max-w-4xl h-[70vh] flex items-center justify-center">
                        {isLoading ? (
                            <div className="animate-pulse flex flex-col items-center">
                                <div className="h-64 w-64 bg-gray-200 rounded-xl mb-4"></div>
                                <div className="h-4 w-32 bg-gray-200 rounded"></div>
                            </div>
                        ) : cards.length > 0 ? (
                            <DeviceSimulator orientation={orientation}>
                                <div className="relative w-full h-full flex items-center justify-center">
                                    <AnimatePresence>
                                        {cards.map((item, index) => (
                                            <SwipeCard
                                                key={item.id}
                                                className={index === cards.length - 1 ? "z-10" : "z-0 scale-95 opacity-50"}
                                                onSwipeRight={() => handleSwipe("right")}
                                                onSwipeLeft={() => handleSwipe("left")}
                                                disabled={index !== cards.length - 1}
                                            >
                                                <div className="h-full flex flex-col">
                                                    {/* Immersive Background */}
                                                    <div className="relative flex-1 bg-black overflow-hidden group">
                                                        <VideoPlayer
                                                            src={item.video_url || "https://assets.mixkit.co/videos/preview/mixkit-girl-in-neon-light-39895-large.mp4"}
                                                            className="w-full h-full object-cover opacity-80"
                                                        />
                                                        <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-transparent to-black/80" />

                                                        <div className="absolute bottom-4 left-4 right-4 text-left space-y-2">
                                                            <h2 className="text-xl font-bold text-white leading-tight drop-shadow-lg">{item.title}</h2>
                                                            <p className="text-white/70 text-xs line-clamp-2">{item.description}</p>

                                                            <div className="flex gap-4 pt-2">
                                                                <div className="flex items-center gap-1 text-white/90 text-[10px] font-bold">
                                                                    <Eye size={12} /> {(item.view_count / 1000).toFixed(1)}k
                                                                </div>
                                                                <div className="flex items-center gap-1 text-white/90 text-[10px] font-bold">
                                                                    <Heart size={12} /> {(item.like_count / 1000).toFixed(1)}k
                                                                </div>
                                                            </div>
                                                        </div>

                                                        <div className="absolute top-4 right-4">
                                                            <div className="px-2 py-1 bg-blue-600/80 backdrop-blur-md rounded text-[9px] text-white font-black uppercase tracking-widest">
                                                                {(item.confidence_score * 100).toFixed(0)}% {isGrandmaMode ? "Success Chance" : "Match"}
                                                            </div>
                                                        </div>
                                                    </div>

                                                    {/* Footer */}
                                                    <div className="bg-white/95 backdrop-blur-xl p-4 border-t border-gray-100">
                                                        <div className="flex justify-between items-center mb-3">
                                                            <div className="flex flex-col">
                                                                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">{isGrandmaMode ? "Pocket Money" : "Monetization"}</span>
                                                                <span className="text-lg font-black text-green-600">${item.monetization_potential.toLocaleString()}</span>
                                                            </div>
                                                            <div className="text-right">
                                                                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">{isGrandmaMode ? "Big Splash" : "Viral Score"}</span>
                                                                <div className="flex items-center justify-end gap-1">
                                                                    <TrendingUp size={14} className="text-orange-500" />
                                                                    <span className="text-lg font-black text-orange-500">{item.viral_potential.toFixed(1)}</span>
                                                                </div>
                                                            </div>
                                                        </div>

                                                        {index === cards.length - 1 && (
                                                            <div className="flex gap-3 pt-1">
                                                                <button onClick={() => handleSwipe("left")} className="flex-1 py-2 bg-gray-100 text-gray-600 rounded-xl text-xs font-bold hover:bg-red-50 hover:text-red-600">{isGrandmaMode ? "Not Today" : "Discard"}</button>
                                                                <button onClick={() => setRemixItem(item)} className="flex-1 py-2 bg-purple-100 text-purple-600 rounded-xl text-xs font-bold hover:bg-purple-200 transition-colors">Remix ✨</button>
                                                                <button onClick={() => handleSwipe("right")} className="flex-1 py-2 bg-blue-600 text-white rounded-xl text-xs font-bold hover:bg-blue-700">{isGrandmaMode ? "I Like This!" : "Approve"}</button>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            </SwipeCard>
                                        ))}
                                    </AnimatePresence>
                                </div>
                            </DeviceSimulator>
                        ) : (
                            <div className="text-center p-8 bg-white rounded-xl shadow-lg border border-gray-100 max-w-sm w-full">
                                <h2 className="text-2xl font-bold mb-4">You&apos;re all caught up!</h2>
                                <button onClick={handleGenerate} className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition">
                                    Generate New Ideas ({selectedTopic})
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            ) : activeTab === "stats" ? (
                <div className="max-w-6xl mx-auto space-y-8 p-4">
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                        <div className="space-y-1">
                            <h2 className="text-2xl font-bold text-gray-800">Performance Analytics</h2>
                            <p className="text-gray-500 text-sm">Real-time data from your approved content library.</p>
                        </div>
                        <button
                            onClick={handleSimulate}
                            disabled={isLoading}
                            className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-bold shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 hover:-translate-y-0.5 transition-all disabled:opacity-50"
                        >
                            <Zap size={18} className={isLoading ? "animate-pulse" : ""} />
                            {isLoading ? "Simulating..." : "Simulate Traffic Growth"}
                        </button>
                    </div>

                    {analytics ? (
                        <>
                            {/* ROI Summary Cards */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 group hover:border-blue-200 transition-colors">
                                    <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Total Views</p>
                                    <div className="flex items-end gap-2">
                                        <h3 className="text-3xl font-black text-gray-900">{(analytics.summary?.total_views || 0).toLocaleString()}</h3>
                                        <span className="text-green-500 text-[10px] font-bold mb-1.5 flex items-center bg-green-50 px-1.5 py-0.5 rounded border border-green-100">
                                            <TrendingUp size={10} className="mr-1" /> LIVE
                                        </span>
                                    </div>
                                </div>
                                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 group hover:border-blue-200 transition-colors">
                                    <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Est. Revenue</p>
                                    <div className="flex items-end gap-2">
                                        <h3 className="text-3xl font-black text-blue-600">${(analytics.summary?.total_revenue || 0).toLocaleString()}</h3>
                                        <span className="text-gray-400 text-[10px] mb-1.5 font-bold uppercase tracking-tighter">Net Profit</span>
                                    </div>
                                </div>
                                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 group hover:border-blue-200 transition-colors">
                                    <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Library Size</p>
                                    <h3 className="text-3xl font-black text-gray-900">{analytics.summary?.approved_count || 0} Assets</h3>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div className="bg-white/50 backdrop-blur-md p-6 rounded-2xl border border-white/50 shadow-sm">
                                    <h4 className="text-sm font-bold text-gray-500 mb-4 uppercase tracking-wider">Viral Trajectory</h4>
                                    <ViralLineChart data={analytics.viral_trends || []} />
                                </div>
                                <div className="bg-white/50 backdrop-blur-md p-6 rounded-2xl border border-white/50 shadow-sm">
                                    <h4 className="text-sm font-bold text-gray-500 mb-4 uppercase tracking-wider">Revenue Projection</h4>
                                    <RevenueBarChart data={analytics.revenue_projections || []} />
                                </div>
                            </div>

                            {/* Referral Panel */}
                            <div className="mt-8">
                                <ReferralPanel />
                            </div>
                        </>
                    ) : (
                        <div className="text-center py-20 animate-pulse text-gray-500">
                            <div className="w-12 h-12 bg-gray-200 rounded-full mx-auto mb-4" />
                            Synchronizing Global Traffic Nodes...
                        </div>
                    )}
                </div>
            ) : activeTab === "wallet" ? (
                <div className="max-w-6xl mx-auto space-y-8 p-4">
                    <LedgerView />
                </div>
            ) : null}

            {/* Broke Modal (Solvency UX) */}
            {showBrokeModal && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
                    <div className="bg-white rounded-3xl p-8 max-w-sm w-full shadow-2xl border border-gray-100 text-center animate-in zoom-in-95 duration-300">
                        <div className="w-20 h-20 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6">
                            <Wallet className="w-10 h-10 text-red-500" />
                        </div>
                        <h3 className="text-2xl font-black text-gray-900 mb-2">
                            {isGrandmaMode ? "Oh dear, wallet is empty! 🍪" : "Solvency Alert: 0.00"}
                        </h3>
                        <p className="text-gray-500 mb-8 leading-relaxed">
                            {isGrandmaMode
                                ? "Curation is expensive, dear! Would you like some more pocket money for more knitting supplies?"
                                : "Your ad budget has been depleted. To continue scaling your content empire, you need a capital injection."}
                        </p>
                        <div className="space-y-3">
                            <button
                                onClick={requestAdditionalBudget}
                                disabled={isRequestingBudget}
                                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-black py-4 rounded-2xl shadow-lg shadow-blue-200 transition-all active:scale-95 flex items-center justify-center gap-2"
                            >
                                {isRequestingBudget ? (
                                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                ) : (
                                    <>
                                        <Zap className="w-5 h-5 fill-current" />
                                        Request $50 Capital
                                    </>
                                )}
                            </button>
                            <button
                                onClick={() => setShowBrokeModal(false)}
                                className="w-full text-gray-400 font-bold py-2 hover:text-gray-600 transition-colors"
                            >
                                {isGrandmaMode ? "Maybe later, dear" : "Dismiss"}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {remixItem && (
                <RemixModal
                    item={remixItem}
                    isOpen={!!remixItem}
                    onClose={() => setRemixItem(null)}
                    onSave={handleSaveRemix}
                />
            )}

            <ThoughtSidebar
                isOpen={isSidebarOpen}
                onClose={() => setIsSidebarOpen(false)}
                currentPersona={settings?.persona || "grandma"}
                onPersonaChange={(p) => updateUserSettings({ persona: p })}
                riskTolerance={settings?.risk_tolerance || 0.5}
                onRiskChange={(r) => updateUserSettings({ risk_tolerance: r })}
            />

            {/* FOMO Activity Ticker */}
            <ActivityTicker />

            {/* Daily Founder Mindset Questionnaire */}
            <FounderMindset />
        </DashboardShell >
    );
}
