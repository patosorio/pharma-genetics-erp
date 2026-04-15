export interface StrainCategory {
  id: number
  name: string
  description: string
}

export interface Strain {
  id: number
  name: string
  slug: string
  catalogue_year: number
  category: number
  category_name: string
  description: string
  thc_percentage: string | null
  cbd_percentage: string | null
  terpene_profile: string
  breeder: string
  lineage: string
  image: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  created_by?: number
  updated_by?: number
}
