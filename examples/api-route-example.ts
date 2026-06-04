// 금강 SAC API 호출 예시 — Vercel API Routes 패턴
import { NextResponse } from 'next/server';

export async function GET(
  req: Request,
  { params }: { params: { id: string } }
) {
  const apiUrl = process.env.KUMKANG_API_URL;
  const apiKey = process.env.KUMKANG_API_KEY;

  // 금강 ERP API 호출 (서버 측에서만)
  const erpRes = await fetch(`${apiUrl}/erp/projects/${params.id}`, {
    headers: { 'Authorization': `Bearer ${apiKey}` },
  });

  if (!erpRes.ok) {
    return NextResponse.json({ error: 'ERP 조회 실패' }, { status: erpRes.status });
  }

  const erpData = await erpRes.json();
  return NextResponse.json({ data: erpData });
}
