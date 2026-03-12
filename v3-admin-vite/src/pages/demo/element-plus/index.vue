<script lang="ts" setup>
import type { CreateOrUpdateUserRequestData, UserData } from "@@/apis/users/type"
import type { FormRules } from "element-plus"
import { createUserApi, deleteUserApi, getUserListApi, updateUserApi } from "@@/apis/users"
import { usePagination } from "@@/composables/usePagination"
import { CirclePlus, Delete, Download, Refresh, RefreshRight, Search } from "@element-plus/icons-vue"
import { cloneDeep } from "lodash-es"

defineOptions({
  // 命名当前组件
  name: "UserManagement"
})

const loading = ref<boolean>(false)

const { paginationData, handleCurrentChange, handleSizeChange } = usePagination()

// #region 增
const DEFAULT_FORM_DATA: CreateOrUpdateUserRequestData = {
  user_id: undefined,
  openid: "",
  nickname: "",
  avatar_url: "",
  phone_number: "",
  email: "",
  introduction: "",
  is_active: true
}

const dialogVisible = ref<boolean>(false)

const formRef = useTemplateRef("formRef")

const formData = ref<CreateOrUpdateUserRequestData>(cloneDeep(DEFAULT_FORM_DATA))

const formRules: FormRules<CreateOrUpdateUserRequestData> = {
  nickname: [{ required: true, trigger: "blur", message: "请输入昵称" }],
  openid: [{ required: true, trigger: "blur", message: "请输入微信openid" }],
  email: [
    { type: "email", trigger: "blur", message: "请输入正确的邮箱格式" }
  ],
  phone_number: [
    { pattern: /^1[3-9]\d{9}$/, trigger: "blur", message: "请输入正确的手机号格式" }
  ]
}

function handleCreateOrUpdate() {
  formRef.value?.validate((valid) => {
    if (!valid) {
      ElMessage.error("表单校验不通过")
      return
    }
    loading.value = true
    const api = formData.value.user_id === undefined ? createUserApi : updateUserApi
    api(formData.value).then(() => {
      ElMessage.success("操作成功")
      dialogVisible.value = false
      getUserData()
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
function handleDelete(row: UserData) {
  ElMessageBox.confirm(`正在删除用户：${row.nickname}，确认删除？`, "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning"
  }).then(() => {
    deleteUserApi(row.user_id).then(() => {
      ElMessage.success("删除成功")
      getUserData()
    })
  })
}
// #endregion

// #region 改
function handleUpdate(row: UserData) {
  dialogVisible.value = true
  formData.value = cloneDeep(row)
}
// #endregion

// #region 查
const tableData = ref<UserData[]>([])

const searchFormRef = useTemplateRef("searchFormRef")

const searchData = reactive({
  nickname: "",
  phone_number: "",
  email: "",
  openid: ""
})

function getUserData() {
  loading.value = true
  getUserListApi({
    skip: (paginationData.currentPage - 1) * paginationData.pageSize,
    limit: paginationData.pageSize,
    nickname: searchData.nickname,
    phone_number: searchData.phone_number,
    email: searchData.email,
    openid: searchData.openid
  }).then((data) => {
    console.log("用户列表", data)
    // 根据后端接口返回的是用户数组，需要适配分页组件
    tableData.value = data
    paginationData.total = data.length // 这里需要根据实际后端接口调整
  }).catch(() => {
    tableData.value = []
  }).finally(() => {
    loading.value = false
  })
}

function handleSearch() {
  paginationData.currentPage === 1 ? getUserData() : (paginationData.currentPage = 1)
}

function resetSearch() {
  searchFormRef.value?.resetFields()
  handleSearch()
}
// #endregion

// 监听分页参数的变化
watch([() => paginationData.currentPage, () => paginationData.pageSize], getUserData, { immediate: true })
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
        <el-form-item prop="nickname" label="昵称">
          <el-input v-model="searchData.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item prop="phone_number" label="手机号">
          <el-input v-model="searchData.phone_number" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item prop="email" label="邮箱">
          <el-input v-model="searchData.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item prop="openid" label="微信openid">
          <el-input v-model="searchData.openid" placeholder="请输入微信openid" />
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
            新增用户
          </el-button>
          <el-button type="danger" :icon="Delete">
            批量删除
          </el-button>
        </div>
        <div>
          <el-tooltip content="下载">
            <el-button type="primary" :icon="Download" circle />
          </el-tooltip>
          <el-tooltip content="刷新当前页">
            <el-button type="primary" :icon="RefreshRight" circle @click="getUserData" />
          </el-tooltip>
        </div>
      </div>
      <div class="table-wrapper">
        <el-table :data="tableData">
          <el-table-column type="selection" width="50" align="center" />
          <el-table-column prop="nickname" label="昵称" align="center" />
          <el-table-column prop="openid" label="微信openid" align="center" width="200" />
          <el-table-column prop="avatar_url" label="头像" align="center" width="80">
            <template #default="scope">
              <el-avatar v-if="scope.row.avatar_url" :src="scope.row.avatar_url" size="small" />
              <el-avatar v-else size="small">
                {{ scope.row.nickname?.charAt(0) || 'U' }}
              </el-avatar>
            </template>
          </el-table-column>
          <el-table-column prop="phone_number" label="手机号" align="center" />
          <el-table-column prop="email" label="邮箱" align="center" />
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
          <el-table-column prop="created_at" label="注册时间" align="center" width="160" />
          <el-table-column prop="last_login_at" label="最后登录" align="center" width="160">
            <template #default="scope">
              {{ scope.row.last_login_at || '从未登录' }}
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
      :title="formData.user_id === undefined ? '新增用户' : '修改用户'"
      width="50%"
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px" label-position="left">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item prop="nickname" label="昵称">
              <el-input v-model="formData.nickname" placeholder="请输入昵称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="openid" label="微信openid">
              <el-input v-model="formData.openid" placeholder="请输入微信openid" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item prop="phone_number" label="手机号">
              <el-input v-model="formData.phone_number" placeholder="请输入手机号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="email" label="邮箱">
              <el-input v-model="formData.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item prop="avatar_url" label="头像URL">
          <el-input v-model="formData.avatar_url" placeholder="请输入头像URL" />
        </el-form-item>
        <el-form-item prop="introduction" label="个人介绍">
          <el-input
            v-model="formData.introduction"
            type="textarea"
            placeholder="请输入个人介绍"
            :rows="3"
            maxlength="500"
            show-word-limit
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
