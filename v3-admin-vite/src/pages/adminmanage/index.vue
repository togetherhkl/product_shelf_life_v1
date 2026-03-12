<script lang="ts" setup>
import type { AdminData, CreateOrUpdateAdminRequestData } from "@@/apis/admin/type"
import type { FormRules } from "element-plus"
import { createAdminApi, deleteAdminApi, getAdminListApi, updateAdminApi } from "@@/apis/admin"
import { usePagination } from "@@/composables/usePagination"
import { CirclePlus, Refresh, RefreshRight, Search } from "@element-plus/icons-vue"
import { cloneDeep } from "lodash-es"

defineOptions({
  // 命名当前组件
  name: "AdminManagement"
})

const loading = ref<boolean>(false)

const { paginationData, handleCurrentChange, handleSizeChange } = usePagination()

// #region 增
const DEFAULT_FORM_DATA: CreateOrUpdateAdminRequestData = {
  admin_id: undefined,
  username: "",
  password_hash: "",
  role: "",
  is_active: true
}

const dialogVisible = ref<boolean>(false)

const formRef = useTemplateRef("formRef")

const formData = ref<CreateOrUpdateAdminRequestData>(cloneDeep(DEFAULT_FORM_DATA))

const formRules: FormRules<CreateOrUpdateAdminRequestData> = {
  username: [{ required: true, trigger: "blur", message: "请输入用户名" }],
  password_hash: [{ required: true, trigger: "blur", message: "请输入密码" }],
  role: [{ required: true, trigger: "blur", message: "请选择角色" }]
}

// 角色选项
const roleOptions = [
  { label: "超级管理员", value: "super_admin" },
  { label: "编辑员", value: "editor" },
  { label: "审核员", value: "reviewer" }
]

function handleCreateOrUpdate() {
  formRef.value?.validate((valid) => {
    if (!valid) {
      ElMessage.error("表单校验不通过")
      return
    }
    loading.value = true
    const api = formData.value.admin_id === undefined ? createAdminApi : updateAdminApi
    api(formData.value).then(() => {
      ElMessage.success("操作成功")
      dialogVisible.value = false
      getAdminData()
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
function handleDelete(row: AdminData) {
  ElMessageBox.confirm(`正在删除管理员：${row.username}，确认删除？`, "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning"
  }).then(() => {
    deleteAdminApi(row.admin_id).then(() => {
      ElMessage.success("删除成功")
      getAdminData()
    })
  })
}
// #endregion

// #region 改
function handleUpdate(row: AdminData) {
  dialogVisible.value = true
  formData.value = cloneDeep(row)
  // 编辑时不需要密码字段
  formData.value.password_hash = undefined
}
// #endregion

// #region 查
const tableData = ref<AdminData[]>([])

const searchFormRef = useTemplateRef("searchFormRef")

const searchData = reactive({
  username: "",
  role: ""
})

function getAdminData() {
  loading.value = true
  getAdminListApi({
    skip: (paginationData.currentPage - 1) * paginationData.pageSize,
    limit: paginationData.pageSize,
    username: searchData.username,
    role: searchData.role
  }).then((data) => {
    console.log("管理员列表", data)
    tableData.value = data.admins
    paginationData.total = data.total
  }).catch(() => {
    tableData.value = []
  }).finally(() => {
    loading.value = false
  })
}

function handleSearch() {
  paginationData.currentPage === 1 ? getAdminData() : (paginationData.currentPage = 1)
}

function resetSearch() {
  searchFormRef.value?.resetFields()
  handleSearch()
}
// #endregion

// 监听分页参数的变化
watch([() => paginationData.currentPage, () => paginationData.pageSize], getAdminData, { immediate: true })
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
        <el-form-item prop="username" label="用户名">
          <el-input v-model="searchData.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item prop="role" label="角色">
          <el-select v-model="searchData.role" placeholder="请选择角色" clearable>
            <el-option
              v-for="option in roleOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
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
            新增管理员
          </el-button>
        </div>
        <div>
          <el-tooltip content="刷新当前页">
            <el-button type="primary" :icon="RefreshRight" circle @click="getAdminData" />
          </el-tooltip>
        </div>
      </div>
      <div class="table-wrapper">
        <el-table :data="tableData">
          <el-table-column type="selection" width="50" align="center" />
          <el-table-column prop="admin_id" label="管理员ID" align="center" width="200" />
          <el-table-column prop="username" label="用户名" align="center" />
          <el-table-column prop="role" label="角色" align="center">
            <template #default="scope">
              <el-tag
                :type="scope.row.role === 'super_admin' ? 'danger' : scope.row.role === 'editor' ? 'warning' : 'info'"
                effect="plain"
                disable-transitions
              >
                {{ roleOptions.find(r => r.value === scope.row.role)?.label || scope.row.role }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" align="center">
            <template #default="scope">
              <el-tag v-if="scope.row.is_active" type="success" effect="plain" disable-transitions>
                活跃
              </el-tag>
              <el-tag v-else type="danger" effect="plain" disable-transitions>
                禁用
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" align="center" width="160" />
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
      :title="formData.admin_id === undefined ? '新增管理员' : '修改管理员'"
      width="50%"
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px" label-position="left">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item prop="username" label="用户名">
              <el-input v-model="formData.username" placeholder="请输入用户名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="role" label="角色">
              <el-select v-model="formData.role" placeholder="请选择角色">
                <el-option
                  v-for="option in roleOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item v-if="formData.admin_id === undefined" prop="password_hash" label="密码">
          <el-input
            v-model="formData.password_hash"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item prop="is_active" label="账户状态">
          <el-switch
            v-model="formData.is_active"
            active-text="活跃"
            inactive-text="禁用"
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
