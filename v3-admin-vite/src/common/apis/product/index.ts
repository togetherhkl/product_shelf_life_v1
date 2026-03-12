import type * as Product from "./type"
import { request } from "@/http/axios"

/** 获取产品列表 */
export function getProductListApi(params: Product.ProductListRequestData) {
  return request<Product.ProductListWithTotalData>({
    url: "product",
    method: "get",
    params
  })
}

/** 新增产品 */
export function createProductApi(data: Product.CreateOrUpdateProductRequestData) {
  return request({
    url: "product",
    method: "post",
    data
  })
}

/** 更新产品 */
export function updateProductApi(data: Product.CreateOrUpdateProductRequestData) {
  return request({
    url: `product/${data.product_id}`,
    method: "put",
    data
  })
}

/** 删除产品 */
export function deleteProductApi(product_id: string) {
  return request({
    url: `product/${product_id}`,
    method: "delete"
  })
}

/** 根据产品ID获取产品详情 */
export function getProductByIdApi(product_id: string) {
  return request<Product.ProductData>({
    url: `product/${product_id}`,
    method: "get"
  })
}

/** 根据条形码获取产品详情 */
export function getProductByBarcodeApi(barcode_or_qr: string) {
  return request<Product.ProductData>({
    url: `product/barcode/${barcode_or_qr}`,
    method: "get"
  })
}

/** 根据分类获取产品列表 */
export function getProductsByCategoryApi(category_id: string, params: { skip?: number, limit?: number }) {
  return request<Product.ProductListWithTotalData>({
    url: `product/category/${category_id}`,
    method: "get",
    params
  })
}

/** 根据管理员获取产品列表 */
export function getProductsByAdminApi(admin_id: string, params: { skip?: number, limit?: number }) {
  return request<Product.ProductListWithTotalData>({
    url: `product/admin/${admin_id}`,
    method: "get",
    params
  })
}

/** 根据名称搜索产品 */
export function searchProductsByNameApi(name: string, params: { skip?: number, limit?: number }) {
  return request<Product.ProductListWithTotalData>({
    url: `product/search/name/${name}`,
    method: "get",
    params
  })
}

/** 获取已过期产品列表 */
export function getExpiredProductsApi(params: { skip?: number, limit?: number }) {
  return request<Product.ProductListWithTotalData>({
    url: "product/expired/list",
    method: "get",
    params
  })
}

/** 获取即将过期产品列表 */
export function getExpiringSoonProductsApi(params: { days?: number, skip?: number, limit?: number }) {
  return request<Product.ProductListWithTotalData>({
    url: "product/expiring-soon/list",
    method: "get",
    params
  })
}

/** 根据扫码值从OpenFoodFacts获取产品信息 */
export function getProductInfoByBarcodeApi(barcode_or_qr: string) {
  return request<Product.OpenFoodFactsResponse>({
    url: `product/openfoodfacts/${barcode_or_qr}`,
    method: "get"
  })
}
