import type * as Admin from "./type"
import { request } from "@/http/axios"

/** 获取管理员列表 */
export function getAdminListApi(params: Admin.AdminListRequestData) {
  return request<Admin.AdminListWithTotalData>({
    url: "admin",
    method: "get",
    params
  })
}

/** 新增管理员 */
export function createAdminApi(data: Admin.CreateOrUpdateAdminRequestData) {
  return request({
    url: "admin",
    method: "post",
    data
  })
}

/** 更新管理员 */
export function updateAdminApi(data: Admin.CreateOrUpdateAdminRequestData) {
  return request({
    url: `admin/${data.admin_id}`,
    method: "put",
    data
  })
}

/** 删除管理员 */
export function deleteAdminApi(admin_id: string) {
  return request({
    url: `admin/${admin_id}`,
    method: "delete"
  })
}
