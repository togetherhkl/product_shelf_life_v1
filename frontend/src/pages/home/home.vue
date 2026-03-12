<template>
	<view class="page">
		<!-- 顶部统计区域 -->
		<view class="header-stats">
			<view class="stats-card">
				<view class="stats-title">
					<text class="title-icon">📦</text>
					<text class="title-text">过期提醒</text>
				</view>
				<view class="stats-content">
					<view class="stat-item expired">
						<text class="stat-icon">🟥</text>
						<text class="stat-label">已过期：</text>
						<text class="stat-value">{{ expiredCount }} 件</text>
					</view>
					<view class="stat-item expiring">
						<text class="stat-icon">🟨</text>
						<text class="stat-label">即将过期：</text>
						<text class="stat-value">{{ expiringSoonCount }} 件</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 内容区域 -->
		<scroll-view 
			class="content-scroll" 
			scroll-y 
			@scrolltolower="loadMore"
			@refresherrefresh="onRefresh"
			:refresher-enabled="true"
			:refresher-triggered="refreshing"
		>
			<!-- 即将过期产品区 -->
			<view class="section expiring-section" v-if="expiringSoonProducts.length > 0">
				<view class="section-header">
					<text class="section-title">即将过期商品</text>
					<text class="section-subtitle">Expiring Soon</text>
				</view>

				<view 
					v-for="product in expiringSoonProducts" 
					:key="product.product_id" 
					class="product-card expiring-card"
					@click="goToDetail(product)"
				>
					<view class="product-image">
						<image 
							:src="product.image_url || '/static/default-product.png'" 
							mode="aspectFill"
							class="product-img"
						/>
					</view>
					<view class="product-info">
						<view class="product-name">{{ product.name }}</view>
						<view class="product-detail">
							<text class="detail-label">分类：</text>
							<text class="detail-value">{{ product.category?.category_name || '未分类' }}</text>
						</view>
						<view class="product-detail">
							<text class="detail-label">到期时间：</text>
							<text class="detail-value">{{ formatDate(product.expiration_date) }}</text>
						</view>
						<view class="product-warn expiring-warn">
							<text class="warn-icon">⚠️</text>
							<text class="warn-text">还有 {{ product.days_until_expiration }} 天到期</text>
						</view>
						<view class="product-scan-time">
							<text class="scan-label">扫码时间：</text>
							<text class="scan-value">{{ formatDateTime(product.scan_time) }}</text>
						</view>
					</view>
				</view>
			</view>

			<!-- 已过期产品区 -->
			<view class="section expired-section" v-if="expiredProducts.length > 0">
				<view class="section-header">
					<text class="section-title">已过期商品</text>
					<text class="section-subtitle">Expired</text>
				</view>

				<view 
					v-for="product in expiredProducts" 
					:key="product.product_id" 
					class="product-card expired-card"
					@click="goToDetail(product)"
				>
					<view class="product-image">
						<image 
							:src="product.image_url || '/static/default-product.png'" 
							mode="aspectFill"
							class="product-img"
						/>
					</view>
					<view class="product-info">
						<view class="product-name">{{ product.name }}</view>
						<view class="product-detail">
							<text class="detail-label">分类：</text>
							<text class="detail-value">{{ product.category?.category_name || '未分类' }}</text>
						</view>
						<view class="product-detail">
							<text class="detail-label">过期时间：</text>
							<text class="detail-value">{{ formatDate(product.expiration_date) }}</text>
						</view>
						<view class="product-warn expired-warn">
							<text class="warn-icon">🚫</text>
							<text class="warn-text">已过期 {{ product.days_since_expired }} 天</text>
						</view>
						<view class="product-scan-time">
							<text class="scan-label">扫码时间：</text>
							<text class="scan-value">{{ formatDateTime(product.scan_time) }}</text>
						</view>
					</view>
				</view>
			</view>

			<!-- 空状态 -->
			<view class="empty-state" v-if="!loading && expiredProducts.length === 0 && expiringSoonProducts.length === 0">
				<text class="empty-icon">✅</text>
				<text class="empty-text">暂无过期或即将过期的商品</text>
				<text class="empty-desc">扫描商品后会在这里显示提醒</text>
				<button class="go-scan-btn" @click="goToScan">
					<text class="go-scan-text">去扫描</text>
				</button>
			</view>

			<!-- 加载状态 -->
			<view class="loading-more" v-if="loading && (expiredProducts.length > 0 || expiringSoonProducts.length > 0)">
				<text class="loading-text">加载中...</text>
			</view>
		</scroll-view>
	</view>
