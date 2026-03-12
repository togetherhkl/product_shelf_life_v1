<template>
	<view class="page">
		
		<!-- 摄像头预览区域 -->
		<view class="camera-section">
			<view class="camera-container">
				<camera 
					class="camera" 
					device-position="back" 
					@error="onCameraError"
					@initdone="onCameraReady"
				/>
				
				<!-- 扫码框 -->
				<view class="scan-overlay">
					<view class="scan-box">
						<view class="corner corner-tl"></view>
						<view class="corner corner-tr"></view>
						<view class="corner corner-bl"></view>
						<view class="corner corner-br"></view>
						<view class="scan-line" :class="{ scanning: isScanning }"></view>
					</view>
				</view>
				
				<!-- 提示文字 -->
				<view class="scan-tip">
					<text class="tip-text">将条形码放入框内进行扫描</text>
				</view>
			</view>
		</view>

		<!-- 操作按钮区域 -->
		<view class="controls-section">
			<view class="scan-info">
				<view class="info-card">
					<text class="info-icon">📱</text>
					<text class="info-text">对准商品条形码，点击扫描按钮</text>
				</view>
			</view>
			
			<button 
				class="scan-btn" 
				:class="{ scanning: isScanning }" 
				@click="doScan"
				:disabled="isScanning"
			>
				<text class="scan-btn-text">
					{{ isScanning ? '扫描中...' : '开始扫描' }}
				</text>
			</button>
			
			<!-- 手动输入选项 -->
			<button class="manual-btn" @click="showManualInput">
				<text class="manual-text">手动输入条码</text>
			</button>
		</view>

		<!-- 手动输入弹窗 -->
		<view class="modal-overlay" v-if="showModal" @click="hideModal">
			<view class="modal-content" @click.stop>
				<view class="modal-header">
					<text class="modal-title">手动输入条码</text>
					<button class="modal-close" @click="hideModal">×</button>
				</view>
				<view class="modal-body">
					<input 
						class="barcode-input" 
						v-model="manualBarcode" 
						placeholder="请输入商品条码"
						type="text"
					/>
				</view>
				<view class="modal-footer">
					<button class="modal-cancel" @click="hideModal">取消</button>
					<button class="modal-confirm" @click="searchByManualCode">确认</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import config from '@/utils/config.js';

