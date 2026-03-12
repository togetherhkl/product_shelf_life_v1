export interface CreateOrUpdateCategoryRequestData {
  category_id?: string
  category_name: string
}

export interface CategoryListRequestData {
  /** 跳过条数 (offset) */
  skip?: number
  /** 查询条数 (limit) */
  limit?: number
  /** 查询参数：分类名称 */
  category_name?: string
}

export interface CategoryData {
  category_id: string
  category_name: string
  created_at: string
  updated_at: string
}

export interface CategoryListWithTotalData {
  /** 分类列表 */
  categories: CategoryData[]
  /** 总记录数 */
  total: number
}

export type CategoryListResponseData = ApiResponseData<CategoryListWithTotalData>
