# GeekendZone Ecommerce — UI-Only Implementation Plan

## Context
Build the complete UI for an ecommerce site selling computer hardware (PCs, Laptops, Monitors, Keyboards, Mice, Ethernet Cards, GPU Cards, Servers) and IT consulting services. Reference design is a clean ecommerce layout like the Stella fashion site (sidebar filters, product grid, trust bar, hero banner). Starting from an empty directory.

**Brand**: GeekendZone | **Theme**: Dark/Midnight (blue/cyan accents) | **Language**: English only
**Stack**: Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui, Prisma (schema only — no backend logic)

---

## Project Structure

```
ecommerce-site/
├── public/images/{hero,categories,products,logo}/
├── prisma/schema.prisma
└── src/
    ├── app/
    │   ├── globals.css
    │   ├── layout.tsx                         # Root layout
    │   ├── page.tsx                           # Home /
    │   ├── (shop)/
    │   │   ├── layout.tsx
    │   │   ├── products/
    │   │   │   ├── page.tsx                   # All products
    │   │   │   └── [category]/
    │   │   │       ├── page.tsx               # Category listing
    │   │   │       └── [slug]/page.tsx        # Product detail
    │   │   ├── services/page.tsx
    │   │   ├── search/page.tsx
    │   │   ├── cart/page.tsx
    │   │   └── checkout/page.tsx
    │   └── (auth)/
    │       ├── layout.tsx                     # Minimal centered layout
    │       └── account/
    │           ├── page.tsx                   # Login / Register tabs
    │           ├── profile/page.tsx
    │           └── orders/page.tsx
    ├── components/
    │   ├── ui/                                # shadcn/ui auto-generated
    │   ├── layout/      Navbar, NavbarMobile, Footer, TrustBar
    │   ├── home/        HeroBanner, CategoryGrid, CategoryCard, FeaturedProducts,
    │   │                ServicesSection, ServiceCard, Newsletter
    │   ├── products/    ProductGrid, ProductCard, ProductListItem, FilterSidebar,
    │   │                FilterBrandSearch, FilterPriceRange, FilterSpecs,
    │   │                SortControls, ViewToggle, ActiveFilters, MobileFilterDrawer
    │   ├── product-detail/ ImageGallery, ProductInfo, SpecsTable, AddToCartButton,
    │   │                   QuantitySelector, ReviewSection, ReviewCard, RelatedProducts
    │   ├── cart/        CartItem, CartSummary, EmptyCart
    │   ├── checkout/    CheckoutStepper, ShippingForm, PaymentForm, OrderReview
    │   ├── account/     LoginForm, RegisterForm, ProfileCard, OrderHistoryItem
    │   └── shared/      Badge, PriceDisplay, StarRating, SearchBar, WishlistButton,
    │                    Breadcrumb, SectionHeader, LoadingSkeleton, EmptyState
    ├── lib/             utils.ts, formatters.ts, constants.ts, validators.ts
    ├── hooks/           useCart.ts, useWishlist.ts, useFilters.ts, useSearch.ts, useLocalStorage.ts
    ├── types/           product.ts, category.ts, cart.ts, user.ts, order.ts, service.ts, filters.ts
    ├── data/            mock-products.ts, mock-categories.ts, mock-services.ts, mock-reviews.ts
    └── config/          site.ts, navigation.ts
```

---

## Prisma Schema (9 models)

