<template>
	<view class="page">
		<!-- 上部区域：未登录显示微信快捷登录，已登录显示用户信息 -->
		<view class="top-section">
			<!-- 未登录：显示微信快捷登录 -->
			<view v-if="!isLogged" class="login-card">
				<view class="login-prompt">
					<text class="prompt-text">您还未登录</text>
					<text class="prompt-desc">登录后可查看更多功能</text>
				</view>
				<button class="wx-login-btn" @click="quickLogin">
					<image src="/static/wx.png" class="wx-icon" mode="aspectFill" />
					<text class="wx-text">微信快捷登录</text>
				</button>
			</view>

			<!-- 已登录：显示用户信息卡片 + 信息完善按钮 -->
			<view v-else class="user-card">
				<view class="user-avatar-wrap">
					<image 
						:src="user.avatar_url || '/static/default-avatar.png'" 
						class="avatar" 
						mode="aspectFill"
					/>
				</view>
				<view class="user-info">
					<view class="nickname">{{ user.nickname || '微信用户' }}</view>
					<view class="phone" v-if="user.phone_number">{{ user.phone_number }}</view>
					<view class="phone no-phone" v-else>未绑定手机号</view>
				</view>
				<button class="edit-btn" @click="gotoEditProfile">
					<text class="edit-text">完善信息</text>
				</button>
			</view>
		</view>

		<!-- 下部区域：功能列表 -->
		<view class="function-list">
			<view class="list-title">功能</view>
			<button class="list-item" @click="gotoHistory">
				<view class="item-left">
					<text class="item-icon">📋</text>
					<text class="item-text">扫描历史记录</text>
				</view>
				<text class="item-arrow">›</text>
			</button>
			<button class="list-item" @click="gotoHelp">
				<view class="item-left">
					<text class="item-icon">💡</text>
					<text class="item-text">关于我们 / 帮助中心</text>
				</view>
				<text class="item-arrow">›</text>
			</button>
			<button v-if="isLogged" class="list-item logout-item" @click="logout">
				<view class="item-left">
					<text class="item-icon">🚪</text>
					<text class="item-text logout-text">退出登录</text>
				</view>
				<text class="item-arrow">›</text>
			</button>
		</view>
	</view>
</template>

<script>

import config from '@/utils/config.js';

