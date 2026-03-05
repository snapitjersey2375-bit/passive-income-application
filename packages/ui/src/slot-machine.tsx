"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "./utils/cn";

interface SlotMachineProps {
    value: string;
    trigger?: boolean;
    className?: string;
}

export function SlotMachine({ value, trigger, className }: SlotMachineProps) {
    // Simple slot effect: animating numbers/text in
    const variants = {
        initial: { y: -20, opacity: 0 },
        animate: { y: 0, opacity: 1 },
        exit: { y: 20, opacity: 0 },
    };

    return (
        <div className={cn("overflow-hidden h-8 inline-block align-middle", className)}>
            <AnimatePresence mode="popLayout">
                <motion.span
                    key={value}
                    variants={variants}
                    initial="initial"
                    animate="animate"
                    exit="exit"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    className="block font-mono font-bold text-green-600"
                >
                    {value}
                </motion.span>
            </AnimatePresence>
        </div>
    );
}