```prisma
// prisma/schema.prisma
generator client { provider = "prisma-client-js" }
datasource db    { provider = "postgresql"; url = env("DATABASE_URL") }

enum Role        { CUSTOMER ADMIN }
enum OrderStatus { PENDING PROCESSING SHIPPED DELIVERED CANCELLED REFUNDED }
enum ProductType { PHYSICAL SERVICE }
enum ServiceTier { BASIC STANDARD PREMIUM ENTERPRISE }

model User         { id, email, name, passwordHash, role, avatarUrl, phone, createdAt, updatedAt
                     relations: addresses, orders, cart, wishlist, reviews }
model Address      { id, userId, label, line1, line2, city, state, postalCode, country, isDefault }
model Category     { id, name, slug, description, imageUrl, iconName, sortOrder, isActive
                     relations: products[] }
model Product      { id, categoryId, name, slug, brand, description, price, comparePrice, sku, stock,
                     isActive, isFeatured, isNewArrival, productType, imageUrls[], thumbnailUrl, tags[]
                     relations: category, specs[], cartItems[], orderItems[], wishlistItems[], reviews[] }
model ProductSpec  { id, productId, key, value, unit, sortOrder }
model CartItem     { id, userId, productId, quantity, addedAt; @@unique([userId, productId]) }
model WishlistItem { id, userId, productId, addedAt; @@unique([userId, productId]) }
model Order        { id, userId, shippingAddressId, status, subtotal, shippingCost, tax, total, notes
                     relations: user, shippingAddress, items[] }
model OrderItem    { id, orderId, productId, quantity, unitPrice, totalPrice, productName }
model Review       { id, productId, userId, rating, title, body, isVerified
                     @@unique([productId, userId]) }
model Service      { id, name, slug, shortDesc, description, tier, priceFrom, iconName,
                     features[], isActive, isFeatured, sortOrder }
```

---

## Tailwind Theme (Dark/Midnight)

CSS variables in `globals.css`:
```css
:root {
  --background:       220 13% 4%;    /* #030712 — page bg */
  --card:             220 16% 10%;   /* #111827 — card bg */
  --primary:          217 91% 60%;   /* #3b82f6 — blue-500 */
  --accent:           189 94% 53%;   /* #22d3ee — cyan-400 */
  --border:           215 14% 25%;   /* #374151 — gray-700 */
  --muted-foreground: 215 16% 47%;   /* #9ca3af */
  --radius: 0.5rem;
}
```

Custom `gz.*` tokens in tailwind config:
- `gz-bg-base` #030712, `gz-bg-card` #111827, `gz-bg-elevated` #1f2937
- `gz-blue` #3b82f6, `gz-cyan` #22d3ee
- `gz-new` #8b5cf6 (New Arrival badge), `gz-success` #10b981, `gz-warning` #f59e0b

Custom shadows: `shadow-glow-blue`, `shadow-card-hover`
Custom animations: `fade-in`, `slide-up`, `shimmer` (for skeleton loading states)

### Color Usage Reference

| Element | Tailwind Class | Hex |
|---|---|---|
| Page background | `bg-gray-950` | `#030712` |
| Card background | `bg-gray-900` | `#111827` |
| Elevated (inputs, hover) | `bg-gray-800` | `#1f2937` |
| Primary border | `border-gray-700` | `#374151` |
| Primary accent | `bg-blue-500` | `#3b82f6` |
| Secondary accent | `text-cyan-400` | `#22d3ee` |
| New Arrival badge | `bg-violet-500` | `#8b5cf6` |
| In Stock | `text-emerald-500` | `#10b981` |
| Low Stock | `text-amber-500` | `#f59e0b` |
| Out of Stock | `text-red-500` | `#ef4444` |

---

## shadcn/ui Components to Install

```bash
npx shadcn@latest add navigation-menu sheet separator breadcrumb scroll-area \
  card badge avatar carousel tabs accordion skeleton tooltip \
  button input label select checkbox radio-group slider textarea \
  dialog drawer dropdown-menu popover progress toast alert pagination
```

---

## Key Component Designs

### Navbar
```
[≡] GeekendZone | [🔍 Search products...] | [♡] [🛒3] [👤]
────────────────────────────────────────────────────────────
PCs  Laptops  Monitors  Keyboards  Mice  GPUs  Servers  Services
```
Sticky with `backdrop-blur`, `bg-background/95`, border-b

### TrustBar (below navbar)
4 items: Free Shipping (orders $99+) | 30-Day Returns | Secure Checkout | Expert Support Mon-Sat

### ProductCard (most reused component)
```
┌──────────────────────────┐
│ [NEW ARRIVAL] badge  [♡] │  ← absolute positioned
│   ┌──────────────────┐   │
│   │   Product Image  │   │  ← aspect-[4/3], bg-gray-800
│   └──────────────────┘   │
│ Brand (muted text)        │
│ Product Name (2-line)     │
│ [Spec] [Chip] [Badges]    │  ← cyan-400 text, key specs
│ ★★★★½  (128)              │
│ $1,599  ~~$1,899~~  -15%  │
│ [+ Add to Cart]           │  ← bg-blue-500, full width
└──────────────────────────┘
```
Props: `product`, `viewMode ("grid"|"list")`, `onAddToCart`, `onToggleWishlist`, `isInWishlist`

