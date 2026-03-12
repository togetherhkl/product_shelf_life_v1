<script lang="ts" setup>
import type { FormRules } from "element-plus"
import type { CategoryData } from "@/common/apis/category/type"
import type { CreateOrUpdateProductRequestData, ProductData } from "@/common/apis/product/type"
import { CirclePlus, Clock, Download, InfoFilled, Refresh, RefreshRight, Search, Warning } from "@element-plus/icons-vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { onMounted, reactive, ref, useTemplateRef, watch } from "vue"
import * as CategoryApi from "@/common/apis/category"
import * as ProductApi from "@/common/apis/product"
import { usePagination } from "@/common/composables/usePagination"
import { formatDateTime } from "@/common/utils/datetime"

defineOptions({
  // 命名当前组件
  name: "ProductManage"
})

const loading = ref<boolean>(false)
const { paginationData, handleCurrentChange, handleSizeChange } = usePagination()

// #region 增
const dialogVisible = ref<boolean>(false)
const formRef = useTemplateRef("formRef")
const fetchingProductInfo = ref<boolean>(false)
const formData = ref<CreateOrUpdateProductRequestData>({
  name: "",
  barcode_or_qr: "",
  category_id: "",
  batch_number: "",
  production_date: "",
  expiration_date: "",
  image_url: "",
  description: ""
})
const formRules: FormRules<CreateOrUpdateProductRequestData> = {
  name: [{ required: true, message: "请输入产品名称", trigger: "blur" }],
  barcode_or_qr: [{ required: true, message: "请输入扫码值", trigger: "blur" }],
  category_id: [{ required: true, message: "请选择分类", trigger: "change" }]
}

function handleCreateOrUpdate() {
  formRef.value?.validate((valid: boolean, fields) => {
    if (!valid) return console.error("表单校验不通过", fields)
    loading.value = true
    const api = formData.value.product_id === undefined ? ProductApi.createProductApi : ProductApi.updateProductApi
    api(formData.value)
      .then(() => {
        ElMessage.success("操作成功")
        dialogVisible.value = false
        getProductData()
      })
      .catch(() => {
        loading.value = false
      })
  })
}

function resetForm() {
  formRef.value?.clearValidate()
  formData.value = {
    name: "",
    barcode_or_qr: "",
    category_id: "",
    batch_number: "",
    production_date: "",
    expiration_date: "",
    image_url: "",
    description: ""
  }
}

// 根据扫码值获取产品信息
function fetchProductInfo() {
  if (!formData.value.barcode_or_qr.trim()) {
    ElMessage.warning("请先输入扫码值")
    return
  }

  fetchingProductInfo.value = true
  ProductApi.getProductInfoByBarcodeApi(formData.value.barcode_or_qr)
    .then((data) => {
      if (data.status === "success") {
        // 自动填充获取到的信息
        formData.value.name = data.name
        formData.value.image_url = data.image_url || ""
        formData.value.description = data.description || ""
        // 保留用户已输入的其他信息，只更新从接口获取的信息
        ElMessage.success(data.message || "成功获取产品信息")
      } else {
        ElMessage.error(data.message || "获取产品信息失败")
      }
    })
    .catch((error) => {
      console.error("获取产品信息失败:", error)
      ElMessage.error("获取产品信息失败，请检查扫码值是否正确")
    })
    .finally(() => {
      fetchingProductInfo.value = false
    })
}
// #endregion

// #region 删
function handleDelete(row: ProductData) {
  ElMessageBox.confirm(`正在删除产品：${row.name}，确认删除？`, "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning"
  }).then(() => {
    ProductApi.deleteProductApi(row.product_id).then(() => {
      ElMessage.success("删除成功")
      getProductData()
    })
  })
}
// #endregion

// #region 改
function handleUpdate(row: ProductData) {
  dialogVisible.value = true
  formData.value = {
    product_id: row.product_id,
    name: row.name,
    barcode_or_qr: row.barcode_or_qr,
    category_id: row.category_id,
    batch_number: row.batch_number || "",
    production_date: row.production_date || "",
    expiration_date: row.expiration_date || "",
    image_url: row.image_url || "",
    description: row.description || ""
  }
}
// #endregion

// #region 查
const tableData = ref<ProductData[]>([])
const searchFormRef = useTemplateRef("searchFormRef")
const searchData = reactive({
  name: "",
  barcode_or_qr: "",
  category_id: "",
  status: ""
})

// 分类选项
const categoryOptions = ref<CategoryData[]>([])

