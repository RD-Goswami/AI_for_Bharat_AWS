import { NextResponse } from 'next/server';
import { generateMarketingCopy, generatePoster } from '@/lib/bedrock';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { business, topic } = body;

    // validation
    if (!business || !topic) {
      return NextResponse.json(
        { error: 'Business and Topic are required' },
        { status: 400 }
      );
    }

    // 1. Generate Text (Gemini or Backup)
    const strategy = await generateMarketingCopy(topic, business);

    // 2. Generate Image (Flux)
    const imageUrl = await generatePoster(topic, business);

    // 3. Combine and Return
    return NextResponse.json({
      ...strategy, // spreads hook, offer, cta
      imageUrl // adds the image url
    });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Failed to generate campaign' },
      { status: 500 }
    );
  }
}
