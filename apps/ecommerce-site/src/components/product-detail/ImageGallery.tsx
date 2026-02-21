'use client'
import { useState } from 'react'
import Image from 'next/image'
import { cn } from '@/lib/utils'
import { ZoomIn } from 'lucide-react'

interface ImageGalleryProps {
  images: string[]
  productName: string
}

export default function ImageGallery({ images, productName }: ImageGalleryProps) {
  const [selected, setSelected] = useState(0)

  return (
    <div className="space-y-3">
      {/* Main image */}
      <div className="relative aspect-square rounded-xl overflow-hidden bg-[#1f2937] border border-[#374151] group">
        <Image
          src={images[selected]}
          alt={`${productName} - image ${selected + 1}`}
          fill
          className="object-cover transition-transform duration-500 group-hover:scale-105"
          sizes="(max-width: 768px) 100vw, 50vw"
          priority
        />
        <div className="absolute top-3 right-3 p-1.5 rounded-lg bg-black/40 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">
          <ZoomIn className="h-4 w-4" />
        </div>
      </div>

      {/* Thumbnails */}
      {images.length > 1 && (
        <div className="grid grid-cols-4 gap-2">
          {images.map((img, i) => (
            <button
              key={i}
              onClick={() => setSelected(i)}
              className={cn(
                'relative aspect-square rounded-lg overflow-hidden border-2 transition-all',
                selected === i
                  ? 'border-[#3b82f6] shadow-glow-blue'
                  : 'border-[#374151] hover:border-[#3b82f6]/50'
              )}
            >
              <Image
                src={img}
                alt={`${productName} thumbnail ${i + 1}`}
                fill
                className="object-cover"
                sizes="80px"
              />
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
