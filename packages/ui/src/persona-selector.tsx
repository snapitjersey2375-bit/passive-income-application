"use client";

import React from "react";
import { Coffee, Rocket, Briefcase, Check } from "lucide-react";
import { cn } from "./utils/cn";

interface Persona {
    id: string;
    name: string;
    description: string;
    icon: React.ElementType;
    color: string;
}

const personas: Persona[] = [
    {
        id: "grandma",
        name: "Grandma",
        description: "Sweet, nurturing, and slightly confused.",
        icon: Coffee,
        color: "text-pink-500 bg-pink-50 border-pink-100"
    },
    {
        id: "degen",
        name: "Degen",
        description: "High energy, crypto-native, Moon-bound.",
        icon: Rocket,
        color: "text-blue-500 bg-blue-50 border-blue-100"
    },
    {
        id: "corporate",
        name: "Corporate",
        description: "Professional, efficiency-obsessed executive.",
        icon: Briefcase,
        color: "text-slate-700 bg-slate-50 border-slate-200"
    }
];

interface PersonaSelectorProps {
    currentPersona: string;
    onPersonaChange: (personaId: string) => void;
}

export function PersonaSelector({ currentPersona, onPersonaChange }: PersonaSelectorProps) {
    return (
        <div className="space-y-4">
            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest px-1">Agent Persona</h4>
            <div className="grid grid-cols-1 gap-3">
                {personas.map((persona) => {
                    const Icon = persona.icon;
                    const isActive = currentPersona === persona.id;

                    return (
                        <button
                            key={persona.id}
                            onClick={() => onPersonaChange(persona.id)}
                            className={cn(
                                "flex items-center gap-4 p-4 rounded-2xl border transition-all text-left group",
                                isActive
                                    ? cn("border-blue-500 bg-blue-50/50 shadow-md transform scale-[1.02]", persona.color)
                                    : "border-gray-100 bg-white hover:border-gray-200 hover:shadow-sm"
                            )}
                        >
                            <div className={cn(
                                "p-3 rounded-xl transition-colors",
                                isActive ? "bg-white shadow-sm" : "bg-gray-50 group-hover:bg-gray-100"
                            )}>
                                <Icon size={20} className={isActive ? persona.color.split(' ')[0] : "text-gray-400"} />
                            </div>

                            <div className="flex-1">
                                <div className="flex items-center justify-between">
                                    <span className={cn(
                                        "font-bold text-sm",
                                        isActive ? "text-gray-900" : "text-gray-600"
                                    )}>
                                        {persona.name}
                                    </span>
                                    {isActive && (
                                        <div className="bg-blue-500 text-white rounded-full p-0.5 animate-in zoom-in duration-300">
                                            <Check size={10} strokeWidth={4} />
                                        </div>
                                    )}
                                </div>
                                <p className="text-[10px] text-gray-400 font-medium leading-tight mt-0.5">
                                    {persona.description}
                                </p>
                            </div>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
