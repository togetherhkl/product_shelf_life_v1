export interface CurrentUserData {
  /** 用户名 */
  username: string
  /** 密码哈希 */
  password_hash: string
  /** 角色 */
  role: string
  /** 账户状态（1:活跃, 0:禁用） */
  is_active: number
  /** 管理员ID */
  admin_id: string
  /** 创建时间 */
  created_at: string
}

export type CurrentUserResponseData = ApiResponseData<CurrentUserData>

export interface CreateOrUpdateUserRequestData {
  user_id?: string
  openid?: string
  nickname: string
  avatar_url?: string
  phone_number?: string
  email?: string
  introduction?: string
  is_active?: boolean
}

export interface UserListRequestData {
  /** 跳过条数 (offset) */
  skip?: number
  /** 查询条数 (limit) */
  limit?: number
  /** 查询参数：昵称 */
  nickname?: string
  /** 查询参数：手机号 */
  phone_number?: string
  /** 查询参数：邮箱 */
  email?: string
  /** 查询参数：openid */
  openid?: string
}

export interface UserData {
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

export interface UserListWithTotalData {
  /** 用户列表 */
  users: UserData[]
  /** 总记录数 */
  total: number
}

export type UserListResponseData = ApiResponseData<UserListWithTotalData>
