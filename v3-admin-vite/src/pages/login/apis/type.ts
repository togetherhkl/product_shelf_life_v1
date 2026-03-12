export interface LoginRequestData {
  /** admin 或 editor */
  username: "admin" | "editor"
  /** 密码 */
  password: string
  /** 验证码 */
  // code: string
}

export interface LoginResponseData {
  /** 访问令牌 */
  access_token: string
  /** 令牌类型 */
  token_type: string
  /** 管理员ID */
  admin_id: string
  /** 用户名 */
  username: string
  /** 角色 */
  role: string
}

export type CaptchaResponseData = ApiResponseData<string>
