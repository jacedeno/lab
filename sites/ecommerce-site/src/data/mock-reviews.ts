export interface MockReview {
  id: string
  productId: string
  userId: string
  userName: string
  userAvatar: string
  rating: number
  title: string
  body: string
  isVerified: boolean
  createdAt: string
}

export const mockReviews: MockReview[] = [
  {
    id: 'rev-1',
    productId: 'prod-1',
    userId: 'user-1',
    userName: 'Alex Thompson',
    userAvatar: 'https://placehold.co/40x40/1f2937/22d3ee?text=AT',
    rating: 5,
    title: 'Absolute beast of a machine',
    body: 'Built this for 3D rendering and gaming. The i9 + RTX 4080 combo handles everything I throw at it. Blender renders in record time. Highly recommend for any creative professional.',
    isVerified: true,
    createdAt: '2026-01-15T10:30:00Z',
  },
  {
    id: 'rev-2',
    productId: 'prod-1',
    userId: 'user-2',
    userName: 'Sarah Chen',
    userAvatar: 'https://placehold.co/40x40/1f2937/3b82f6?text=SC',
    rating: 5,
    title: 'Outstanding performance and quality',
    body: 'GeekendZone built this to my specifications. The cable management is immaculate, thermal performance is excellent, and customer support was incredible throughout the process.',
    isVerified: true,
    createdAt: '2026-01-22T14:15:00Z',
  },
  {
    id: 'rev-3',
    productId: 'prod-1',
    userId: 'user-3',
    userName: 'Marcus Davis',
    userAvatar: 'https://placehold.co/40x40/1f2937/8b5cf6?text=MD',
    rating: 4,
    title: 'Great PC, minor shipping delay',
    body: 'The PC itself is phenomenal - gaming at 4K ultra settings is buttery smooth. Only knocked one star because it arrived 2 days late. Performance is 10/10 though.',
    isVerified: true,
    createdAt: '2026-02-01T09:00:00Z',
  },
  {
    id: 'rev-4',
    productId: 'prod-5',
    userId: 'user-4',
    userName: 'Jennifer Wu',
    userAvatar: 'https://placehold.co/40x40/1f2937/22d3ee?text=JW',
    rating: 5,
    title: 'Best gaming laptop money can buy',
    body: 'The OLED display is absolutely stunning. Games look incredible and the performance is console-crushing. Battery life is surprisingly decent for a gaming laptop. Worth every penny.',
    isVerified: true,
    createdAt: '2026-01-10T16:45:00Z',
  },
  {
    id: 'rev-5',
    productId: 'prod-17',
    userId: 'user-5',
    userName: 'Robert Miller',
    userAvatar: 'https://placehold.co/40x40/1f2937/3b82f6?text=RM',
    rating: 5,
    title: 'The king of GPUs',
    body: '4K gaming at 144fps+ in every game I play. DLSS 3.5 Frame Generation is a game changer. Yes it is expensive, but the performance is unmatched. No regrets.',
    isVerified: true,
    createdAt: '2025-12-28T11:20:00Z',
  },
  {
    id: 'rev-6',
    productId: 'prod-14',
    userId: 'user-6',
    userName: 'Lisa Park',
    userAvatar: 'https://placehold.co/40x40/1f2937/8b5cf6?text=LP',
    rating: 5,
    title: 'Lightest gaming mouse I have ever used',
    body: 'At 60g you barely feel it. The HERO 2 sensor tracks perfectly. Battery lasts weeks. This is the mouse pro players use for a reason. Completely transformed my FPS gaming.',
    isVerified: true,
    createdAt: '2026-01-30T08:30:00Z',
  },
]

export const getReviewsForProduct = (productId: string) =>
  mockReviews.filter((r) => r.productId === productId)
