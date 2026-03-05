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
        const checkAuth = () => {
            const storedUser = localStorage.getItem("nexus_user");
            const token = localStorage.getItem("nexus_token");

            if (storedUser && token) {
                try {
                    setUser(JSON.parse(storedUser));
                } catch (e) {
                    console.error("Failed to parse user", e);
                }
            }
            setIsLoading(false);
        };
        checkAuth();
    }, []);

    const login = (userData: User, token: string) => {
        console.log("useAuth.login called with:", { userData, token });
        localStorage.setItem("nexus_user", JSON.stringify(userData));
        localStorage.setItem("nexus_token", token);
        console.log("Stored in localStorage");
        setUser(userData);
        console.log("Calling router.push to /dashboard");
        router.push("/dashboard");
        console.log("router.push called");
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
