"use client";

import React, { useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { getApiUrl } from "@/lib/api-url";
import { motion } from "framer-motion";

export default function LoginPage() {
    const { login } = useAuth();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");

    const [isSignup, setIsSignup] = useState(false);

    const handleAuth = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError("");

        try {
            const API_URL = getApiUrl();
            const endpoint = isSignup ? "/auth/signup" : "/auth/login";

            let res;
            if (isSignup) {
                // Signup: JSON body — credentials never appear in URL or logs
                res = await fetch(`${API_URL}${endpoint}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    credentials: "include",
                    body: JSON.stringify({ email: email.trim(), password }),
                });
            } else {
                // Login: OAuth2 form (required by FastAPI OAuth2PasswordRequestForm)
                const formData = new FormData();
                formData.append("username", email.trim());
                formData.append("password", password);
                res = await fetch(`${API_URL}${endpoint}`, {
                    method: "POST",
                    credentials: "include",
                    body: formData,
                });
            }

            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || "Authentication failed");
            }

            const data = await res.json();
            // Backend now returns { access_token, user: { id, email, ... } }
            login(data.user, data.access_token);
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: unknown) {
            setError((err as Error).message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-[#050505] text-white selection:bg-blue-500/30">
            {/* Background Decorations */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/10 blur-[120px] rounded-full" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600/10 blur-[120px] rounded-full" />
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                className="relative z-10 w-full max-w-md p-8 bg-zinc-900/50 backdrop-blur-3xl border border-white/10 rounded-3xl shadow-2xl"
            >
                <div className="space-y-6">
                    <div className="text-center space-y-2">
                        <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-b from-white to-zinc-400 bg-clip-text text-transparent">
                            NexusFlow
                        </h1>
                        <p className="text-zinc-500 text-sm">
                            Phase 2: Supervisor Authentication
                        </p>
                    </div>

                    <form onSubmit={handleAuth} className="space-y-4">
                        <div className="space-y-1.5">
                            <label className="text-xs font-medium text-zinc-400 ml-1">Email Address</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="dipali@nexusflow.ai"
                                className="w-full px-4 py-3 bg-black/40 border border-white/5 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all placeholder:text-zinc-700"
                                required
                            />
                        </div>

                        <div className="space-y-1.5">
                            <label className="text-xs font-medium text-zinc-400 ml-1">Password</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="••••••••"
                                className="w-full px-4 py-3 bg-black/40 border border-white/5 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all placeholder:text-zinc-700"
                                required
                            />
                        </div>

                        {error && (
                            <motion.p
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="text-red-400 text-xs text-center font-medium"
                            >
                                {error}
                            </motion.p>
                        )}

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full py-3.5 bg-white text-black font-semibold rounded-xl hover:bg-zinc-200 active:scale-[0.98] transition-all disabled:opacity-50 disabled:scale-100"
                        >
                            {isLoading ? "Authenticating..." : isSignup ? "Create Account" : "Enter Workspace"}
                        </button>

                        <button
                            type="button"
                            onClick={() => setIsSignup(!isSignup)}
                            className="w-full text-zinc-500 text-xs hover:text-white transition-colors py-2"
                        >
                            {isSignup ? "Already have an account? Log in" : "Don't have an account? Sign up"}
                        </button>
                    </form>

                    <div className="pt-4 border-t border-white/5 text-center">
                        <p className="text-zinc-600 text-[10px] uppercase tracking-[0.2em]">
                            End-to-End Encrypted Dashboard
                        </p>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
