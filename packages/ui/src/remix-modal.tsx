"use client";
import React, { useState } from 'react';
import { X, Sparkles, Save } from 'lucide-react';
import { cn } from './utils/cn';

interface ContentItem {
    id: string;
    title: string;
    description?: string;
}

interface RemixModalProps {
    item: ContentItem;
    isOpen: boolean;
    onClose: () => void;
    onSave: (id: string, newTitle: string, newDesc: string) => Promise<void>;
}

export function RemixModal({ item, isOpen, onClose, onSave }: RemixModalProps) {
    const [title, setTitle] = useState(item.title);
    const [description, setDescription] = useState(item.description || '');
    const [isSaving, setIsSaving] = useState(false);
    const [isRemixing, setIsRemixing] = useState(false);

    if (!isOpen) return null;

    const handleRemix = async () => {
        setIsRemixing(true);
        try {
            // Mock LLM remix
            await new Promise(r => setTimeout(r, 800));
            setTitle(`🔥 REACTING TO ${item.title} (GONE WRONG)`);
            setDescription(`You won&apos;t believe what happened when we tried to ${item.description?.toLowerCase()}... Click the link in bio to see the full story! #viral #trending`);
        } finally {
            setIsRemixing(false);
        }
    };

    const handleSave = async () => {
        setIsSaving(true);
        try {
            await onSave(item.id, title, description);
            onClose();
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="bg-white rounded-3xl w-full max-w-lg shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
                <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                    <h2 className="font-bold text-gray-900 flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-purple-500" />
                        Remix Content
                    </h2>
                    <button onClick={onClose} className="p-1 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="p-6 space-y-4">
                    <div className="space-y-1">
                        <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Hook / Title</label>
                        <textarea
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            className="w-full bg-gray-50 border border-gray-200 rounded-xl p-3 text-sm font-semibold text-gray-900 focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all resize-none min-h-[80px]"
                            placeholder="Write a viral hook..."
                        />
                    </div>

                    <div className="space-y-1">
                        <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Caption / Description</label>
                        <textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            className="w-full bg-gray-50 border border-gray-200 rounded-xl p-3 text-sm text-gray-700 focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all resize-none min-h-[120px]"
                            placeholder="Add your caption and hashtags..."
                        />
                    </div>
                </div>

                <div className="p-4 bg-gray-50 border-t border-gray-100 flex gap-3">
                    <button
                        onClick={handleRemix}
                        disabled={isRemixing || isSaving}
                        className="flex-1 px-4 py-2.5 bg-purple-100 text-purple-700 font-semibold rounded-xl hover:bg-purple-200 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                    >
                        {isRemixing ? (
                            <div className="w-4 h-4 border-2 border-purple-500/30 border-t-purple-500 rounded-full animate-spin" />
                        ) : (
                            <Sparkles className="w-4 h-4" />
                        )}
                        AI Auto-Remix
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={isSaving || isRemixing}
                        className="flex-1 px-4 py-2.5 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-colors shadow-lg shadow-blue-500/30 flex items-center justify-center gap-2 disabled:opacity-50"
                    >
                        {isSaving ? (
                            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        ) : (
                            <Save className="w-4 h-4" />
                        )}
                        Save Changes
                    </button>
                </div>
            </div>
        </div>
    );
}
