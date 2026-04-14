import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(_request: NextRequest) {
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/meal-plans/:path*",
    "/food-log/:path*",
    "/photo-estimator/:path*",
    "/progress/:path*",
    "/assistant/:path*",
    "/settings/:path*",
    "/personal-details/:path*",
    "/goals/:path*",
    "/plan/:path*"
  ],
};
