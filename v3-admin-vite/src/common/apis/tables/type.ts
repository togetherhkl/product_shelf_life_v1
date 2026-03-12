export interface CreateOrUpdateTableRequestData {
  user_id?: string
  openid?: string
  nickname: string
  avatar_url?: string
  phone_number?: string
  email?: string
  introduction?: string
  is_active?: boolean
}

export interface TableRequestData {
  /** 当前页码 */
  currentPage: number
  /** 查询条数 */
  size: number
  /** 查询参数：昵称 */
  nickname?: string
  /** 查询参数：手机号 */
  phone_number?: string
  /** 查询参数：邮箱 */
  email?: string
  /** 查询参数：openid */
  openid?: string
}

export interface TableData {
  user_id: string
  openid: string
  nickname: string
  avatar_url?: string
  phone_number?: string
  email?: string
  introduction?: string
  is_active: boolean
  created_at: string
  last_login_at?: string
}

export type TableResponseData = ApiResponseData<{
  list: TableData[]
  total: number
}>
