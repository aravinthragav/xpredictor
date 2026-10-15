import { NextRequest, NextResponse } from "next/server";
import { generateOGCardSvg } from "@/growth/og-generator";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const symbol = searchParams.get("symbol") || "XAUUSD";
  const timeframe = searchParams.get("tf") || "1h";
  const bullishSkew = parseFloat(searchParams.get("skew") || "86.4");

  const svg = generateOGCardSvg({
    symbol,
    timeframe,
    bullishSkew,
    matchDate: "Oct 18, 2024",
    matchPct: 96.2,
    winRate: 73.0,
    optimalRR: 3.54,
  });

  return new NextResponse(svg, {
    status: 200,
    headers: {
      "Content-Type": "image/svg+xml",
      "Cache-Control": "public, max-age=86400, stale-while-revalidate=43200",
    },
  });
}
