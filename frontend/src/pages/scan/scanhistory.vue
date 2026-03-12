<template>
	<view class="page">
		<!-- 顶部统计信息 -->
		<view class="header-stats">
			<view class="stats-card">
				<text class="stats-icon">📊</text>
				<view class="stats-content">
					<text class="stats-label">总扫描次数</text>
					<text class="stats-number">{{ total }}</text>
				</view>
			</view>
		</view>

		<!-- 扫描历史列表 -->
		<scroll-view 
			class="history-list" 
			scroll-y 
			@scrolltolower="loadMore"
			@refresherrefresh="onRefresh"
			:refresher-enabled="true"
			:refresher-triggered="refreshing"
		>
			<view 
				v-for="item in scanHistories" 
				:key="item.history_id" 
				class="history-item"
				@click="goToDetail(item)"
			>
				<!-- 左侧产品图片 -->
				<view class="item-image">
					<image 
						:src="item.product.image_url || '/static/default-product.png'" 
						mode="aspectFill"
						class="product-img"
					/>
				</view>

				<!-- 中间产品信息 -->
				<view class="item-content">
					<view class="item-header">
						<text class="product-name">{{ item.product.name }}</text>
						<text class="scan-time">扫描时间：{{ formatDate(item.scan_time) }}</text>
					</view>
					<view class="item-details">
						<text class="detail-text">批次号：{{ item.product.batch_number || '未知' }}</text>
						<text class="detail-text">条形码号：{{ item.product.barcode_or_qr }}</text>
					</view>
				</view>

				<!-- 右侧有效期状态 -->
				<view class="item-status">
					<view class="status-badge" :class="getStatusClass(item.product.expiration_date)">
						<text class="status-text">{{ getExpireStatus(item.product.expiration_date) }}</text>
					</view>
				</view>
			</view>

			<!-- 加载状态 -->
			<view class="loading-more" v-if="hasMore">
				<text class="loading-text">{{ loading ? '加载中...' : '上滑加载更多' }}</text>
			</view>
			<view class="no-more" v-else-if="scanHistories.length > 0">
				<text class="no-more-text">没有更多了</text>
			</view>

			<!-- 空状态 -->
			<view class="empty-state" v-if="!loading && scanHistories.length === 0">
				<text class="empty-icon">📦</text>
				<text class="empty-text">暂无扫描记录</text>
				<button class="go-scan-btn" @click="goToScan">
					<text class="go-scan-text">去扫描</text>
				</button>
			</view>
		</scroll-view>
	</view>
</template>

<script>
import config from '@/utils/config.js';