export default {
	data() {
		return {
			user: {},
			isLogged: false
		};
	},
	onShow() {
		this.checkWeChatLogin();
	},
	methods: {
		// 修改：检查是否已登录（根据 token 判断）
		checkWeChatLogin() {
			uni.getStorage({
				key: 'token',
				success: (res) => {
					const token = res.data;
					if (token) {
						// 有 token，获取用户信息
						uni.getStorage({
							key: 'user',
							success: (userRes) => {
								this.user = userRes.data || {};
								this.isLogged = true;
							},
							fail: () => {
								// 有 token 但没有用户信息，可选择请求后端获取或清除 token
								this.user = {};
								this.isLogged = true; // 仍视为已登录
							}
						});
					} else {
						this.user = {};
						this.isLogged = false;
					}
				},
				fail: () => {
					// 没有 token，未登录
					this.user = {};
					this.isLogged = false;
				}
			});
		},

		// 修改：微信快捷登录（获取用户信息）
		quickLogin() {
			uni.showLoading({ title: '登录中...' });
			
			// 先获取用户信息
			uni.getUserProfile({
				desc: '用于完善用户资料',
				success: (userRes) => {
					const userInfo = userRes.userInfo;
					
					// 然后进行登录
					uni.login({
						provider: 'weixin',
						success: (loginRes) => {
							const code = loginRes.code || loginRes.authCode || '';
							if (!code) {
								uni.hideLoading();
								uni.showToast({ title: '获取登录凭证失败', icon: 'none' });
								return;
							}
							
							// 调用后端登录接口
							this.loginWithWechat(code, userInfo);
						},
						fail: () => {
							uni.hideLoading();
							uni.showToast({ title: '登录失败', icon: 'none' });
						}
					});
				},
				fail: () => {
					// 用户拒绝授权，尝试只用 code 登录
					uni.login({
						provider: 'weixin',
						success: (loginRes) => {
							const code = loginRes.code || loginRes.authCode || '';
							if (!code) {
								uni.hideLoading();
								uni.showToast({ title: '获取登录凭证失败', icon: 'none' });
								return;
							}
							this.loginWithWechat(code, null);
						},
						fail: () => {
							uni.hideLoading();
							uni.showToast({ title: '登录失败', icon: 'none' });
						}
					});
				}
			});
		},

		// 新增：使用 uni.request 调用后端登录接口
		loginWithWechat(code, userInfo) {
			const requestData = { code };
			
			// 如果有用户信息，添加到请求数据中
			if (userInfo) {
				requestData.nickname = userInfo.nickName;
				requestData.avatar_url = userInfo.avatarUrl;
			}
			
			uni.request({
				url: config.baseURL + '/api/login/wx',
				method: 'POST',
				header: {
					'Content-Type': 'application/json'
				},
				data: requestData,
				success: (res) => {
					uni.hideLoading();
					
					if (res.statusCode === 200 && res.data) {
						const data = res.data;
						const token = data.access_token;	
                        console.log('登录成功，返回数据:', data);					
						// 如果后端返回的用户信息中没有头像和昵称，使用前端获取的
                        this.user.phone_number = data.phone_number
						if (userInfo) {
							// 如果文件路径已经包含完整URL，直接使用；否则拼接baseURL
							if (data.avatar_url.startsWith('http')) {
								this.user.avatar_url = data.avatar_url;
							} else {
								// 确保路径以 / 开头
								if (!data.avatar_url.startsWith('/')) {
									data.avatar_url = '/' + data.avatar_url;
								}
								this.user.avatar_url = config.baseURL +'/api'+ data.avatar_url;
													
							}
							this.user.nickname = data.nickname || userInfo.nickName;
						}
						
						if (token) {
							uni.setStorage({
								key: 'token',
								data: token,
								success: () => {
									uni.setStorage({
										key: 'user',
										data: this.user,
										success: () => {
											this.isLogged = true;
											uni.showToast({ title: '登录成功', icon: 'success' });
										}
									});
								}
							});
						} else {
							const msg = data.message || data.msg || '登录失败：未返回token';
							uni.showToast({ title: msg, icon: 'none' });
						}
					} else {
						const msg = res.data?.message || res.data?.msg || '登录失败';
						uni.showToast({ title: msg, icon: 'none' });
					}
				},
				fail: (err) => {
					uni.hideLoading();
					console.error('登录请求失败:', err);
					uni.showToast({ title: '网络请求失败', icon: 'none' });
				}
			});
		},

		// 跳转到信息完善页面
		gotoEditProfile() {
			uni.navigateTo({ url: '/pages/my/edit-profile' });
		},

		gotoHistory() {
			// 跳转到扫描历史记录页面
			uni.navigateTo({ url: '/pages/scan/scanhistory' });
		},
		
		gotoHelp() {
			uni.showModal({ title: '关于我们', content: '请联系管理员获取帮助。', showCancel: false });
		},
		
		logout() {
			uni.showModal({
				content: '确定要退出登录吗？',
				success: (res) => {
					if (res.confirm) {
						// 清除 token 和用户信息
						uni.removeStorage({ key: 'token' });
						uni.removeStorage({ key: 'user' });
						uni.showToast({ title: '已退出', icon: 'none' });
						this.user = {};
						this.isLogged = false;
					}
				}
			});
		},
        
	}
};
</script>

<style scoped>
.page { 
	min-height: 100vh; 
	background: #f5f5f7; 
}

/* 上部区域 */
.top-section { 
	padding: 20rpx; 
	margin-bottom: 20rpx; 
}

