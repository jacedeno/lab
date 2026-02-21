import { MockReview } from '@/data/mock-reviews'
import StarRating from '@/components/shared/StarRating'
import { formatDate } from '@/lib/formatters'
import { Badge } from '@/components/ui/badge'
import Image from 'next/image'

interface ReviewCardProps {
  review: MockReview
}

export default function ReviewCard({ review }: ReviewCardProps) {
  return (
    <div className="bg-[#111827] border border-[#374151] rounded-xl p-5">
      <div className="flex items-start justify-between gap-4 mb-3">
        <div className="flex items-center gap-3">
          <div className="relative w-9 h-9 rounded-full overflow-hidden bg-[#1f2937] shrink-0">
            <Image src={review.userAvatar} alt={review.userName} fill className="object-cover" sizes="36px" />
          </div>
          <div>
            <p className="text-sm font-semibold text-white">{review.userName}</p>
            <p className="text-xs text-gray-500">{formatDate(review.createdAt)}</p>
          </div>
        </div>
        <div className="flex flex-col items-end gap-1">
          <StarRating rating={review.rating} size="sm" />
          {review.isVerified && (
            <Badge className="text-[10px] bg-green-500/10 text-green-400 border-green-500/20">Verified Purchase</Badge>
          )}
        </div>
      </div>
      <h4 className="font-semibold text-white mb-1">{review.title}</h4>
      <p className="text-sm text-gray-400 leading-relaxed">{review.body}</p>
    </div>
  )
}
