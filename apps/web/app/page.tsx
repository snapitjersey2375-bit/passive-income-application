"use client";

import Image from "next/image";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, CheckCircle2, Zap, BarChart3, Users } from "lucide-react";
import { StatsTicker } from "../components/landing/stats-ticker";
import { WaitlistForm } from "../components/landing/waitlist-form";
import { ReferralLeaderboard } from "../components/landing/referral-leaderboard";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center bg-black text-white selection:bg-purple-500/30">

      {/* Navigation */}
      <nav className="w-full max-w-7xl mx-auto px-6 py-6 flex items-center justify-between z-50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <Zap className="w-4 h-4 text-white fill-current" />
          </div>
          <span className="font-bold text-xl tracking-tight">Antigravity</span>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/login" className="text-sm text-zinc-400 hover:text-white transition-colors">
            Login
          </Link>
          <Link
            href="/login"
            className="px-4 py-2 rounded-full bg-white text-black text-sm font-medium hover:bg-zinc-200 transition-colors"
          >
            Get Started
          </Link>
        </div>
      </nav>

      <main className="w-full flex-1 flex flex-col items-center relative overflow-hidden">

        {/* Hero Section */}
        <div className="w-full max-w-5xl mx-auto px-6 pt-20 pb-16 text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 mb-8 backdrop-blur-sm">
              <span className="flex h-2 w-2 rounded-full bg-green-500" />
              <span className="text-sm text-zinc-300">Waitlist is now open</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white via-white/90 to-white/50">
              AI That Prints Money <br /> While You Sleep
            </h1>

            <p className="text-xl text-zinc-400 max-w-2xl mx-auto mb-10 leading-relaxed">
              Let our autonomous agents create, curate, and monetize viral content for you.
              The first passive income engine powered by Agentic AI.
            </p>

            <div className="mb-16">
              <WaitlistForm />
            </div>
          </motion.div>
        </div>

        {/* Live Ticker */}
        <div className="w-full bg-black/50 border-y border-white/5 backdrop-blur-sm">
          <StatsTicker />
        </div>

        {/* Features / How It Works */}
        <div className="w-full max-w-6xl mx-auto px-6 py-24">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">

            <div className="space-y-8">
              <h2 className="text-3xl md:text-4xl font-bold">The infinite money glitch, patched into reality.</h2>
              <p className="text-lg text-zinc-400">Stop trading time for money. Antigravity builds a self-sustaining content empire that works 24/7/365.</p>

              <div className="space-y-4">
                <FeatureItem
                  icon={<Zap className="w-5 h-5 text-yellow-400" />}
                  title="Content Swarms"
                  description="Agents generate thousands of viral ideas instantly."
                />
                <FeatureItem
                  icon={<BarChart3 className="w-5 h-5 text-blue-400" />}
                  title="Auto-Optimization"
                  description="Traffic agents analyze performance and adjust strategy in real-time."
                />
                <FeatureItem
                  icon={<Users className="w-5 h-5 text-purple-400" />}
                  title="Community Multiplier"
                  description="Earn commission from every user you refer to the ecosystem."
                />
              </div>
            </div>

            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 blur-3xl rounded-full" />
              <div className="relative z-10">
                <ReferralLeaderboard />
              </div>
            </div>

          </div>
        </div>

      </main>

      <footer className="w-full border-t border-white/10 bg-black/50 backdrop-blur-sm py-8 text-center text-zinc-500 text-sm">
        <p>© 2026 Antigravity Inc. All rights reserved.</p>
      </footer>
    </div>
  );
}

function FeatureItem({ icon, title, description }: { icon: any, title: string, description: string }) {
  return (
    <div className="flex gap-4 p-4 rounded-xl hover:bg-white/5 transition-colors border border-transparent hover:border-white/5">
      <div className="mt-1">{icon}</div>
      <div>
        <h3 className="font-semibold text-white mb-1">{title}</h3>
        <p className="text-sm text-zinc-400">{description}</p>
      </div>
    </div>
  );
}
