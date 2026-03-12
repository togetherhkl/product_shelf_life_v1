export interface CreateOrUpdateProductRequestData {
  product_id?: string
  /** 扫码值（条形码或二维码） */
  barcode_or_qr: string
  /** 产品名称 */
  name: string
  /** 关联的分类ID */
  category_id: string
  /** 生产日期 */
  production_date?: string
  /** 到期日期 */
  expiration_date?: string
  /** 批次号 */
  batch_number?: string
  /** 产品详细描述 */
  description?: string
  /** 产品图像URL */
  image_url?: string
}

export interface ProductListRequestData {
  /** 跳过条数 (offset) */
  skip?: number
  /** 查询条数 (limit) */
  limit?: number
  /** 查询参数：产品名称 */
  name?: string
  /** 查询参数：分类ID */
  category_id?: string
  /** 查询参数：创建管理员ID */
  created_by_admin_id?: string
  /** 查询参数：条形码或二维码 */
  barcode_or_qr?: string
}

export interface ProductData {
  product_id: string
  /** 扫码值（条形码或二维码） */
  barcode_or_qr: string
  /** 产品名称 */
  name: string
  /** 关联的分类ID */
  category_id: string
  /** 添加该产品的管理员ID */
  created_by_admin_id?: string
  /** 生产日期 */
  production_date?: string
  /** 到期日期 */
  expiration_date?: string
  /** 批次号 */
  batch_number?: string
  /** 产品详细描述 */
  description?: string
  /** 产品图像URL */
  image_url?: string
  /** 创建时间 */
  created_at: string
  /** 最后更新时间 */
  updated_at: string
  /** 关联分类信息 */
  category?: {
    category_id: string
    category_name: string
  }
  /** 创建管理员信息 */
  created_by_admin?: {
    admin_id: string
    username: string
  }
}

export interface ProductListWithTotalData {
  /** 产品列表 */
  products: ProductData[]
  /** 总记录数 */
  total: number
}

export interface OpenFoodFactsResponse {
  /** 扫码值（条形码或二维码） */
  barcode_or_qr: string
  /** 产品名称 */
  name: string
  /** 产品图像URL */
  image_url?: string
  /** 产品描述 */
  description?: string
  /** 关联的分类ID */
  category_id?: string
  /** 添加该产品的管理员ID */
  created_by_admin_id?: string
  /** 生产日期 */
  production_date?: string
  /** 到期日期 */
  expiration_date?: string
  /** 批次号 */
  batch_number?: string
  /** 状态 */
  status: string
  /** 消息 */
  message: string
}

export type ProductListResponseData = ApiResponseData<ProductListWithTotalData>
