// SIMULATION MODE - Mock AI responses for testing without AWS credentials

export async function generateMarketingCopy(topic: string, businessType: string): Promise<string> {
  // Simulate AI processing time (2 seconds)
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Generate realistic Hinglish marketing response
  const response = `📢 Namaste ${businessType} Owner! 🚀

Here is your campaign for ${topic}:

✨ The Hook:
"Arrey wah! ${topic} is here! 😲 Don't miss out!"

🎁 The Offer:
"Flat 20% OFF only for today! 🛍️✨"

🔥 Call to Action:
"Jaldi aao! Visit us before stocks run out! 🏃‍♂️💨"

---

💡 Pro Tip: Share this on WhatsApp and Instagram for maximum reach in your local community!

#${topic.replace(/\s+/g, '')} #IndianBusiness #LocalShop #SpecialOffer`;

  return response;
}