### FilterSidebar (most complex component)
Accordion sections:
- **Always**: Brand (searchable checkboxes), Price range (Slider + inputs), In Stock, New Arrivals
- **Category-specific**: spec filters from `CATEGORY_FILTER_SPECS` constant

Props: `filters`, `onFilterChange`, `availableBrands`, `priceRange`, `availableSpecs`, `productCount`

---

## Category-Specific Filter Specs (`src/lib/constants.ts` — `CATEGORY_FILTER_SPECS`)

| Category | Filters |
|---|---|
| pcs | cpu_brand, ram, storage_type, storage_size, gpu_brand, form_factor |
| laptops | cpu_brand, ram, storage_size, screen_size, use_case |
| monitors | resolution, screen_size, refresh_rate, panel_type, connectivity |
| keyboards | switch_type, form_factor, connectivity, backlight |
| mice | dpi_range, connectivity, grip_style, use_case |
| gpus | manufacturer, vram, memory_type, tdp |
| servers | form_factor, cpu_sockets, max_ram, storage_bays |
| networking | speed, ports, interface |

---

## Custom Hooks

| Hook | Purpose | Storage |
|---|---|---|
| `useCart` | items, addItem, removeItem, updateQuantity, clearCart, totalItems, subtotal | localStorage |
| `useWishlist` | items[], toggle, isInWishlist, count | localStorage |
| `useFilters` | FilterState, setFilter, toggleBrand, setPriceRange, clearFilters, activeFilterCount | URL search params |
| `useSearch` | query, results, isLoading | local state |
| `useLocalStorage` | generic SSR-safe read/write | — |

---

## TypeScript Types (`src/types/`)

```typescript
// product.ts
interface Product {
  id, categoryId, categorySlug, name, slug, brand, description,
  price, comparePrice?, sku, stock, isActive, isFeatured, isNewArrival,
  imageUrls[], thumbnailUrl, tags[], specs: ProductSpec[],
  rating?, reviewCount?
}
interface ProductSpec { key, value, unit? }
type ViewMode = "grid" | "list"
type SortOption = "relevance" | "price-asc" | "price-desc" | "name-asc" | "newest" | "rating"

// filters.ts
interface FilterState { brands: string[], priceRange: PriceRange,
  specs: Record<string, string[]>, inStock: boolean, isNewArrival: boolean }

// service.ts
interface ITService { id, name, slug, shortDesc, description,
  tier: "BASIC"|"STANDARD"|"PREMIUM"|"ENTERPRISE", priceFrom?,
  iconName, features[], isFeatured }
```

---

## Pages

| Route | Layout | Key Components |
|---|---|---|
| `/` | (shop) | HeroBanner, CategoryGrid, FeaturedProducts (tabs), ServicesSection, Newsletter |
| `/products` | (shop) | FilterSidebar + ProductGrid + SortControls + Pagination |
| `/products/[category]` | (shop) | Same + category-specific filters |
| `/products/[category]/[slug]` | (shop) | ImageGallery + ProductInfo + SpecsTable + ReviewSection + RelatedProducts |
| `/services` | (shop) | ServicesHero + ServiceTiersGrid + ProcessSection + ContactCTA |
| `/cart` | (shop) | CartItemList 65% + CartSummary sticky 35% |
| `/checkout` | (shop) | CheckoutStepper (3 steps) + OrderSummary sidebar |
| `/search` | (shop) | Same as /products + search query header |
| `/account` | (auth) | Tabs: LoginForm / RegisterForm |
| `/account/profile` | (auth) | ProfileCard + address management |
| `/account/orders` | (auth) | OrderHistoryItem list |

---

## Mock Data

- **8 categories**: Desktop PCs, Laptops, Monitors, Keyboards, Mice, GPU Cards, Ethernet Cards, Servers
- **20+ products** across all categories (varying price, brand, specs to make filters meaningful)
- **6 IT services**: Infrastructure Assessment, Managed IT Support, Server Setup, Cloud Migration, Cybersecurity Hardening, Hardware Procurement
- **Mock reviews** with ratings 3.5–5.0

---

## Implementation Phases

