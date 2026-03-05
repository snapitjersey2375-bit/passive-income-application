"use client";

import React, { useState, useEffect } from "react";
import { X, Target, Clock, Compass, Sparkles } from "lucide-react";

interface FounderMindsetProps {
    onComplete?: (answers: FounderGoals) => void;
}

export interface FounderGoals {
    incomeGoal: string;
    timeCommitment: string;
    targetNiche: string;
    timestamp: number;
}

const STORAGE_KEY = "antigravity_founder_mindset";

function isSameDay(timestamp: number): boolean {
    const today = new Date();
    const stored = new Date(timestamp);
    return (
        today.getFullYear() === stored.getFullYear() &&
        today.getMonth() === stored.getMonth() &&
        today.getDate() === stored.getDate()
    );
}

export function FounderMindset({ onComplete }: FounderMindsetProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [step, setStep] = useState(0);
    const [answers, setAnswers] = useState<Partial<FounderGoals>>({});

    useEffect(() => {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                const parsed: FounderGoals = JSON.parse(stored);
                if (isSameDay(parsed.timestamp)) {
                    // Already answered today
                    return;
                }
            }
            // Show modal after a short delay for better UX
            const timer = setTimeout(() => setIsOpen(true), 500);
            return () => clearTimeout(timer);
        } catch {
            setIsOpen(true);
        }
    }, []);

    const questions = [
        {
            key: "incomeGoal",
            icon: <Target className="w-8 h-8 text-emerald-500" />,
            title: "What's your passive income goal?",
            subtitle: "Dream big. This is your North Star.",
            placeholder: "$5,000 / month",
            options: ["$1,000/mo", "$5,000/mo", "$10,000/mo", "$50,000/mo"],
        },
        {
            key: "timeCommitment",
            icon: <Clock className="w-8 h-8 text-blue-500" />,
            title: "How much time can you invest today?",
            subtitle: "Even 10 minutes moves the needle.",
            placeholder: "10 minutes",
            options: ["5 mins", "10 mins", "30 mins", "1 hour"],
        },
        {
            key: "targetNiche",
            icon: <Compass className="w-8 h-8 text-purple-500" />,
            title: "What niche are you conquering?",
            subtitle: "Focus on one. Dominate it.",
            placeholder: "Tech Reviews",
            options: ["Tech", "Finance", "Lifestyle", "Gaming"],
        },
    ];

    const handleOptionSelect = (value: string) => {
        const currentQuestion = questions[step];
        setAnswers((prev) => ({ ...prev, [currentQuestion.key]: value }));

        if (step < questions.length - 1) {
            setStep((s) => s + 1);
        } else {
            // Complete
            const finalAnswers: FounderGoals = {
                incomeGoal: answers.incomeGoal || value,
                timeCommitment: answers.timeCommitment || value,
                targetNiche: answers.targetNiche || value,
                timestamp: Date.now(),
            };
            // Handle the last answer correctly
            finalAnswers[currentQuestion.key as keyof Omit<FounderGoals, 'timestamp'>] = value;

            localStorage.setItem(STORAGE_KEY, JSON.stringify(finalAnswers));
            onComplete?.(finalAnswers);
            setIsOpen(false);
        }
    };

    if (!isOpen) return null;

    const currentQuestion = questions[step];

    return (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-in fade-in duration-300">
            <div className="bg-white rounded-3xl p-8 max-w-md w-full shadow-2xl border border-gray-100 animate-in zoom-in-95 duration-300">
                {/* Progress */}
                <div className="flex gap-2 mb-8">
                    {questions.map((_, i) => (
                        <div
                            key={i}
                            className={`h-1.5 flex-1 rounded-full transition-all duration-500 ${i <= step ? "bg-blue-600" : "bg-gray-200"
                                }`}
                        />
                    ))}
                </div>

                {/* Icon */}
                <div className="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mx-auto mb-6 ring-4 ring-gray-100">
                    {currentQuestion.icon}
                </div>

                {/* Question */}
                <h2 className="text-2xl font-black text-gray-900 text-center mb-2">
                    {currentQuestion.title}
                </h2>
                <p className="text-gray-500 text-center mb-8">
                    {currentQuestion.subtitle}
                </p>

                {/* Options */}
                <div className="grid grid-cols-2 gap-3">
                    {currentQuestion.options.map((option) => (
                        <button
                            key={option}
                            onClick={() => handleOptionSelect(option)}
                            className="py-4 px-4 bg-gray-50 hover:bg-blue-50 border-2 border-gray-100 hover:border-blue-500 rounded-xl font-bold text-gray-700 hover:text-blue-600 transition-all duration-200 active:scale-95"
                        >
                            {option}
                        </button>
                    ))}
                </div>

                {/* Skip */}
                <button
                    onClick={() => setIsOpen(false)}
                    className="mt-6 w-full text-gray-400 text-sm font-medium hover:text-gray-600 transition-colors"
                >
                    Skip for now
                </button>

                {/* Branding */}
                <div className="mt-8 pt-6 border-t border-gray-100 flex items-center justify-center gap-2 text-gray-400 text-xs">
                    <Sparkles size={12} />
                    <span>Founder Mindset™ by Antigravity</span>
                </div>
            </div>
        </div>
    );
}