/* 未登录状态：登录卡片 */
.login-card { 
	background: #fff; 
	border-radius: 16rpx; 
	padding: 60rpx 40rpx; 
	display: flex; 
	flex-direction: column; 
	align-items: center; 
	box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06); 
}

.login-prompt { 
	text-align: center; 
	margin-bottom: 40rpx; 
}

.prompt-text { 
	display: block; 
	font-size: 36rpx; 
	font-weight: 600; 
	color: #333; 
	margin-bottom: 12rpx; 
}

.prompt-desc { 
	display: block; 
	font-size: 28rpx; 
	color: #999; 
}

.wx-login-btn { 
	display: flex; 
	align-items: center; 
	gap: 16rpx; 
	padding: 24rpx 60rpx; 
	background: #88928d; 
	color: #fff; 
	border-radius: 48rpx; 
	border: none; 
	box-shadow: 0 4rpx 12rpx rgba(7,193,96,0.3); 
}

.wx-icon { 
	width: 80rpx; 
	height: 80rpx; 
}

.wx-text { 
	color: #fff; 
	font-weight: 600; 
	font-size: 32rpx; 
}

/* 已登录状态：用户信息卡片 */
.user-card { 
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
	border-radius: 16rpx; 
	padding: 40rpx; 
	display: flex; 
	align-items: center; 
	box-shadow: 0 4rpx 20rpx rgba(102,126,234,0.3); 
	position: relative; 
}

.user-avatar-wrap { 
	margin-right: 24rpx; 
}

.avatar { 
	width: 120rpx; 
	height: 120rpx; 
	border-radius: 60rpx; 
	border: 4rpx solid rgba(255,255,255,0.3); 
}

.user-info { 
	flex: 1; 
}

.nickname { 
	font-size: 36rpx; 
	font-weight: 700; 
	color: #fff; 
	margin-bottom: 8rpx; 
}

.phone { 
	font-size: 26rpx; 
	color: rgba(255,255,255,0.8); 
}

.no-phone { 
	color: rgba(255,255,255,0.6); 
	font-style: italic; 
}

.edit-btn { 
	padding: 16rpx 32rpx; 
	background: rgba(255,255,255,0.2); 
	border: 2rpx solid rgba(255,255,255,0.5); 
	border-radius: 40rpx; 
	backdrop-filter: blur(10rpx); 
}

.edit-text { 
	color: #fff; 
	font-size: 28rpx; 
	font-weight: 500; 
}

/* 下部区域：功能列表 */
.function-list { 
	padding: 0 20rpx; 
}

.list-title { 
	font-size: 28rpx; 
	color: #999; 
	padding: 20rpx 24rpx 16rpx; 
	font-weight: 500; 
}

.list-item { 
	background: #fff; 
	padding: 32rpx 24rpx; 
	margin-bottom: 16rpx; 
	border-radius: 16rpx; 
	display: flex; 
	align-items: center; 
	justify-content: space-between; 
	box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); 
	text-align: left; 
}

.item-left { 
	display: flex; 
	align-items: center; 
	gap: 20rpx; 
}

.item-icon { 
	font-size: 40rpx; 
}

.item-text { 
	font-size: 32rpx; 
	color: #333; 
	font-weight: 500; 
}

.item-arrow { 
	font-size: 48rpx; 
	color: #ccc; 
	font-weight: 300; 
}

.logout-item { 
	border: 2rpx solid #ff3b30; 
	background: #fff; 
}

.logout-text { 
	color: #ff3b30; 
}
.item-text { 
	font-size: 32rpx; 
	color: #333; 
	font-weight: 500; 
}

.item-arrow { 
	font-size: 48rpx; 
	color: #ccc; 
	font-weight: 300; 
}

.logout-item { 
	border: 2rpx solid #ff3b30; 
	background: #fff; 
}

.logout-text { 
	color: #ff3b30; 
}
</style>
