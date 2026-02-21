import Link from 'next/link'
import Image from 'next/image'
import { ArrowRight } from 'lucide-react'
import { Category } from '@/types/category'

interface CategoryCardProps {
  category: Category
}

export default function CategoryCard({ category }: CategoryCardProps) {
  return (
    <Link
      href={`/products/${category.slug}`}
      className="group relative overflow-hidden rounded-xl bg-[#111827] border border-[#374151] hover:border-[#3b82f6]/50 transition-all duration-300 hover:shadow-card-hover block"
    >
      {/* Image */}
      <div className="aspect-video relative overflow-hidden bg-[#1f2937]">
        <Image
          src={category.imageUrl}
          alt={category.name}
          fill
          className="object-cover opacity-60 group-hover:opacity-80 group-hover:scale-105 transition-all duration-500"
          sizes="(max-width: 768px) 50vw, 25vw"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#030712] via-[#030712]/40 to-transparent" />
      </div>

      {/* Content */}
      <div className="absolute bottom-0 inset-x-0 p-4">
        <div className="flex items-end justify-between">
          <div>
            <h3 className="font-bold text-white group-hover:text-[#22d3ee] transition-colors">{category.name}</h3>
            {category.productCount && (
              <p className="text-xs text-gray-400 mt-0.5">{category.productCount} products</p>
            )}
          </div>
          <div className="w-7 h-7 rounded-full bg-[#3b82f6]/20 flex items-center justify-center group-hover:bg-[#3b82f6] transition-colors">
            <ArrowRight className="h-3.5 w-3.5 text-[#3b82f6] group-hover:text-white transition-colors" />
          </div>
        </div>
      </div>
    </Link>
  )
}
