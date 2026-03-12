<script lang="ts" setup>
import type { CategoryData, CreateOrUpdateCategoryRequestData } from "@@/apis/category/type"
import type { FormRules } from "element-plus"
import { createCategoryApi, deleteCategoryApi, getCategoryListApi, updateCategoryApi } from "@@/apis/category"
import { usePagination } from "@@/composables/usePagination"
import { CirclePlus, Refresh, RefreshRight, Search } from "@element-plus/icons-vue"
import { cloneDeep } from "lodash-es"

defineOptions({
  // 命名当前组件
  name: "CategoryManagement"
})

const loading = ref<boolean>(false)

const { paginationData, handleCurrentChange, handleSizeChange } = usePagination()

// #region 增
const DEFAULT_FORM_DATA: CreateOrUpdateCategoryRequestData = {
  category_id: undefined,
  category_name: ""
}

const dialogVisible = ref<boolean>(false)

const formRef = useTemplateRef("formRef")

const formData = ref<CreateOrUpdateCategoryRequestData>(cloneDeep(DEFAULT_FORM_DATA))

const formRules: FormRules<CreateOrUpdateCategoryRequestData> = {
  category_name: [
    { required: true, trigger: "blur", message: "请输入分类名称" },
    { min: 2, max: 100, trigger: "blur", message: "分类名称长度在 2 到 100 个字符" }
  ]
}

function handleCreateOrUpdate() {
  formRef.value?.validate((valid) => {
    if (!valid) {
      ElMessage.error("表单校验不通过")
      return
    }
    loading.value = true
    const api = formData.value.category_id === undefined ? createCategoryApi : updateCategoryApi
    api(formData.value).then(() => {
      ElMessage.success("操作成功")
      dialogVisible.value = false
      getCategoryData()
    }).finally(() => {
      loading.value = false
    })
  })
}

function resetForm() {
  formRef.value?.clearValidate()
  formData.value = cloneDeep(DEFAULT_FORM_DATA)
}
// #endregion

// #region 删
function handleDelete(row: CategoryData) {
  ElMessageBox.confirm(`正在删除分类：${row.category_name}，确认删除？`, "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning"
  }).then(() => {
    deleteCategoryApi(row.category_id).then(() => {
      ElMessage.success("删除成功")
      getCategoryData()
    })
  })
}
// #endregion

// #region 改
function handleUpdate(row: CategoryData) {
  dialogVisible.value = true
  formData.value = cloneDeep(row)
}
// #endregion

// #region 查
const tableData = ref<CategoryData[]>([])

const searchFormRef = useTemplateRef("searchFormRef")

const searchData = reactive({
  category_name: ""
})

function getCategoryData() {
  loading.value = true
  getCategoryListApi({
    skip: (paginationData.currentPage - 1) * paginationData.pageSize,
    limit: paginationData.pageSize,
    category_name: searchData.category_name
  }).then((data) => {
    console.log("分类列表", data)
    tableData.value = data.categories
    paginationData.total = data.total
  }).catch(() => {
    tableData.value = []
  }).finally(() => {
    loading.value = false
  })
}

function handleSearch() {
  paginationData.currentPage === 1 ? getCategoryData() : (paginationData.currentPage = 1)
}

function resetSearch() {
  searchFormRef.value?.resetFields()
  handleSearch()
}
// #endregion

// 监听分页参数的变化
watch([() => paginationData.currentPage, () => paginationData.pageSize], getCategoryData, { immediate: true })
</script>

<template>
  <div class="app-container">
    <el-alert
      title="数据来源"
      type="success"
      description="数据来源于Mysql数据库"
      show-icon
    />
    <el-card v-loading="loading" shadow="never" class="search-wrapper">
      <el-form ref="searchFormRef" :inline="true" :model="searchData">
        <el-form-item prop="category_name" label="分类名称">
          <el-input v-model="searchData.category_name" placeholder="请输入分类名称" />
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
            新增分类
          </el-button>
        </div>
        <div>
          <el-tooltip content="刷新当前页">
            <el-button type="primary" :icon="RefreshRight" circle @click="getCategoryData" />
          </el-tooltip>
        </div>
      </div>
      <div class="table-wrapper">
        <el-table :data="tableData">
          <el-table-column type="selection" width="50" align="center" />
          <el-table-column prop="category_id" label="分类ID" align="center" width="200" />
          <el-table-column prop="category_name" label="分类名称" align="center">
            <template #default="scope">
              <el-tag type="primary" effect="light" disable-transitions>
                {{ scope.row.category_name }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" align="center" width="160" />
          <el-table-column prop="updated_at" label="更新时间" align="center" width="160" />
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
      :title="formData.category_id === undefined ? '新增分类' : '修改分类'"
      width="40%"
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px" label-position="left">
        <el-form-item prop="category_name" label="分类名称">
          <el-input
            v-model="formData.category_name"
            placeholder="请输入分类名称（如：食品、美妆）"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">
          取消
        </el-button>
        <el-button type="primary" :loading="loading" @click="handleCreateOrUpdate">
          确认
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.el-alert {
  margin-bottom: 20px;
}

.search-wrapper {
  margin-bottom: 20px;
  :deep(.el-card__body) {
    padding-bottom: 2px;
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
