import type * as Category from "./type"
import { request } from "@/http/axios"

/** 获取分类列表 */
export function getCategoryListApi(params: Category.CategoryListRequestData) {
  return request<Category.CategoryListWithTotalData>({
    url: "category",
    method: "get",
    params
  })
}

/** 新增分类 */
export function createCategoryApi(data: Category.CreateOrUpdateCategoryRequestData) {
  return request({
    url: "category",
    method: "post",
    data
  })
}

/** 更新分类 */
export function updateCategoryApi(data: Category.CreateOrUpdateCategoryRequestData) {
  return request({
    url: `category/${data.category_id}`,
    method: "put",
    data
  })
}

/** 删除分类 */
export function deleteCategoryApi(category_id: string) {
  return request({
    url: `category/${category_id}`,
    method: "delete"
  })
}
