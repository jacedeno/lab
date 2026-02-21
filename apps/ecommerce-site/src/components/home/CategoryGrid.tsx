import CategoryCard from './CategoryCard'
import SectionHeader from '@/components/shared/SectionHeader'
import { mockCategories } from '@/data/mock-categories'

export default function CategoryGrid() {
  return (
    <section className="py-12">
      <div className="container mx-auto px-4">
        <SectionHeader title="Shop by Category" subtitle="Find exactly what you need across our full hardware lineup" />
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {mockCategories.map(cat => (
            <CategoryCard key={cat.id} category={cat} />
          ))}
        </div>
      </div>
    </section>
  )
}
