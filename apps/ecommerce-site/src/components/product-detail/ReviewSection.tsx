import ReviewCard from './ReviewCard'
import StarRating from '@/components/shared/StarRating'
import { getReviewsForProduct } from '@/data/mock-reviews'
import { Button } from '@/components/ui/button'

interface ReviewSectionProps {
  productId: string
  rating?: number
  reviewCount?: number
}

export default function ReviewSection({ productId, rating = 0, reviewCount = 0 }: ReviewSectionProps) {
  const reviews = getReviewsForProduct(productId)

  return (
    <div id="reviews" className="bg-[#111827] border border-[#374151] rounded-xl p-6">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-lg font-bold text-white mb-2">Customer Reviews</h2>
          <div className="flex items-center gap-3">
            <span className="text-4xl font-bold text-white">{rating.toFixed(1)}</span>
            <div>
              <StarRating rating={rating} size="md" />
              <p className="text-sm text-gray-400 mt-1">{reviewCount} reviews</p>
            </div>
          </div>
        </div>
        <Button className="bg-[#3b82f6] hover:bg-[#2563eb] text-white">Write a Review</Button>
      </div>

      {reviews.length > 0 ? (
        <div className="space-y-4">
          {reviews.map(review => (
            <ReviewCard key={review.id} review={review} />
          ))}
        </div>
      ) : (
        <p className="text-gray-500 text-sm text-center py-8">No reviews yet. Be the first to review this product!</p>
      )}
    </div>
  )
}