function getProductData() {
  loading.value = true

  // 根据状态选择不同的API
  let apiCall: Promise<any>

  if (searchData.status === "expired") {
    apiCall = ProductApi.getExpiredProductsApi({
      skip: (paginationData.currentPage - 1) * paginationData.pageSize,
      limit: paginationData.pageSize
    })
  } else if (searchData.status === "expiring") {
    apiCall = ProductApi.getExpiringSoonProductsApi({
      days: 7,
      skip: (paginationData.currentPage - 1) * paginationData.pageSize,
      limit: paginationData.pageSize
    })
  } else {
    apiCall = ProductApi.getProductListApi({
      skip: (paginationData.currentPage - 1) * paginationData.pageSize,
      limit: paginationData.pageSize,
      name: searchData.name || undefined,
      barcode_or_qr: searchData.barcode_or_qr || undefined,
      category_id: searchData.category_id || undefined
    })
  }

  apiCall.then((data) => {
    console.log("产品列表", data)
    console.log("第一个产品数据结构:", data.products[0])
    if (data.products[0]) {
      console.log("分类信息:", data.products[0].category)
      console.log("分类ID:", data.products[0].category_id)
      console.log("创建者信息:", data.products[0].created_by_admin)
      console.log("创建者ID:", data.products[0].created_by_admin_id)
    }
    tableData.value = data.products
    paginationData.total = data.total
  }).catch(() => {
    tableData.value = []
  }).finally(() => {
    loading.value = false
  })
}

function handleSearch() {
  paginationData.currentPage === 1 ? getProductData() : (paginationData.currentPage = 1)
}

function resetSearch() {
  searchFormRef.value?.resetFields()
  handleSearch()
}

function handleExpiringSoon() {
  searchData.status = "expiring"
  handleSearch()
}

function handleExpired() {
  searchData.status = "expired"
  handleSearch()
}

// 获取分类列表
function getCategoryData() {
  CategoryApi.getCategoryListApi({ skip: 0, limit: 1000 })
    .then((data) => {
      categoryOptions.value = data.categories
    })
    .catch(() => {
      categoryOptions.value = []
    })
}
// #endregion

// #region 工具函数
function getImageUrl(imageUrl: string) {
  if (!imageUrl) return ""
  if (imageUrl.startsWith("http")) return imageUrl
  const baseURL = import.meta.env.VITE_BASE_URL || "http://localhost:8000"
  return `${baseURL}${imageUrl}`
}

function getExpirationStatus(expirationDate: string) {
  if (!expirationDate) return { type: "" as const, text: "" }

  const today = new Date()
  const expDate = new Date(expirationDate)
  const diffTime = expDate.getTime() - today.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays < 0) {
    return { type: "danger" as const, text: "已过期" }
  } else if (diffDays <= 7) {
    return { type: "warning" as const, text: "即将过期" }
  } else {
    return { type: "success" as const, text: "正常" }
  }
}

// 根据分类ID获取分类名称
function getCategoryNameById(categoryId: string) {
  const category = categoryOptions.value.find(cat => cat.category_id === categoryId)
  return category ? category.category_name : `未知分类(${categoryId})`
}
// #endregion

// 监听分页参数的变化
watch([() => paginationData.currentPage, () => paginationData.pageSize], getProductData, { immediate: true })

onMounted(() => {
  getCategoryData()
})
</script>