</template>

<script>
import config from '@/utils/config.js';

export default {
	data() {
		return {
			expiredProducts: [],
			expiringSoonProducts: [],
			expiredCount: 0,
			expiringSoonCount: 0,
			totalCount: 0,
			loading: false,
			refreshing: false,
			daysThreshold: 7 // 即将过期的天数阈值
		};
	},
	onLoad() {
		this.loadExpiredProducts();
	},
	onShow() {
		// 每次显示页面时刷新数据
		this.refreshData();
	},
	methods: {
		// 加载过期和即将过期的商品
		async loadExpiredProducts() {
			if (this.loading) return;

			this.loading = true;

			try {
				const token = await this.getToken();
				if (!token) {
					uni.showToast({ title: '请先登录', icon: 'none' });
					this.loading = false;
					return;
				}

				const response = await uni.request({
					url: config.baseURL + `/api/scan/user/expired-products?days_threshold=${this.daysThreshold}`,
					method: 'GET',
					header: {
						'Authorization': 'Bearer ' + token,
						'Content-Type': 'application/json'
					}
				});

				console.log('过期商品响应:', response);

				if (response.statusCode === 200 && response.data) {
					const data = response.data;
					
					this.expiredProducts = data.expired_products || [];
					this.expiringSoonProducts = data.expiring_soon_products || [];
					this.expiredCount = data.expired_count || 0;
					this.expiringSoonCount = data.expiring_soon_count || 0;
					this.totalCount = data.total_count || 0;
				}
			} catch (error) {
				console.error('加载过期商品失败:', error);
				uni.showToast({ 
					title: '加载失败，请重试', 
					icon: 'none' 
				});
			} finally {
				this.loading = false;
				this.refreshing = false;
			}
		},

		// 下拉刷新
		async onRefresh() {
			this.refreshing = true;
			await this.refreshData();
		},

		// 刷新数据
		async refreshData() {
			await this.loadExpiredProducts();
		},

		// 加载更多（预留接口，当前不需要分页）
		loadMore() {
			// 如果后续需要分页，可以在这里实现
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

		// 格式化日期（仅日期）
		formatDate(dateStr) {
			if (!dateStr) return '未知';
			try {
				const date = new Date(dateStr);
				const year = date.getFullYear();
				const month = String(date.getMonth() + 1).padStart(2, '0');
				const day = String(date.getDate()).padStart(2, '0');
				return `${year}-${month}-${day}`;
			} catch (e) {
				return dateStr;
			}
		},

		// 格式化日期时间（包含时间）
		formatDateTime(dateStr) {
			if (!dateStr) return '未知';
			try {
				const date = new Date(dateStr);
				const year = date.getFullYear();
				const month = String(date.getMonth() + 1).padStart(2, '0');
				const day = String(date.getDate()).padStart(2, '0');
				const hours = String(date.getHours()).padStart(2, '0');
				const minutes = String(date.getMinutes()).padStart(2, '0');
				return `${year}-${month}-${day} ${hours}:${minutes}`;
			} catch (e) {
				return dateStr;
			}
		},

		// 跳转到产品详情页
		goToDetail(product) {
			uni.navigateTo({
				url: `/pages/product/detail?barcode=${product.barcode_or_qr}`
			});
		},

		// 跳转到扫描页面
		goToScan() {
			uni.switchTab({
				url: '/pages/scan/scan'
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

/* 顶部统计区域 */
.header-stats {
	padding: 20rpx;
	background: #fff;
	box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06);
	margin-bottom: 20rpx;
}

.stats-card {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	border-radius: 16rpx;
	padding: 40rpx;
	box-shadow: 0 4rpx 20rpx rgba(102,126,234,0.3);
}

.stats-title {
	display: flex;
	align-items: center;
	margin-bottom: 24rpx;
}

.title-icon {
	font-size: 40rpx;
	margin-right: 12rpx;
}

.title-text {
	color: #fff;
	font-size: 36rpx;
	font-weight: 700;
}

.stats-content {
	display: flex;
	gap: 40rpx;
}

.stat-item {
	flex: 1;
	display: flex;
	align-items: center;
	background: rgba(255,255,255,0.2);
	padding: 24rpx;
	border-radius: 12rpx;
	backdrop-filter: blur(10rpx);
}

.stat-icon {
	font-size: 32rpx;
	margin-right: 12rpx;
}

.stat-label {
	color: rgba(255,255,255,0.9);
	font-size: 28rpx;
	margin-right: 8rpx;
}

.stat-value {
	color: #fff;
	font-size: 32rpx;
	font-weight: 700;
}

/* 内容滚动区域 */
.content-scroll {
	height: calc(100vh - 260rpx);
	padding: 0 20rpx;
}

/* 分区样式 */
.section {
	margin-bottom: 40rpx;
}

.section-header {
	margin-bottom: 24rpx;
	padding: 0 8rpx;
}

.section-title {
	display: block;
	font-size: 36rpx;
	font-weight: 700;
	color: #333;
	margin-bottom: 4rpx;
}

.section-subtitle {
	display: block;
	font-size: 24rpx;
	color: #999;
	font-weight: 500;
	letter-spacing: 1rpx;
}

/* 产品卡片 */
.product-card {
	background: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
	margin-bottom: 20rpx;
	display: flex;
	box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.08);
	transition: transform 0.2s;
}

.product-card:active {
	transform: scale(0.98);
}

/* 即将过期卡片样式 */
.expiring-card {
	border-left: 6rpx solid #E6A23C;
	background: linear-gradient(to right, #fffbf0 0%, #fff 20%);
}

/* 已过期卡片样式 */
.expired-card {
	border-left: 6rpx solid #F56C6C;
	background: linear-gradient(to right, #fff5f5 0%, #fff 20%);
}

/* 产品图片 */
.product-image {
	width: 140rpx;
	height: 140rpx;
	border-radius: 12rpx;
	overflow: hidden;
	margin-right: 24rpx;
	flex-shrink: 0;
	background: #f5f5f7;
}

.product-img {
	width: 100%;
	height: 100%;
}

/* 产品信息 */
.product-info {
	flex: 1;
	display: flex;
	flex-direction: column;
	justify-content: space-between;
}

.product-name {
	font-size: 32rpx;
	font-weight: 700;
	color: #333;
	margin-bottom: 12rpx;
	overflow: hidden;
	text-overflow: ellipsis;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	line-clamp: 2;
	-webkit-box-orient: vertical;
}

.product-detail {
	font-size: 26rpx;
	color: #666;
	margin-bottom: 8rpx;
}

.detail-label {
	color: #999;
}

.detail-value {
	color: #333;
	font-weight: 500;
}

/* 警告提示 */
.product-warn {
	display: flex;
	align-items: center;
	padding: 12rpx 16rpx;
	border-radius: 8rpx;
	margin: 12rpx 0;
}

.warn-icon {
	font-size: 28rpx;
	margin-right: 8rpx;
}

.warn-text {
	font-size: 28rpx;
	font-weight: 600;
}

/* 即将过期警告样式 */
.expiring-warn {
	background: #fef0e6;
	border: 1rpx solid #E6A23C;
}

.expiring-warn .warn-text {
	color: #E6A23C;
}

/* 已过期警告样式 */
.expired-warn {
	background: #fef0f0;
	border: 1rpx solid #F56C6C;
}

.expired-warn .warn-text {
	color: #F56C6C;
}

/* 扫码时间 */
.product-scan-time {
	font-size: 24rpx;
	color: #999;
}

.scan-label {
	color: #bbb;
}

.scan-value {
	color: #999;
}

/* 空状态 */
.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 150rpx 0;
}

.empty-icon {
	font-size: 120rpx;
	margin-bottom: 30rpx;
	opacity: 0.6;
}

.empty-text {
	font-size: 32rpx;
	color: #666;
	margin-bottom: 12rpx;
	font-weight: 600;
}

.empty-desc {
	font-size: 28rpx;
	color: #999;
	margin-bottom: 40rpx;
}

.go-scan-btn {
	width: 300rpx;
	height: 80rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	border-radius: 40rpx;
	border: none;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 8rpx 25rpx rgba(102,126,234,0.4);
}

.go-scan-text {
	color: #fff;
	font-size: 30rpx;
	font-weight: 600;
}

/* 加载状态 */
.loading-more {
	text-align: center;
	padding: 40rpx 0;
}

.loading-text {
	font-size: 28rpx;
	color: #999;
}
</style>