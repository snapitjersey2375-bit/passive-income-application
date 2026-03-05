"use client";

import { motion, useMotionValue, useTransform } from "framer-motion";
import React, { useState } from "react";
import { cn } from "./utils/cn";

interface SwipeCardProps {
    children: React.ReactNode;
    onSwipeRight?: () => void;
    onSwipeLeft?: () => void;
    className?: string;
    disabled?: boolean;
}

export function SwipeCard({
    children,
    onSwipeRight,
    onSwipeLeft,
    className,
    disabled = false,
}: SwipeCardProps) {
    const x = useMotionValue(0);
    const rotate = useTransform(x, [-200, 200], [-30, 30]);
    const opacity = useTransform(x, [-200, -100, 0, 100, 200], [0, 1, 1, 1, 0]);

    const handleDragEnd = (_: any, info: { offset: { x: number }; velocity: { x: number } }) => {
        if (disabled) return;
        const threshold = 100;
        if (info.offset.x > threshold) {
            onSwipeRight?.();
        } else if (info.offset.x < -threshold) {
            onSwipeLeft?.();
        }
    };

    return (
        <motion.div
            className={cn(
                "absolute inset-0 glass rounded-3xl overflow-hidden cursor-grab active:cursor-grabbing",
                "shadow-[0_20px_50px_rgba(0,0,0,0.1)] border-white/60",
                className
            )}
            style={{ x, rotate, opacity }}
            drag={disabled ? false : "x"}
            dragConstraints={{ left: 0, right: 0 }}
            onDragEnd={handleDragEnd}
            whileHover={{ scale: 1.02, boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.15)" }}
            whileTap={{ scale: 0.98 }}
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ x: x.get() < 0 ? -200 : 200, opacity: 0, transition: { duration: 0.2 } }}
        >
            {children}
        </motion.div>
    );
}
