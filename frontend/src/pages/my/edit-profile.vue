<template>
	<view class="page">
		<!-- 加载状态 -->
		<view class="loading-overlay" v-if="loading">
			<view class="loading-content">
				<view class="loading-spinner"></view>
				<text class="loading-text">加载用户信息中...</text>
			</view>
		</view>

		<!-- 顶部标题栏 -->
		<!-- <view class="header">
			<button class="back-btn" @click="goBack">
				<text class="back-icon">‹</text>
			</button>
			<text class="header-title">完善个人信息</text>
			<view class="placeholder"></view>
		</view> -->

		<!-- 头像区域 -->
		<view class="avatar-section">
			<view class="avatar-card">
				<view class="avatar-wrap" @click="chooseAvatar">
					<image 
						:src="formData.avatar_url || '/static/default-avatar.png'" 
						class="avatar" 
						mode="aspectFill"
					/>
					<view class="avatar-edit-overlay">
						<text class="camera-icon">📷</text>
					</view>
				</view>
				<text class="avatar-tip">点击更换头像</text>
			</view>
		</view>

		<!-- 微信信息授权卡片 -->
		<view class="auth-section" v-if="!hasWxInfo">
			<view class="auth-card">
				<view class="auth-icon">👤</view>
				<view class="auth-content">
					<text class="auth-title">获取微信信息</text>
					<text class="auth-desc">获取您的微信昵称和头像，让资料更完整</text>
				</view>
				<button class="auth-btn" open-type="getUserInfo" @getuserinfo="onGetUserInfo">
					<text class="auth-btn-text">授权获取</text>
				</button>
			</view>
		</view>

		<!-- 表单区域 -->
		<view class="form-section">
			<view class="form-group">
				<text class="form-label">昵称</text>
				<input 
					class="form-input" 
					v-model="formData.nickname" 
					placeholder="请输入昵称"
					maxlength="20"
				/>
			</view>

			<view class="form-group">
				<text class="form-label">手机号</text>
				<input 
					class="form-input" 
					v-model="formData.phone_number" 
					placeholder="请输入手机号"
					type="number"
					maxlength="11"
				/>
			</view>

			<view class="form-group">
				<text class="form-label">邮箱</text>
				<input 
					class="form-input" 
					v-model="formData.email" 
					placeholder="请输入邮箱"
					type="text"
				/>
			</view>

			<view class="form-group textarea-group">
				<text class="form-label">个人简介</text>
				<textarea 
					class="form-textarea" 
					v-model="formData.introduction" 
					placeholder="介绍一下自己吧..."
					maxlength="200"
					:show-count="true"
				/>
			</view>
		</view>

		<!-- 底部按钮 -->
		<view class="bottom-section">
			<button class="save-btn" @click="saveProfile" :disabled="saving">
				<text class="save-btn-text">{{ saving ? '保存中...' : '保存' }}</text>
			</button>
		</view>
	</view>
</template>

<script>
import config from '@/utils/config.js';

