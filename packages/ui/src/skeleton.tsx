"use client";

import React from "react";
import { cn } from "./utils/cn";

interface SkeletonProps {
    className?: string;
    variant?: "text" | "circular" | "rectangular";
    width?: string | number;
    height?: string | number;
}

export function Skeleton({
    className,
    variant = "rectangular",
    width,
    height,
}: SkeletonProps) {
    const baseClasses = "animate-pulse bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 bg-[length:200%_100%]";

    const variantClasses = {
        text: "rounded h-4",
        circular: "rounded-full",
        rectangular: "rounded-xl",
    };

    return (
        <div
            className={cn(baseClasses, variantClasses[variant], className)}
            style={{
                width: width,
                height: height,
            }}
        />
    );
}

// Pre-built skeleton patterns
export function CardSkeleton() {
    return (
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 space-y-4">
            <Skeleton height={200} className="w-full" />
            <Skeleton variant="text" className="w-3/4" />
            <Skeleton variant="text" className="w-1/2" />
            <div className="flex gap-2 pt-2">
                <Skeleton className="w-20 h-8" />
                <Skeleton className="w-20 h-8" />
            </div>
        </div>
    );
}

export function StatsSkeleton() {
    return (
        <div className="grid grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
                <div key={i} className="bg-white p-6 rounded-2xl border border-gray-100">
                    <Skeleton variant="text" className="w-1/3 mb-2" height={12} />
                    <Skeleton variant="text" className="w-2/3" height={28} />
                </div>
            ))}
        </div>
    );
}
