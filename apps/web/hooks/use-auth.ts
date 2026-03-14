"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface User {
    id: string;
    email: string;
    risk_tolerance: number;
    is_grandma_mode: boolean;
}

export function useAuth() {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const storedUser = localStorage.getItem("nexus_user");
        const token = localStorage.getItem("nexus_token");
        if (storedUser && token) {
            try {
                setUser(JSON.parse(storedUser));
            } catch {
                // Corrupted storage — clear it
                localStorage.removeItem("nexus_user");
                localStorage.removeItem("nexus_token");
            }
        }
        setIsLoading(false);
    }, []);

    const login = (userData: User, token: string) => {
        localStorage.setItem("nexus_user", JSON.stringify(userData));
        localStorage.setItem("nexus_token", token);
        setUser(userData);
        router.push("/dashboard");
    };

    const logout = () => {
        localStorage.removeItem("nexus_user");
        localStorage.removeItem("nexus_token");
        setUser(null);
        router.push("/login");
    };

    const requireAuth = () => {
        if (!isLoading && !user) {
            router.push("/login");
        }
    };

    return { user, isLoading, login, logout, requireAuth };
}