export default {
	data() {
		return {
			formData: {
				nickname: '',
				avatar_url: '',
				phone_number: '',
				email: '',
				introduction: '',
				upoload_avatar_url: '' // 标记头像是否已上传
			},
			hasWxInfo: false,
			saving: false,
			loading: false // 添加加载状态
		};
	},
	onLoad() {
		// 页面加载时立即获取用户信息
		this.fetchUserInfo();
	},
	methods: {
		// 优先从后端获取用户信息
		async fetchUserInfo() {
			this.loading = true;
			
			try {
				// 检查是否有 token
				const token = await this.getToken();
				
				if (token) {
					console.log('Token 存在，从后端获取用户信息');
					// 有 token，从后端获取最新用户信息
					const response = await uni.request({
                        url: config.baseURL + '/api/user/me',
                        method: 'GET',
                        header: {
                            'Authorization': 'Bearer ' + token, 
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (response.statusCode === 200) {
                        const userData = response.data;
                        console.log('后端用户信息:', userData);
                        
                        this.updateFormData(userData);
                        this.hasWxInfo = !!(userData.nickname || userData.avatar_url);
                        
                        // 更新本地存储的用户信息
                        uni.setStorage({
                            key: 'user',
                            data: userData
                        });
                        
                        uni.showToast({ 
                            title: '用户信息加载成功', 
                            icon: 'success',
                            duration: 1500
                        });
                    } else {
                        console.error('API 请求失败，状态码:', response.statusCode);
                        throw new Error(`API 请求失败: ${response.statusCode}`);
                    }
				} else {
					console.log('无 Token，使用本地存储');
					// 没有 token，使用本地存储的用户信息
					this.loadLocalUserInfo();
				}
			} catch (error) {
				console.error('获取用户信息失败:', error);
				// 接口请求失败，降级使用本地存储的用户信息
				this.loadLocalUserInfo();
				uni.showToast({ 
					title: '网络异常，使用本地数据', 
					icon: 'none',
					duration: 2000
				});
			} finally {
				this.loading = false;
			}
		},

		// 获取 Token 的 Promise 包装
		getToken() {
			return new Promise((resolve) => {
				uni.getStorage({
					key: 'token',
					success: (res) => {
						const token = res.data;
						resolve(token);
					},
					fail: (err) => {
						resolve(null);
					}
				});
			});
		},

		// 更新表单数据
		updateFormData(userData) {
			this.formData = {
				nickname: userData.nickname || '',
				avatar_url: userData.avatar_url || '',
				phone_number: userData.phone_number || '',
				email: userData.email || '',
				introduction: userData.introduction || ''
			};
		},

		// 加载用户信息（保留原方法作为兼容）
		loadUserInfo() {
			this.fetchUserInfo();
		},

		// 降级方案：从本地存储加载用户信息
		loadLocalUserInfo() {
			uni.getStorage({
				key: 'user',
				success: (res) => {
					const user = res.data || {};
					this.updateFormData({
						nickname: user.nickname || '',
						avatar_url: user.avatar_url || user.avatar || '',
						phone_number: user.phone_number || user.phone || '',
						email: user.email || '',
						introduction: user.introduction || ''
					});
					this.hasWxInfo = !!(user.nickname || user.avatar_url || user.avatar);
					
					if (Object.keys(user).length > 0) {
						uni.showToast({ 
							title: '已加载本地数据', 
							icon: 'none',
							duration: 1500
						});
					}
				},
				fail: () => {
					// 如果本地也没有用户信息，使用空值
					this.updateFormData({
						nickname: '',
						avatar_url: '',
						phone_number: '',
						email: '',
						introduction: ''
					});
					this.hasWxInfo = false;
				}
			});
		},

		// 获取微信用户信息授权
		onGetUserInfo(e) {
			const userInfo = e.detail.userInfo;
			if (userInfo) {
				this.formData.nickname = userInfo.nickName || this.formData.nickname;
				this.formData.avatar_url = userInfo.avatarUrl || this.formData.avatar_url;
				this.hasWxInfo = true;
				uni.showToast({ title: '信息获取成功', icon: 'success' });
			} else {
				uni.showToast({ title: '授权失败', icon: 'none' });
			}
		},

		// 选择头像
		chooseAvatar() {
			uni.chooseImage({
				count: 1,
				sizeType: ['compressed'],
				sourceType: ['album', 'camera'],
				success: (res) => {
					const tempFilePath = res.tempFilePaths[0];
					this.uploadAvatar(tempFilePath);
				}
			});
		},

		// 上传头像
		async uploadAvatar(filePath) {
			uni.showLoading({ title: '上传中...' });
			
			try {
				// 获取 token
				const token = await this.getToken();
				
				// 使用 uni.uploadFile 上传文件
				const uploadResult = await new Promise((resolve, reject) => {
					uni.uploadFile({
						url: config.baseURL + '/api/uploads?file_type=images',
						filePath: filePath,
						name: 'files',
						header: {
							'Authorization': token ? 'Bearer ' + token : ''
						},
						success: (res) => {
							console.log('上传响应:', res);
							
							try {
								// 检查状态码
								if (res.statusCode !== 200) {
									reject(new Error(`HTTP状态码错误: ${res.statusCode}`));
									return;
								}
								
								// 解析返回的数据
								let data;
								if (typeof res.data === 'string') {
									data = JSON.parse(res.data);
								} else {
									data = res.data;
								}
								
								// 检查业务状态码
								if (data.status_code === 200) {
									resolve(data);
								} else {
									const errorMsg = data.detail || data.message || '上传失败';
									reject(new Error(errorMsg));
								}
							} catch (parseError) {
								reject(new Error('服务器响应格式错误'));
							}
						},
						fail: (error) => {
							reject(new Error('网络请求失败'));
						}
					});
				});

				// 上传成功，更新头像URL
				if (uploadResult.file_paths && uploadResult.file_paths.length > 0) {
					// 取第一个上传成功的文件路径
					let uploadedFilePath = uploadResult.file_paths[0];
					
					// 处理反斜杠问题：将反斜杠替换为正斜杠
					uploadedFilePath = uploadedFilePath.replace(/\\/g, '/');
					
					console.log('处理后的文件路径:', uploadedFilePath);
					
					// 如果文件路径已经包含完整URL，直接使用；否则拼接baseURL
					if (uploadedFilePath.startsWith('http')) {
						this.formData.avatar_url = uploadedFilePath;
					} else {
						// 确保路径以 / 开头
						if (!uploadedFilePath.startsWith('/')) {
							uploadedFilePath = '/' + uploadedFilePath;
						}
						this.formData.avatar_url = config.baseURL +'/api'+ uploadedFilePath;
						this.formData.upoload_avatar_url = uploadedFilePath; // 标记头像已上传
					}
					
					// console.log('最终头像URL:', this.formData.avatar_url);
					
					uni.hideLoading();
					uni.showToast({ 
						title: '头像上传成功', 
						icon: 'success',
						duration: 2000
					});
				} else {
					throw new Error('上传成功但未返回文件路径');
				}
				
			} catch (error) {
				uni.hideLoading();
				console.error('头像上传失败:', error);
				
				// 显示具体的错误信息
				let errorMsg = '头像上传失败';
				if (error && typeof error === 'object') {
					if (error.message) {
						errorMsg = error.message;
					} else if (error.errMsg) {
						errorMsg = error.errMsg;
					}
				} else if (typeof error === 'string') {
					errorMsg = error;
				}
				
				uni.showToast({ 
					title: errorMsg, 
					icon: 'none',
					duration: 3000
				});
			}
		},

		// 表单验证
		validateForm() {
			if (!this.formData.nickname || this.formData.nickname.trim() === '') {
				uni.showToast({ title: '请输入昵称', icon: 'none' });
				return false;
			}

			if (this.formData.phone_number && !/^1[3-9]\d{9}$/.test(this.formData.phone_number)) {
				uni.showToast({ title: '手机号格式不正确', icon: 'none' });
				return false;
			}

			if (this.formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.formData.email)) {
				uni.showToast({ title: '邮箱格式不正确', icon: 'none' });
				return false;
			}

			return true;
		},

		// 保存用户信息
		async saveProfile() {
			if (!this.validateForm()) return;

			this.saving = true;
			
			// 构建提交数据，只包含有值的字段
			const submitData = {};
			Object.keys(this.formData).forEach(key => {
				const value = this.formData[key];
				if (value !== null && value !== undefined && value !== '') {
					submitData[key] = value;
				}
				// 上传图像时不需要前端拼接完整URL，后端会处理
				submitData['avatar_url'] =  this.formData.upoload_avatar_url;
			});

			try {
				// 获取 token
				const token = await this.getToken();
				
				// 使用 uni.request 调用后端 API
				const response = await uni.request({
					url: config.baseURL + '/api/user/me',
					method: 'PUT',
					header: {
						'Authorization': token ? 'Bearer ' + token : '',
						'Content-Type': 'application/json'
					},
					data: submitData
				});

				if (response.statusCode === 200) {
					// 更新本地存储的用户信息
					uni.getStorage({
						key: 'user',
						success: (res) => {
							const user = res.data || {};
							const updatedUser = { ...user, ...submitData };
							uni.setStorage({
								key: 'user',
								data: updatedUser,
								success: () => {
									uni.showToast({ title: '保存成功', icon: 'success' });
									setTimeout(() => {
										uni.navigateBack();
									}, 1500);
								}
							});
						},
						fail: () => {
							uni.setStorage({
								key: 'user',
								data: submitData,
								success: () => {
									uni.showToast({ title: '保存成功', icon: 'success' });
									setTimeout(() => {
										uni.navigateBack();
									}, 1500);
								}
							});
						}
					});
				} else {
					const errorMsg = response.data?.message || response.data?.msg || '保存失败';
					uni.showToast({ title: errorMsg, icon: 'none' });
				}
			} catch (error) {
				console.error('保存用户信息失败:', error);
				uni.showToast({ title: '网络错误，保存失败', icon: 'none' });
			} finally {
				this.saving = false;
			}
		},

		// 返回上一页
		goBack() {
			uni.navigateBack();
		}
	}
};
</script>

<style scoped>
.page {
	min-height: 100vh;
	background: #f5f5f7;
	padding-bottom: 120rpx;
}

/* 顶部标题栏 */
.header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 20rpx 20rpx 10rpx;
	background: #fff;
	border-bottom: 1rpx solid #f0f0f0;
}

.back-btn {
	width: 80rpx;
	height: 80rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	background: none;
	border: none;
	padding: 0;
    margin-left: 0;
    margin-right: 0;
}

.back-icon {
	font-size: 48rpx;
	color: #333;
	font-weight: 300;
}

.header-title {
	font-size: 36rpx;
	font-weight: 600;
	color: #333;
}

.placeholder {
	width: 80rpx;
}

/* 头像区域 */
.avatar-section {
	padding: 40rpx 20rpx;
}

.avatar-card {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	border-radius: 20rpx;
	padding: 60rpx 40rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
	box-shadow: 0 8rpx 30rpx rgba(102,126,234,0.3);
}

.avatar-wrap {
	position: relative;
	margin-bottom: 20rpx;
}

.avatar {
	width: 160rpx;
	height: 160rpx;
	border-radius: 80rpx;
	border: 6rpx solid rgba(255,255,255,0.3);
}

.avatar-edit-overlay {
	position: absolute;
	bottom: 0;
	right: 0;
	width: 60rpx;
	height: 60rpx;
	background: rgba(255,255,255,0.9);
	border-radius: 30rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	backdrop-filter: blur(10rpx);
}

.camera-icon {
	font-size: 32rpx;
}

.avatar-tip {
	color: rgba(255,255,255,0.8);
	font-size: 28rpx;
}

/* 微信授权区域 */
.auth-section {
	padding: 0 20rpx 20rpx;
}

.auth-card {
	background: #fff;
	border-radius: 16rpx;
	padding: 40rpx;
	display: flex;
	align-items: center;
	box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.08);
}