export default {
	data() {
		return {
			isScanning: false,
			showModal: false,
			manualBarcode: '',
			cameraReady: false,
            scanCodeMsg: ''
		};
	},
	onLoad() {
		// 页面加载完成后的初始化
		this.initPage();
	},
	methods: {
		initPage() {
			// 检查摄像头权限
			uni.authorize({
				scope: 'scope.camera',
				success: () => {
					console.log('摄像头权限已授权');
				},
				fail: () => {
					uni.showModal({
						title: '权限申请',
						content: '需要摄像头权限进行扫码，请允许授权',
						success: (res) => {
							if (res.confirm) {
								uni.openSetting();
							}
						}
					});
				}
			});
		},

		// 摄像头准备就绪
		onCameraReady() {
			this.cameraReady = true;
			console.log('摄像头已准备就绪');
		},

		// 摄像头错误处理
		onCameraError(e) {
			console.error('摄像头错误:', e);
			uni.showToast({
				title: '摄像头启动失败',
				icon: 'none',
				duration: 2000
			});
		},

		// 执行扫码
		doScan() {
			if (this.isScanning) return;
			
			this.isScanning = true;
			
			uni.scanCode({
				onlyFromCamera: false,
				scanType: ['barCode'], // 只扫描条形码
				success: (res) => {
					console.log('扫码结果:', res);
					const code = res.result || res.code;
					console.log('扫码成功:', code);
					
					// 震动反馈
					uni.vibrateShort();
					
					// 查询商品信息
					this.searchProduct(code);
				},
				fail: (err) => {
					console.error('扫码失败:', err);
					uni.showModal({
						title: '扫码失败',
						content: '无法识别条码，请重新尝试或手动输入',
						showCancel: false
					});
				},
				complete: () => {
					this.isScanning = false;
				}
			});
		},

		// 查询商品信息
		async searchProduct(barcode) {
			if (!barcode) {
				uni.showToast({ title: '条码不能为空', icon: 'none' });
				return;
			}

			uni.showLoading({ title: '查询商品信息中...' });
			
			try {
				// 获取 token
				const token = await this.getToken();
				
				// 调用后端API查询商品信息
				const response = await uni.request({
					url: config.baseURL + `/api/product/barcode/${barcode}`,
					method: 'GET',
					header: {
						'Authorization': token ? 'Bearer ' + token : '',
						'Content-Type': 'application/json'
					}
				});

				uni.hideLoading();
				console.log('商品查询响应:', response);

				if (response.statusCode === 200 && response.data) {
					// 找到商品，显示商品信息并跳转
					const product = response.data;
					this.showProductInfo(product, barcode);
				} else if (response.statusCode === 404) {
					// 未找到商品
					this.showNotFoundDialog(barcode);
				} else {
					throw new Error('查询失败');
				}
			} catch (error) {
				uni.hideLoading();
				console.error('查询商品失败:', error);
				
				if (error.message && error.message.includes('404')) {
					this.showNotFoundDialog(barcode);
				} else {
					uni.showModal({
						title: '查询失败',
						content: '网络异常，请检查网络连接后重试',
						showCancel: false
					});
				}
			}
		},

		// 显示商品信息
		showProductInfo(product, barcode) {
			// 格式化日期显示
			const formatDate = (dateStr) => {
				if (!dateStr) return '未知';
				try {
					const date = new Date(dateStr);
					return date.toLocaleDateString('zh-CN');
				} catch (e) {
					return dateStr;
				}
			};

			// 计算到期状态
			const getExpireStatus = (expireDate) => {
				if (!expireDate) return '未知';
				
				const now = new Date();
				const expire = new Date(expireDate);
				const diffDays = Math.ceil((expire - now) / (1000 * 60 * 60 * 24));
				
				if (diffDays < 0) {
					return `已过期 ${Math.abs(diffDays)} 天`;
				} else if (diffDays === 0) {
					return '今日到期';
				} else if (diffDays <= 7) {
					return `${diffDays} 天后到期`;
				} else {
					return `还有 ${diffDays} 天到期`;
				}
			};

			const productInfo = `
商品名称：${product.name || '未知'}
条形码：${product.barcode_or_qr || barcode}
品牌：${product.brand || '未知'}
生产日期：${formatDate(product.production_date)}
到期日期：${formatDate(product.expiration_date)}
到期状态：${getExpireStatus(product.expiration_date)}
批次：${product.batch_number || '未知'}
描述：${product.description || '未知'}
			`.trim();

			uni.showModal({
				title: '商品信息',
				content: productInfo,
				confirmText: '查看详情',
				cancelText: '继续扫码',
				success: (res) => {
					if (res.confirm) {
						// 跳转到商品详情页
						uni.navigateTo({ 
							url: `/pages/product/detail?barcode=${barcode}` 
						});
					}
					// 如果点击继续扫码，什么也不做，用户可以继续扫描
				}
			});

			// 保存扫描历史
			this.saveScanHistory(product, barcode);
		},

		// 保存扫描历史
		saveScanHistory(product, barcode) {
			try {
				// 获取现有的扫描历史
				uni.getStorage({
					key: 'scanHistory',
					success: (res) => {
						let history = res.data || [];
						
						// 添加新的扫描记录
						const newRecord = {
							id: Date.now(), // 使用时间戳作为ID
							barcode: barcode,
							product: product,
							scanTime: new Date().toISOString(),
							timestamp: Date.now()
						};
						
						// 检查是否已存在相同条码的记录
						const existingIndex = history.findIndex(item => item.barcode === barcode);
						if (existingIndex >= 0) {
							// 更新现有记录
							history[existingIndex] = newRecord;
						} else {
							// 添加新记录
							history.unshift(newRecord);
						}
						
						// 限制历史记录数量（最多保存100条）
						if (history.length > 100) {
							history = history.slice(0, 100);
						}
						
						// 保存到本地存储
						uni.setStorage({
							key: 'scanHistory',
							data: history
						});
					},
					fail: () => {
						// 如果没有历史记录，创建新的
						const newHistory = [{
							id: Date.now(),
							barcode: barcode,
							product: product,
							scanTime: new Date().toISOString(),
							timestamp: Date.now()
						}];

						uni.setStorage({
							key: 'scanHistory',
							data: newHistory
						});
					}
				});
				
				// 同时发送到后端保存
				this.saveScanHistoryToServer(product, barcode);
			} catch (error) {
				console.error('保存扫描历史失败:', error);
			}
		},

		// 保存扫描历史到服务器
		async saveScanHistoryToServer(product, barcode) {
			try {
				const token = await this.getToken();
				if (!token) return; // 未登录则不保存到服务器
				
				await uni.request({
					url: config.baseURL + '/api/scan',
					method: 'POST',
					header: {
						'Authorization': 'Bearer ' + token,
						'Content-Type': 'application/json'
					},
					data: {
						product_id: product.product_id,
					}
				});
			} catch (error) {
				console.error('保存扫描历史到服务器失败:', error);
				// 不影响用户体验，静默失败
			}
		},

		// 获取 Token
		getToken() {
			return new Promise((resolve) => {
				uni.getStorage({
					key: 'token',
					success: (res) => resolve(res.data),
					fail: () => resolve(null)
				});
			});
		},

		// 显示手动输入弹窗
		showManualInput() {
			this.showModal = true;
			this.manualBarcode = '';
		},

		// 隐藏手动输入弹窗
		hideModal() {
			this.showModal = false;
			this.manualBarcode = '';
		},

		// 手动输入条码查询
		searchByManualCode() {
			
			if (!this.manualBarcode.trim()) {
				uni.showToast({ title: '请输入条码', icon: 'none' });
				return;
			}
			const code = this.manualBarcode.trim();
			this.hideModal();
			this.searchProduct(code);
		}
	}
};
</script>

