<template>
	<view class="page">
		<!-- 顶部导航栏 -->
		<!-- <view class="header">
			<button class="back-btn" @click="goBack">
				<text class="back-icon">‹</text>
			</button>
			<view class="header-title">商品详情</view>
			<view class="placeholder"></view>
		</view> -->

		<!-- 滚动内容区域 -->
		<scroll-view scroll-y class="content">
			<!-- 商品图片 -->
			<view class="image-section" v-if="product.image_url">
				<image :src="product.image_url" class="main-image" mode="aspectFit" />
			</view>

			<!-- 到期状态醒目展示 -->
			<view class="status-card" :class="expireStatusClass">
				<view class="status-icon">{{ expireStatusIcon }}</view>
				<view class="status-info">
					<view class="status-title">{{ expireStatusTitle }}</view>
					<view class="status-desc">{{ expireStatusDesc }}</view>
				</view>
			</view>

			<!-- 商品基本信息 -->
			<view class="info-card">
				<view class="card-title">商品信息</view>
				<view class="info-row">
					<text class="label">商品名称</text>
					<text class="value">{{ product.name || '-' }}</text>
				</view>
				<view class="info-row">
					<text class="label">商品条码</text>
					<text class="value">{{ product.barcode_or_qr || '-' }}</text>
				</view>
				<view class="info-row">
					<text class="label">商品分类</text>
					<text class="value">{{ categoryName || '加载中...' }}</text>
				</view>
				<view class="info-row">
					<text class="label">批次号</text>
					<text class="value">{{ product.batch_number || '-' }}</text>
				</view>
			</view>

			<!-- 日期信息 -->
			<view class="info-card">
				<view class="card-title">日期信息</view>
				<view class="info-row">
					<text class="label">生产日期</text>
					<text class="value">{{ formatDate(product.production_date) }}</text>
				</view>
				<view class="info-row">
					<text class="label">到期日期</text>
					<text class="value expire-date" :class="expireDateClass">{{ formatDate(product.expiration_date) }}</text>
				</view>
			</view>

			<!-- 商品描述 -->
			<view class="info-card" v-if="product.description">
				<view class="card-title">商品描述</view>
				<view class="description">{{ product.description }}</view>
			</view>
		</scroll-view>

		<!-- 加载状态 -->
		<view class="loading-overlay" v-if="loading">
			<view class="loading-content">
				<text class="loading-text">加载中...</text>
			</view>
		</view>
	</view>
</template>

<script>
import config from '@/utils/config.js';

export default {
	data() {
		return {
			product: {},
			categoryName: '',
			loading: true,
			barcode: ''
		};
	},
	onLoad(params) {
		console.log('页面参数:', params);
		
		// 获取传入的参数
		this.barcode = params.barcode || '';
		const productId = params.id || '';

		if (this.barcode) {
			this.loadProductByBarcode(this.barcode);
		} else if (productId) {
			// 如果没有 barcode 但有 id，可以通过 id 查询
			this.loadProductById(productId);
		} else {
			uni.showModal({
				title: '错误',
				content: '缺少必要参数',
				showCancel: false,
				success: () => uni.navigateBack()
			});
		}
	},
	computed: {
		// 计算到期剩余天数
		remainingDays() {
			if (!this.product.expiration_date) return null;
			const today = new Date();
			const expireDate = new Date(this.product.expiration_date);
			const diffTime = expireDate - today;
			const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
			return diffDays;
		},

		// 到期状态样式类
		expireStatusClass() {
			const days = this.remainingDays;
			if (days === null) return 'status-unknown';
			if (days < 0) return 'status-expired';
			if (days <= 7) return 'status-warning';
			return 'status-ok';
		},

		// 到期状态图标
		expireStatusIcon() {
			const days = this.remainingDays;
			if (days === null) return '❓';
			if (days < 0) return '⚠️';
			if (days <= 7) return '⏰';
			return '✅';
		},

		// 到期状态标题
		expireStatusTitle() {
			const days = this.remainingDays;
			if (days === null) return '到期信息未知';
			if (days < 0) return '商品已过期';
			if (days === 0) return '今日到期';
			if (days <= 7) return '即将到期';
			return '商品新鲜';
		},

		// 到期状态描述
		expireStatusDesc() {
			const days = this.remainingDays;
			if (days === null) return '请检查商品包装上的到期日期';
			if (days < 0) return `已过期 ${Math.abs(days)} 天，请勿食用`;
			if (days === 0) return '今天是最后一天，请尽快食用';
			if (days <= 7) return `还有 ${days} 天到期，请尽快食用`;
			return `还有 ${days} 天到期，商品状态良好`;
		},

		// 到期日期样式类
		expireDateClass() {
			const days = this.remainingDays;
			if (days === null) return '';
			if (days < 0) return 'expired';
			if (days <= 7) return 'warning';
			return 'ok';
		}
	},
	methods: {
		// 返回上一页
		goBack() {
			uni.navigateBack();
		},

		// 通过条码加载商品信息
		async loadProductByBarcode(barcode) {
			try {
				this.loading = true;
				
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

				console.log('商品查询响应:', response);

				if (response.statusCode === 200 && response.data) {
					this.product = response.data;
					// 加载分类信息
					if (this.product.category_id) {
						this.loadCategory(this.product.category_id);
					}
				} else {
					throw new Error('商品信息加载失败');
				}
			} catch (error) {
				console.error('加载商品信息失败:', error);
				uni.showModal({
					title: '加载失败',
					content: '无法加载商品信息，请重试',
					showCancel: false,
					success: () => uni.navigateBack()
				});
			} finally {
				this.loading = false;
			}
		},

		// 通过ID加载商品信息（备用方法）
		async loadProductById(productId) {
			try {
				this.loading = true;
				
				const token = await this.getToken();
				
				const response = await uni.request({
					url: config.baseURL + `/api/product/${productId}`,
					method: 'GET',
					header: {
						'Authorization': token ? 'Bearer ' + token : '',
						'Content-Type': 'application/json'
					}
				});

				if (response.statusCode === 200 && response.data) {
					this.product = response.data;
					if (this.product.category_id) {
						this.loadCategory(this.product.category_id);
					}
				} else {
					throw new Error('商品信息加载失败');
				}
			} catch (error) {
				console.error('加载商品信息失败:', error);
				uni.showModal({
					title: '加载失败',
					content: '无法加载商品信息，请重试',
					showCancel: false,
					success: () => uni.navigateBack()
				});
			} finally {
				this.loading = false;
			}
		},

		// 加载商品分类信息
		async loadCategory(categoryId) {
			try {
				const token = await this.getToken();
				
				const response = await uni.request({
					url: config.baseURL + `/api/category/${categoryId}`,
					method: 'GET',
					header: {
						'Authorization': token ? 'Bearer ' + token : '',
						'Content-Type': 'application/json'
					}
				});

				console.log('分类查询响应:', response);

				if (response.statusCode === 200 && response.data) {
					this.categoryName = response.data.name || response.data.category_name || '未知分类';
				} else {
					this.categoryName = '未知分类';
				}
			} catch (error) {
				console.error('加载分类信息失败:', error);
				this.categoryName = '未知分类';
			}
		},

		// 格式化日期
		formatDate(dateStr) {
			if (!dateStr) return '-';
			try {
				const date = new Date(dateStr);
				return date.toLocaleDateString('zh-CN', {
					year: 'numeric',
					month: '2-digit',
					day: '2-digit'
				});
			} catch (e) {
				return dateStr;
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
		}
	}
};
</script>

<style scoped>
.page {
	min-height: 100vh;
	background: #f5f5f7;
}

/* 顶部导航栏 - 与 my.vue 一致 */
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

/* 内容区域 */
.content {
	height: calc(100vh - 120rpx);
	padding: 20rpx;
}

/* 商品图片区域 */
.image-section {
	margin-bottom: 20rpx;
}

.main-image {
	width: 100%;
	height: 400rpx;
	border-radius: 16rpx;
	background: #fff;
	box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06);
}

