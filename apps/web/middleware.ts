import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PROTECTED_PREFIXES = ["/dashboard"];
const AUTH_COOKIE = "nexus_token";

export function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl;

    // Redirect root to login
    if (pathname === "/") {
        return NextResponse.redirect(new URL("/login", request.url));
    }

    // Protect dashboard routes — redirect to /login if no auth cookie present
    const isProtected = PROTECTED_PREFIXES.some((prefix) => pathname.startsWith(prefix));
    if (isProtected) {
        const token = request.cookies.get(AUTH_COOKIE)?.value;
        if (!token) {
            const loginUrl = new URL("/login", request.url);
            loginUrl.searchParams.set("next", pathname);
            return NextResponse.redirect(loginUrl);
        }
    }

    return NextResponse.next();
}

export const config = {
    matcher: ["/", "/dashboard/:path*"],
};