.auth-icon {
	font-size: 60rpx;
	margin-right: 24rpx;
}

.auth-content {
	flex: 1;
}

.auth-title {
	display: block;
	font-size: 32rpx;
	font-weight: 600;
	color: #333;
	margin-bottom: 8rpx;
}

.auth-desc {
	display: block;
	font-size: 26rpx;
	color: #666;
}

.auth-btn {
	padding: 20rpx 32rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	border-radius: 40rpx;
	border: none;
}

.auth-btn-text {
	color: #fff;
	font-size: 28rpx;
	font-weight: 500;
}

/* 表单区域 */
.form-section {
	padding: 0 20rpx;
}

.form-group {
	background: #fff;
	border-radius: 16rpx;
	padding: 32rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06);
}

.form-label {
	display: block;
	font-size: 32rpx;
	font-weight: 600;
	color: #333;
	margin-bottom: 20rpx;
}

.form-input {
	width: 100%;
	font-size: 30rpx;
	color: #333;
	padding: 24rpx 0;
	border-bottom: 2rpx solid #f0f0f0;
}

.form-input::placeholder {
	color: #999;
}

.textarea-group {
	min-height: 200rpx;
}

.form-textarea {
	width: 100%;
	min-height: 160rpx;
	font-size: 30rpx;
	color: #333;
	padding: 20rpx 0;
	border: none;
	resize: none;
}