/* 到期状态卡片 - 醒目展示 */
.status-card {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	border-radius: 16rpx;
	padding: 32rpx;
	margin-bottom: 20rpx;
	display: flex;
	align-items: center;
	box-shadow: 0 4rpx 20rpx rgba(102,126,234,0.3);
}

.status-card.status-expired {
	background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
	box-shadow: 0 4rpx 20rpx rgba(255,107,107,0.3);
}

.status-card.status-warning {
	background: linear-gradient(135deg, #ffa726 0%, #ff9800 100%);
	box-shadow: 0 4rpx 20rpx rgba(255,167,38,0.3);
}

.status-card.status-ok {
	background: linear-gradient(135deg, #66bb6a 0%, #4caf50 100%);
	box-shadow: 0 4rpx 20rpx rgba(102,187,106,0.3);
}

.status-card.status-unknown {
	background: linear-gradient(135deg, #bdbdbd 0%, #9e9e9e 100%);
	box-shadow: 0 4rpx 20rpx rgba(189,189,189,0.3);
}

.status-icon {
	font-size: 60rpx;
	margin-right: 24rpx;
}

.status-info {
	flex: 1;
}

.status-title {
	font-size: 32rpx;
	font-weight: 700;
	color: #fff;
	margin-bottom: 8rpx;
}

.status-desc {
	font-size: 26rpx;
	color: rgba(255,255,255,0.9);
	line-height: 1.4;
}

/* 信息卡片 - 与 my.vue 保持一致 */
.info-card {
	background: #fff;
	border-radius: 16rpx;
	padding: 32rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}

.card-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #333;
	margin-bottom: 24rpx;
	padding-bottom: 16rpx;
	border-bottom: 2rpx solid #f0f0f0;
}

.info-row {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 20rpx 0;
	border-bottom: 1rpx solid #f8f8f8;
}

.info-row:last-child {
	border-bottom: none;
}

.label {
	font-size: 28rpx;
	color: #666;
	flex-shrink: 0;
	width: 160rpx;
}

.value {
	font-size: 28rpx;
	color: #333;
	flex: 1;
	text-align: right;
	font-weight: 500;
}

/* 到期日期颜色 */
.expire-date.ok {
	color: #4caf50;
	font-weight: 600;
}

.expire-date.warning {
	color: #ff9800;
	font-weight: 600;
}

.expire-date.expired {
	color: #f44336;
	font-weight: 600;
}

/* 商品描述 */
.description {
	font-size: 28rpx;
	color: #666;
	line-height: 1.6;
	background: #f8f8f8;
	padding: 24rpx;
	border-radius: 12rpx;
}

/* 加载状态 */
.loading-overlay {
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

.loading-content {
	background: #fff;
	border-radius: 16rpx;
	padding: 60rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
}

.loading-text {
	font-size: 28rpx;
	color: #666;
	margin-top: 20rpx;
}
</style>
