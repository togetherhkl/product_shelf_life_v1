import type * as Users from "./type"
import { request } from "@/http/axios"

/** 获取当前登录用户详情 */
export function getCurrentUserApi() {
  return request<Users.CurrentUserData>({
    url: "admin/me",
    method: "get"
  })
}

/** 获取用户列表 */
export function getUserListApi(params: Users.UserListRequestData) {
  return request<Users.UserListWithTotalData>({
    url: "user",
    method: "get",
    params
  })
}

/** 新增用户 */
export function createUserApi(data: Users.CreateOrUpdateUserRequestData) {
  return request({
    url: "user",
    method: "post",
    data
  })
}

/** 更新用户 */
export function updateUserApi(data: Users.CreateOrUpdateUserRequestData) {
  return request({
    url: `user/${data.user_id}`,
    method: "put",
    data
  })
}

/** 删除用户 */
export function deleteUserApi(user_id: string) {
  return request({
    url: `user/${user_id}`,
    method: "delete"
  })
}