### Phase 1 — Foundation
1. `npx create-next-app@latest ecommerce-site --typescript --tailwind --app --src-dir --import-alias "@/*"`
2. Configure `tailwind.config.ts` with custom colors, shadows, animations
3. Add CSS variables to `globals.css` for dark theme
4. `npx shadcn@latest init` (dark, slate base) + install all components
5. Create all TypeScript types, lib utilities, config files, mock data files
6. Add `prisma/schema.prisma`

### Phase 2 — Layout Shell
7. Navbar (logo, search, icons, category NavigationMenu)
8. NavbarMobile (hamburger + Sheet drawer)
9. TrustBar, Footer
10. Root layout, (shop) layout, (auth) layout
11. Shared: SearchBar, PriceDisplay, StarRating, WishlistButton

### Phase 3 — Home Page
12. HeroBanner (Carousel + gradient overlay text)
13. CategoryCard + CategoryGrid
14. ProductCard (grid view)
15. FeaturedProducts (tabbed + carousel)
16. ServiceCard + ServicesSection
17. Newsletter (email input + success state)
18. Assemble `app/page.tsx`

### Phase 4 — Product Listing
19. ProductGrid + ProductListItem (list view)
20. ViewToggle, SortControls, ActiveFilters (chip row)
21. FilterBrandSearch → FilterPriceRange → FilterSpecs → FilterSidebar
22. MobileFilterDrawer, Breadcrumb
23. `/products/page.tsx` and `/products/[category]/page.tsx`

### Phase 5 — Product Detail
24. ImageGallery (thumbnail strip + zoom)
25. QuantitySelector, AddToCartButton
26. ProductInfo (name, price, stock, specs tabs)
27. SpecsTable, ReviewCard + ReviewSection
28. RelatedProducts
29. `/products/[category]/[slug]/page.tsx`

### Phase 6 — Cart + State Hooks
30. `useLocalStorage`, `useCart`, `useWishlist`
31. CartItem, CartSummary, EmptyCart
32. `/cart/page.tsx` + wire Navbar badge counts

### Phase 7 — Remaining Pages
33. CheckoutStepper + ShippingForm + PaymentForm + OrderReview → `/checkout/page.tsx`
34. ServicesSection full-page variant → `/services/page.tsx`
35. `useSearch` + `useFilters` → `/search/page.tsx`

### Phase 8 — Account + Polish
36. LoginForm, RegisterForm → `/account/page.tsx`
37. ProfileCard, OrderHistoryItem → profile/orders pages
38. `LoadingSkeleton` for all loading states, `EmptyState`, `not-found.tsx`
39. Final responsive pass (mobile breakpoints: 375px, 768px, 1024px)

---

## Key Config Files

**`next.config.ts`**
```typescript
const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "images.unsplash.com" },
      { protocol: "https", hostname: "placehold.co" },
    ],
  },
};
```

**`components.json`** (shadcn)
```json
{
  "style": "default", "rsc": true, "tsx": true,
  "tailwind": { "config": "tailwind.config.ts", "css": "src/app/globals.css",
    "baseColor": "slate", "cssVariables": true },
  "aliases": { "components": "@/components", "utils": "@/lib/utils",
    "ui": "@/components/ui", "lib": "@/lib", "hooks": "@/hooks" }
}
```

**Key `package.json` dependencies**
- next, react, react-dom
- @prisma/client
- react-hook-form, @hookform/resolvers, zod
- lucide-react
- class-variance-authority, clsx, tailwind-merge, tailwindcss-animate
- embla-carousel-react

---

## Verification Checklist

- [ ] `npm run dev` — all pages render without errors
- [ ] Home: hero visible, 8 category cards, 4+ featured products with tabs, 3+ service cards
- [ ] `/products/pcs` — PC-specific filters in sidebar, price slider works, sort dropdown works
- [ ] `/products/pcs/[slug]` — image gallery, specs table, reviews render
- [ ] Add to cart: badge increments, cart page shows item, quantity updates
- [ ] Wishlist: heart toggles, count updates in navbar
- [ ] Checkout: stepper advances through all 3 steps
- [ ] Mobile (375px): hamburger nav opens, filter drawer opens, cards stack single column
- [ ] Dark theme consistent across all pages, no flash of unstyled content