export default {
	data() {
		return {
			scanHistories: [],
			total: 0,
			skip: 0,
			limit: 20,
			loading: false,
			refreshing: false,
			hasMore: true
		};
	},
	onLoad() {
		this.loadHistories();
	},
	onShow() {
		// 每次显示页面时刷新数据
		this.refreshHistories();
	},
	methods: {
		// 加载扫描历史
		async loadHistories() {
			if (this.loading || !this.hasMore) return;

			this.loading = true;

			try {
				const token = await this.getToken();
				if (!token) {
					uni.showToast({ title: '请先登录', icon: 'none' });
					this.loading = false;
					return;
				}

				const response = await uni.request({
					url: config.baseURL + `/api/scan/user/?skip=${this.skip}&limit=${this.limit}`,
					method: 'GET',
					header: {
						'Authorization': 'Bearer ' + token,
						'Content-Type': 'application/json'
					}
				});

				console.log('扫描历史响应:', response);

				if (response.statusCode === 200 && response.data) {
					const { scan_histories, total } = response.data;
					
					this.total = total;
					this.scanHistories = [...this.scanHistories, ...scan_histories];
					this.skip += scan_histories.length;
					
					// 判断是否还有更多数据
					if (this.scanHistories.length >= total) {
						this.hasMore = false;
					}
				}
			} catch (error) {
				console.error('加载扫描历史失败:', error);
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
			await this.refreshHistories();
		},

		// 刷新历史记录
		async refreshHistories() {
			this.skip = 0;
			this.hasMore = true;
			this.scanHistories = [];
			await this.loadHistories();
		},

		// 加载更多
		loadMore() {
			if (!this.loading && this.hasMore) {
				this.loadHistories();
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

		// 格式化日期
		formatDate(dateStr) {
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

		// 获取有效期状态
		getExpireStatus(expireDate) {
			if (!expireDate) return '未知';
			
			const now = new Date();
			const expire = new Date(expireDate);
			const diffDays = Math.ceil((expire - now) / (1000 * 60 * 60 * 24));
			
			if (diffDays < 0) {
				return '已过期';
			} else if (diffDays === 0) {
				return '今日到期';
			} else if (diffDays <= 7) {
				return `${diffDays}天到期`;
			} else if (diffDays <= 30) {
				return '即将到期';
			} else {
				return '有效期内';
			}
		},

		// 获取状态样式类
		getStatusClass(expireDate) {
			if (!expireDate) return 'status-unknown';
			
			const now = new Date();
			const expire = new Date(expireDate);
			const diffDays = Math.ceil((expire - now) / (1000 * 60 * 60 * 24));
			
			if (diffDays < 0) {
				return 'status-expired';
			} else if (diffDays <= 7) {
				return 'status-warning';
			} else if (diffDays <= 30) {
				return 'status-attention';
			} else {
				return 'status-normal';
			}
		},

		// 跳转到产品详情页
		goToDetail(item) {
			uni.navigateTo({
				url: `/pages/product/detail?barcode=${item.product.barcode_or_qr}`
			});
		},

		// 跳转到扫描页面
		goToScan() {
			uni.navigateTo({
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

/* 顶部统计卡片 */
.header-stats {
	padding: 20rpx;
	background: #fff;
	margin-bottom: 20rpx;
	box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06);
}

.stats-card {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	border-radius: 16rpx;
	padding: 40rpx;
	display: flex;
	align-items: center;
	box-shadow: 0 8rpx 25rpx rgba(102,126,234,0.3);
}

.stats-icon {
	font-size: 80rpx;
	margin-right: 30rpx;
}

.stats-content {
	display: flex;
	flex-direction: column;
}

.stats-label {
	color: rgba(255,255,255,0.9);
	font-size: 28rpx;
	margin-bottom: 8rpx;
}

.stats-number {
	color: #fff;
	font-size: 56rpx;
	font-weight: 700;
}

/* 历史列表 */
.history-list {
	height: calc(100vh - 240rpx);
	padding: 0 20rpx;
}

.history-item {
	background: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
	margin-bottom: 20rpx;
	display: flex;
	align-items: center;
	box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.08);
	transition: transform 0.2s;
}

.history-item:active {
	transform: scale(0.98);
}

/* 产品图片 */
.item-image {
	width: 120rpx;
	height: 120rpx;
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
.item-content {
	flex: 1;
	display: flex;
	flex-direction: column;
	min-width: 0;
}

.item-header {
	margin-bottom: 16rpx;
}

.product-name {
	font-size: 32rpx;
	font-weight: 600;
	color: #333;
	display: block;
	margin-bottom: 8rpx;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.scan-time {
	font-size: 24rpx;
	color: #999;
}

.item-details {
	display: flex;
	flex-direction: column;
	gap: 6rpx;
}

.detail-text {
	font-size: 24rpx;
	color: #666;
}

/* 有效期状态 */
.item-status {
	margin-left: 16rpx;
	flex-shrink: 0;
}

.status-badge {
	padding: 12rpx 20rpx;
	border-radius: 20rpx;
	white-space: nowrap;
}

.status-text {
	font-size: 24rpx;
	font-weight: 500;
}

/* 状态颜色 */
.status-normal {
	background: linear-gradient(135deg, #67C23A 0%, #85CE61 100%);
}

.status-normal .status-text {
	color: #fff;
}

.status-attention {
	background: linear-gradient(135deg, #E6A23C 0%, #F0C78A 100%);
}

.status-attention .status-text {
	color: #fff;
}

.status-warning {
	background: linear-gradient(135deg, #F56C6C 0%, #F89898 100%);
}

.status-warning .status-text {
	color: #fff;
}

.status-expired {
	background: linear-gradient(135deg, #909399 0%, #C0C4CC 100%);
}

.status-expired .status-text {
	color: #fff;
}

.status-unknown {
	background: #f5f5f7;
}

.status-unknown .status-text {
	color: #999;
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

.no-more {
	text-align: center;
	padding: 40rpx 0;
}

.no-more-text {
	font-size: 28rpx;
	color: #ccc;
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
</style>