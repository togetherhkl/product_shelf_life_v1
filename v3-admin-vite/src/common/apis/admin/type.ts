export interface CreateOrUpdateAdminRequestData {
  admin_id?: string
  username: string
  password_hash?: string
  role: string
  is_active?: boolean
}

export interface AdminListRequestData {
  /** 跳过条数 (offset) */
  skip?: number
  /** 查询条数 (limit) */
  limit?: number
  /** 查询参数：用户名 */
  username?: string
  /** 查询参数：角色 */
  role?: string
}

export interface AdminData {
  admin_id: string
  username: string
  password_hash: string
  role: string
  is_active: boolean
  created_at: string
}

export interface AdminListWithTotalData {
  /** 管理员列表 */
  admins: AdminData[]
  /** 总记录数 */
  total: number
}

export type AdminListResponseData = ApiResponseData<AdminListWithTotalData>