<style scoped>
.page {
	min-height: 100vh;
	background: #f5f5f7;
}

/* 顶部导航栏 */
.header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 20rpx;
	background: #fff;
	box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06);
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

/* 摄像头区域 */
.camera-section {
	padding: 20rpx;
	flex: 1;
}

.camera-container {
	position: relative;
	height: 600rpx;
	border-radius: 20rpx;
	overflow: hidden;
	background: #000;
	box-shadow: 0 8rpx 30rpx rgba(0,0,0,0.3);
}

.camera {
	width: 100%;
	height: 100%;
}

/* 扫码叠加层 */
.scan-overlay {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	display: flex;
	align-items: center;
	justify-content: center;
	background: rgba(0,0,0,0.4);
}

.scan-box {
	position: relative;
	width: 500rpx;
	height: 300rpx;
	border: 4rpx solid transparent;
}

.corner {
	position: absolute;
	width: 60rpx;
	height: 60rpx;
	border: 6rpx solid #67C23A;
}

.corner-tl {
	top: -4rpx;
	left: -4rpx;
	border-right: none;
	border-bottom: none;
}

.corner-tr {
	top: -4rpx;
	right: -4rpx;
	border-left: none;
	border-bottom: none;
}

.corner-bl {
	bottom: -4rpx;
	left: -4rpx;
	border-right: none;
	border-top: none;
}

.corner-br {
	bottom: -4rpx;
	right: -4rpx;
	border-left: none;
	border-top: none;
}

.scan-line {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	height: 4rpx;
	background: linear-gradient(90deg, transparent, #67C23A, transparent);
	opacity: 0;
}

.scan-line.scanning {
	animation: scanMove 2s linear infinite;
	opacity: 1;
}

@keyframes scanMove {
	0% { transform: translateY(0); }
	100% { transform: translateY(300rpx); }
}

/* 提示文字 */
.scan-tip {
	position: absolute;
	bottom: 60rpx;
	left: 0;
	right: 0;
	text-align: center;
}

.tip-text {
	color: #fff;
	font-size: 28rpx;
	background: rgba(0,0,0,0.6);
	padding: 16rpx 32rpx;
	border-radius: 40rpx;
	backdrop-filter: blur(10rpx);
}

/* 控制区域 */
.controls-section {
	padding: 40rpx 20rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
}

.scan-info {
	margin-bottom: 40rpx;
}

.info-card {
	background: #fff;
	border-radius: 16rpx;
	padding: 40rpx;
	display: flex;
	align-items: center;
	box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.08);
}

.info-icon {
	font-size: 60rpx;
	margin-right: 24rpx;
}

.info-text {
	font-size: 28rpx;
	color: #666;
	flex: 1;
}

/* 扫描按钮 */
.scan-btn {
	width: 500rpx;
	height: 100rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	border-radius: 50rpx;
	border: none;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 8rpx 25rpx rgba(102,126,234,0.4);
	margin-bottom: 30rpx;
}

.scan-btn.scanning {
	opacity: 0.6;
}

.scan-btn-text {
	color: #fff;
	font-size: 36rpx;
	font-weight: 600;
}

/* 手动输入按钮 */
.manual-btn {
	background: none;
	border: 2rpx solid #ddd;
	border-radius: 40rpx;
	padding: 20rpx 40rpx;
}

.manual-text {
	color: #666;
	font-size: 28rpx;
}

/* 手动输入弹窗 */
.modal-overlay {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0,0,0,0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 9999;
}

.modal-content {
	background: #fff;
	border-radius: 20rpx;
	width: 600rpx;
	max-width: 90%;
	overflow: hidden;
}

.modal-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 40rpx;
	border-bottom: 1rpx solid #f0f0f0;
}

.modal-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #333;
}

.modal-close {
	width: 60rpx;
	height: 60rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	background: none;
	border: none;
	font-size: 40rpx;
	color: #999;
}

.modal-body {
	padding: 40rpx;
}

.barcode-input {
	width: 100%;
	height: 80rpx;
	border: 2rpx solid #ddd;
	border-radius: 12rpx;
	padding: 0 20rpx;
	font-size: 30rpx;
}

.modal-footer {
	display: flex;
	border-top: 1rpx solid #f0f0f0;
}

.modal-cancel, .modal-confirm {
	flex: 1;
	height: 100rpx;
	border: none;
	font-size: 32rpx;
}

.modal-cancel {
	background: #f8f8f8;
	color: #666;
}

.modal-confirm {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: #fff;
}
</style>