<template>
  <div class="app-container">
    <el-card v-loading="loading" shadow="never" class="search-wrapper">
      <el-form ref="searchFormRef" :inline="true" :model="searchData">
        <el-form-item prop="name" label="产品名称">
          <el-input v-model="searchData.name" placeholder="请输入产品名称" style="width: 180px" />
        </el-form-item>
        <el-form-item prop="barcode_or_qr" label="扫码值">
          <el-input v-model="searchData.barcode_or_qr" placeholder="请输入条形码或二维码" style="width: 200px" />
        </el-form-item>
        <el-form-item prop="category_id" label="分类">
          <el-select v-model="searchData.category_id" placeholder="请选择分类" clearable style="width: 160px">
            <el-option
              v-for="category in categoryOptions"
              :key="category.category_id"
              :label="category.category_name"
              :value="category.category_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item prop="status" label="状态">
          <el-select v-model="searchData.status" placeholder="请选择状态" clearable style="width: 120px">
            <el-option label="正常" value="normal" />
            <el-option label="即将过期" value="expiring" />
            <el-option label="已过期" value="expired" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">
            查询
          </el-button>
          <el-button :icon="Refresh" @click="resetSearch">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    <el-card v-loading="loading" shadow="never">
      <div class="toolbar-wrapper">
        <div>
          <el-button type="primary" :icon="CirclePlus" @click="dialogVisible = true">
            新增产品
          </el-button>
          <el-button type="warning" :icon="Clock" @click="handleExpiringSoon">
            即将过期
          </el-button>
          <el-button type="danger" :icon="Warning" @click="handleExpired">
            已过期
          </el-button>
        </div>
        <div>
          <el-tooltip content="下载">
            <el-button type="primary" :icon="Download" circle />
          </el-tooltip>
          <el-tooltip content="刷新当前页">
            <el-button type="primary" :icon="RefreshRight" circle @click="getProductData" />
          </el-tooltip>
        </div>
      </div>
      <div class="table-wrapper">
        <el-table :data="tableData">
          <el-table-column type="selection" width="50" align="center" />
          <el-table-column prop="image_url" label="产品图片" align="center" width="100">
            <template #default="scope">
              <el-image
                v-if="scope.row.image_url"
                :src="getImageUrl(scope.row.image_url)"
                :preview-src-list="[getImageUrl(scope.row.image_url)]"
                fit="cover"
                style="width: 50px; height: 50px; border-radius: 4px"
                preview-teleported
              />
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="产品名称" align="center" min-width="120" />
          <el-table-column prop="barcode_or_qr" label="扫码值" align="center" min-width="120">
            <template #default="scope">
              <el-tag size="small">
                {{ scope.row.barcode_or_qr }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="category" label="分类" align="center" min-width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.category" type="info" size="small">
                {{ scope.row.category.category_name }}
              </el-tag>
              <el-tag v-else-if="scope.row.category_id" type="success" size="small">
                {{ getCategoryNameById(scope.row.category_id) }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="batch_number" label="批次号" align="center" min-width="100">
            <template #default="scope">
              <span>{{ scope.row.batch_number || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="production_date" label="生产日期" align="center" min-width="110">
            <template #default="scope">
              <span>{{ scope.row.production_date || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="expiration_date" label="到期日期" align="center" min-width="110">
            <template #default="scope">
              <el-tag
                v-if="scope.row.expiration_date"
                :type="getExpirationStatus(scope.row.expiration_date).type"
                size="small"
              >
                {{ scope.row.expiration_date }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_by_admin" label="创建者" align="center" min-width="100">
            <template #default="scope">
              <span v-if="scope.row.created_by_admin">{{ scope.row.created_by_admin.username }}</span>
              <el-tag v-else-if="scope.row.created_by_admin_id" type="warning" size="small">
                ID: {{ scope.row.created_by_admin_id }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" align="center" min-width="160">
            <template #default="scope">
              <span>{{ formatDateTime(scope.row.created_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column fixed="right" label="操作" width="150" align="center">
            <template #default="scope">
              <el-button type="primary" text bg size="small" @click="handleUpdate(scope.row)">
                修改
              </el-button>
              <el-button type="danger" text bg size="small" @click="handleDelete(scope.row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div class="pager-wrapper">
        <el-pagination
          background
          :layout="paginationData.layout"
          :page-sizes="paginationData.pageSizes"
          :total="paginationData.total"
          :page-size="paginationData.pageSize"
          :current-page="paginationData.currentPage"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    <!-- 新增/修改 -->
    <el-dialog
      v-model="dialogVisible"
      :title="formData.product_id === undefined ? '新增产品' : '修改产品'"
      @closed="resetForm"
      width="600px"
    >
      <el-alert
        v-if="formData.product_id === undefined"
        title="提示：输入扫码值后点击「获取信息」按钮，可从商品数据库中自动获取产品基本信息，然后手动补充其他必要信息。"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      />
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px" label-position="left">
        <el-form-item prop="name" label="产品名称">
          <el-input v-model="formData.name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item prop="barcode_or_qr" label="扫码值">
          <div style="display: flex; gap: 8px; align-items: center;">
            <el-input
              v-model="formData.barcode_or_qr"
              placeholder="请输入条形码或二维码"
              style="flex: 1;"
            />
            <el-button
              type="primary"
              :icon="InfoFilled"
              :loading="fetchingProductInfo"
              @click="fetchProductInfo"
            >
              获取信息
            </el-button>
          </div>
        </el-form-item>
        <el-form-item prop="category_id" label="分类">
          <el-select v-model="formData.category_id" placeholder="请选择分类" style="width: 100%;">
            <el-option
              v-for="category in categoryOptions"
              :key="category.category_id"
              :label="category.category_name"
              :value="category.category_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item prop="batch_number" label="批次号">
          <el-input v-model="formData.batch_number" placeholder="请输入批次号" />
        </el-form-item>
        <el-form-item prop="production_date" label="生产日期">
          <el-date-picker
            v-model="formData.production_date"
            type="date"
            placeholder="请选择生产日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item prop="expiration_date" label="到期日期">
          <el-date-picker
            v-model="formData.expiration_date"
            type="date"
            placeholder="请选择到期日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item prop="image_url" label="产品图片">
          <el-input v-model="formData.image_url" placeholder="请输入图片URL" />
        </el-form-item>
        <el-form-item prop="description" label="产品描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            placeholder="请输入产品描述"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">
          取消
        </el-button>
        <el-button type="primary" @click="handleCreateOrUpdate" :loading="loading">
          确认
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.search-wrapper {
  margin-bottom: 20px;
  :deep(.el-card__body) {
    padding-bottom: 2px;
  }

  // 搜索表单响应式优化
  :deep(.el-form--inline) {
    .el-form-item {
      margin-bottom: 16px;
    }

    // 在小屏幕上调整表单项的宽度
    @media (max-width: 1200px) {
      .el-input {
        width: 150px !important;
      }
      .el-select {
        width: 130px !important;
      }
    }

    @media (max-width: 768px) {
      .el-input {
        width: 120px !important;
      }
      .el-select {
        width: 100px !important;
      }
    }
  }
}

.toolbar-wrapper {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.table-wrapper {
  margin-bottom: 20px;
}

.pager-wrapper {
  display: flex;
  justify-content: flex-end;
}
</style>
