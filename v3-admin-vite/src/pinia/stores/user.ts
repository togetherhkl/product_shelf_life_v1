import { getCurrentUserApi } from "@@/apis/users"
import { setToken as _setToken, getToken, removeToken } from "@@/utils/cache/cookies"
import { pinia } from "@/pinia"
import { resetRouter } from "@/router"
import { routerConfig } from "@/router/config"
import { useSettingsStore } from "./settings"
import { useTagsViewStore } from "./tags-view"

export const useUserStore = defineStore("user", () => {
  const token = ref<string>(getToken() || "")

  const roles = ref<string[]>([])

  const username = ref<string>("")

  const tagsViewStore = useTagsViewStore()

  const settingsStore = useSettingsStore()

  // 设置 Token
  const setToken = (value: string) => {
    _setToken(value)
    token.value = value
  }

  // 设置登录信息
  const setLoginInfo = (tokenValue: string, usernameValue: string, roleValue: string) => {
    _setToken(tokenValue)
    token.value = tokenValue
    username.value = usernameValue
    // 将角色字符串转换为数组
    roles.value = roleValue ? [roleValue] : routerConfig.defaultRoles
  }

  // 获取用户详情
  const getInfo = async () => {
    try {
      const data = await getCurrentUserApi()
      // console.log("用户详情", data)
      username.value = data.username
      // console.log("用户角色", data.role)
      // 验证返回的 role 是否为字符串，否则塞入一个没有任何作用的默认角色，防止路由守卫逻辑进入无限循环
      roles.value = data.role ? [data.role] : routerConfig.defaultRoles
    } catch (error) {
      console.error("获取用户详情失败", error)
    }
  }

  // 模拟角色变化
  const changeRoles = (role: string) => {
    const newToken = `token-${role}`
    token.value = newToken
    _setToken(newToken)
    // 用刷新页面代替重新登录
    location.reload()
  }

  // 登出
  const logout = () => {
    removeToken()
    token.value = ""
    roles.value = []
    resetRouter()
    resetTagsView()
  }

  // 重置 Token
  const resetToken = () => {
    removeToken()
    token.value = ""
    roles.value = []
  }

  // 重置 Visited Views 和 Cached Views
  const resetTagsView = () => {
    if (!settingsStore.cacheTagsView) {
      tagsViewStore.delAllVisitedViews()
      tagsViewStore.delAllCachedViews()
    }
  }

  return { token, roles, username, setToken, setLoginInfo, getInfo, changeRoles, logout, resetToken }
})

/**
 * @description 在 SPA 应用中可用于在 pinia 实例被激活前使用 store
 * @description 在 SSR 应用中可用于在 setup 外使用 store
 */
export function useUserStoreOutside() {
  return useUserStore(pinia)
}