.form-textarea::placeholder {
	color: #999;
}

/* 底部按钮 */
.bottom-section {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	padding: 30rpx 20rpx;
	background: #fff;
	border-top: 1rpx solid #f0f0f0;
	box-shadow: 0 -4rpx 20rpx rgba(0,0,0,0.08);
}

.save-btn {
	width: 100%;
	height: 100rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	border-radius: 50rpx;
	border: none;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 8rpx 25rpx rgba(102,126,234,0.4);
}

.save-btn[disabled] {
	opacity: 0.6;
}

.save-btn-text {
	color: #fff;
	font-size: 36rpx;
	font-weight: 600;
}

/* 加载状态样式 */
.loading-overlay {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(245, 245, 247, 0.9);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 9999;
	backdrop-filter: blur(10rpx);
}

.loading-content {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 60rpx;
	background: #fff;
	border-radius: 20rpx;
	box-shadow: 0 8rpx 30rpx rgba(0,0,0,0.1);
}

.loading-spinner {
	width: 80rpx;
	height: 80rpx;
	border: 6rpx solid #f3f3f3;
	border-top: 6rpx solid #667eea;
	border-radius: 50%;
	animation: spin 1s linear infinite;
	margin-bottom: 30rpx;
}

@keyframes spin {
	0% { transform: rotate(0deg); }
	100% { transform: rotate(360deg); }
}

.loading-text {
	font-size: 28rpx;
	color: #666;
	font-weight: 500;
}
</style>
