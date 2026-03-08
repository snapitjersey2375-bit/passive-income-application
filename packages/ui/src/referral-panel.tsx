"use client";

import React, { useState, useEffect } from "react";
import { Copy, Check, Users, DollarSign, Share2 } from "lucide-react";

interface ReferralStats {
    referral_code: string;
    referral_count: number;
    wallet_balance: number;
}

export function ReferralPanel() {
    const [stats, setStats] = useState<ReferralStats | null>(null);
    const [copied, setCopied] = useState(false);

    useEffect(() => {
        fetchReferralStats();
    }, []);

    const fetchReferralStats = async () => {
        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const res = await fetch(`${API_URL}/user/settings`);
            const data = await res.json();
            setStats({
                referral_code: data.referral_code,
                referral_count: 0, // Will be added to API response
                wallet_balance: data.wallet_balance,
            });
        } catch (error) {
            console.error("Failed to fetch referral stats:", error);
        }
    };

    const copyReferralCode = () => {
        if (stats?.referral_code) {
            navigator.clipboard.writeText(stats.referral_code);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    const shareReferralCode = async () => {
        if (!stats?.referral_code) return;
        const shareData = {
            title: "Join NexusFlow AI",
            text: `Use my referral code ${stats.referral_code} to join NexusFlow AI and get $10 in free AI Credits!`,
            url: window.location.origin
        };

        if (navigator.share) {
            try {
                await navigator.share(shareData);
            } catch (err) {
                console.log("Share failed", err);
                copyReferralCode();
            }
        } else {
            copyReferralCode();
        }
    };

    if (!stats) {
        return (
            <div className="bg-gradient-to-br from-purple-500/10 to-blue-500/10 rounded-xl p-6 border border-purple-500/20 mb-8">
                <div className="text-gray-500 font-medium animate-pulse">Loading referral stats...</div>
            </div>
        );
    }

    return (
        <div className="bg-gradient-to-br from-purple-500/5 to-blue-500/5 rounded-2xl p-8 border border-purple-500/20 shadow-sm mb-8">
            <div className="flex items-center gap-2 mb-6">
                <div className="p-2 bg-purple-500/10 rounded-lg">
                    <Users className="w-5 h-5 text-purple-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-800">Referral Program</h3>
            </div>

            {/* Referral Code */}
            <div className="mb-8">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 block">Your Unique Referral Code</label>
                <div className="flex items-center gap-3">
                    <div className="flex-1 bg-white rounded-xl px-5 py-4 font-mono text-xl font-bold text-purple-600 border border-purple-200 shadow-inner flex items-center justify-between">
                        {stats.referral_code}
                        <div className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
                    </div>
                    <div className="flex gap-2">
                        <button
                            onClick={shareReferralCode}
                            className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-xl font-bold transition-all shadow-lg shadow-blue-200 active:scale-95"
                            title="Share Code"
                        >
                            <Share2 className="w-5 h-5" />
                        </button>
                        <button
                            onClick={copyReferralCode}
                            className="flex-1 bg-purple-600 hover:bg-purple-700 text-white px-6 py-4 rounded-xl font-bold transition-all shadow-lg shadow-purple-200 hover:shadow-purple-300 active:scale-95 flex items-center gap-2"
                        >
                            {copied ? (
                                <>
                                    <Check className="w-5 h-5" />
                                    Copied!
                                </>
                            ) : (
                                <>
                                    <Copy className="w-5 h-5" />
                                    Copy
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-6">
                <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm transition-transform hover:scale-[1.02]">
                    <div className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-1">Total Referrals</div>
                    <div className="text-3xl font-black text-gray-900">{stats.referral_count || 0}</div>
                </div>
                <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm transition-transform hover:scale-[1.02]">
                    <div className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-1 flex items-center gap-1">
                        <DollarSign className="w-3 h-3" />
                        AI Credit Balance
                    </div>
                    <div className="text-3xl font-black text-green-600">
                        ${stats.wallet_balance ? stats.wallet_balance.toFixed(2) : "0.00"}
                    </div>
                </div>
            </div>

            {/* Info */}
            <div className="mt-8 text-sm text-purple-700/70 bg-purple-50 rounded-xl p-4 border border-purple-100 flex items-start gap-3">
                <span className="text-xl">💡</span>
                <p className="font-medium">
                    <span className="font-bold text-purple-700">Earn $10 in AI Credits</span> for each friend who joins using your code. Help us grow the NexusFlow ecosystem!
                </p>
            </div>
        </div>
    );
}
