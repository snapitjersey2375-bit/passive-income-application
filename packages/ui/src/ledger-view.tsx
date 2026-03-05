"use client";

import React, { useEffect, useState } from 'react';
import { ArrowUpRight, ArrowDownLeft, DollarSign } from 'lucide-react';

interface LedgerEntry {
    id: number;
    transaction_type: string;
    amount: number;
    description: string;
    balance_snapshot: number;
    created_at: string;
}

export function LedgerView() {
    const [entries, setEntries] = useState<LedgerEntry[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        fetch('http://localhost:8000/analytics/ledger?limit=50')
            .then(res => res.json())
            .then(data => {
                setEntries(data.entries);
                setIsLoading(false);
            })
            .catch(err => console.error("Failed to load ledger:", err));
    }, []);

    if (isLoading) {
        return <div className="p-8 text-center text-zinc-500">Loading financial data...</div>;
    }

    return (
        <div className="w-full bg-[#09090b] border border-white/5 rounded-xl overflow-hidden shadow-sm">
            <div className="p-4 border-b border-white/5 bg-white/5 backdrop-blur-sm flex justify-between items-center">
                <h3 className="text-lg font-semibold text-zinc-100 flex items-center gap-2">
                    <DollarSign className="w-5 h-5 text-emerald-400" />
                    Financial Ledger
                </h3>
                <span className="text-xs text-zinc-500 uppercase tracking-widest font-medium">Real-time Double Entry</span>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                    <thead className="text-xs text-zinc-500 uppercase bg-black/20 font-medium">
                        <tr>
                            <th className="px-6 py-3">ID</th>
                            <th className="px-6 py-3">Type</th>
                            <th className="px-6 py-3">Description</th>
                            <th className="px-6 py-3 text-right">Amount</th>
                            <th className="px-6 py-3 text-right">Balance</th>
                            <th className="px-6 py-3 text-right">Time</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {entries.map((entry) => (
                            <tr key={entry.id} className="hover:bg-white/5 transition-colors group">
                                <td className="px-6 py-4 font-mono text-zinc-600">#{entry.id.toString().padStart(6, '0')}</td>
                                <td className="px-6 py-4">
                                    <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium border ${entry.amount > 0
                                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                                        : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                                        }`}>
                                        {entry.amount > 0 ? <ArrowUpRight className="w-3 h-3 mr-1" /> : <ArrowDownLeft className="w-3 h-3 mr-1" />}
                                        {entry.transaction_type.replace('_', ' ')}
                                    </span>
                                </td>
                                <td className="px-6 py-4 font-medium text-zinc-300">{entry.description}</td>
                                <td className={`px-6 py-4 text-right font-mono font-medium ${entry.amount > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                    {entry.amount > 0 ? '+' : ''}{entry.amount.toFixed(2)}
                                </td>
                                <td className="px-6 py-4 text-right font-mono text-zinc-400">
                                    ${entry.balance_snapshot.toFixed(2)}
                                </td>
                                <td className="px-6 py-4 text-right text-zinc-500 text-xs">
                                    {new Date(entry.created_at).toLocaleTimeString()}
                                </td>
                            </tr>
                        ))}
                        {entries.length === 0 && (
                            <tr>
                                <td colSpan={6} className="px-6 py-12 text-center text-zinc-500">
                                    No transactions recorded yet. Start approving content to build history.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
