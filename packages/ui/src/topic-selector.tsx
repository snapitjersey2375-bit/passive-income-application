"use client";

import { motion } from "framer-motion";

export const TOPICS = [
    "General",
    "Coding",
    "Finance",
    "Biohacking",
    "AI Tools",
    "Fitness"
];

interface TopicSelectorProps {
    selectedTopic: string;
    onSelect: (topic: string) => void;
}

export function TopicSelector({ selectedTopic, onSelect }: TopicSelectorProps) {
    return (
        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide py-2">
            {TOPICS.map((topic) => {
                const isSelected = selectedTopic === topic;
                return (
                    <motion.button
                        key={topic}
                        onClick={() => onSelect(topic)}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className={`
              relative px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200 whitespace-nowrap
              ${isSelected
                                ? "text-white shadow-lg shadow-blue-500/25"
                                : "text-slate-600 hover:bg-white/50 bg-white/30 border border-white/40"
                            }
            `}
                    >
                        {isSelected && (
                            <motion.div
                                layoutId="activeTopic"
                                className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full"
                                initial={false}
                                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                            />
                        )}
                        <span className="relative z-10">{topic}</span>
                    </motion.button>
                );
            })}
        </div>
    );
}
