<template>
	<view class="page">
		<view class="nav">
			<button @click="goBack">返回</button>
			<view class="title">{{ product.name || '商品详情' }}</view>
		</view>

		<scroll-view class="content">
			<image v-if="product.image" :src="product.image" class="main-image" mode="aspectFit" />
			<view class="info">
				<view class="row name">{{ product.name }}</view>
				<view class="row">分类：{{ product.category || '-' }}</view>
				<view class="row">条码：{{ product.barcode || '-' }}</view>
				<view class="row">批次：{{ product.batch || '-' }}</view>
				<view class="row">生产日期：{{ product.manufactureDate || '-' }}</view>
				<view class="row">到期日期：{{ product.expireDate || '-' }}</view>
				<view class="row">
					到期剩余：
					<text :class="remainClass">{{ remainingDaysText }}</text>
				</view>

				<view class="desc-section">
					<view class="section-title">商品描述</view>
					<view class="desc">{{ product.description || '无' }}</view>
				</view>
			</view>
		</scroll-view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			product: {}
		};
	},
	onLoad(e) {
		const id = e.id;
		this.loadProduct(id);
	},
	methods: {
		goBack() {
			uni.navigateBack();
		},
		loadProduct(id) {
			uni.getStorage({
				key: 'products',
				success: (res) => {
					const arr = res.data || [];
					const p = arr.find(x => String(x.id) === String(id));
					if (p) this.product = p;
					else {
						uni.showModal({ content: '未找到商品信息。', showCancel: false, success: () => uni.navigateBack() });
					}
				},
				fail: () => {
					uni.showModal({ content: '未找到商品信息。', showCancel: false, success: () => uni.navigateBack() });
				}
			});
		}
	},
	computed: {
		remainingDays() {
			if (!this.product.expireDate) return null;
			const today = new Date();
			const exp = new Date(this.product.expireDate);
			const diff = Math.ceil((exp - today) / (1000 * 60 * 60 * 24));
			return diff;
		},
		remainingDaysText() {
			const d = this.remainingDays;
			if (d === null) return '-';
			if (d < 0) return `已过期 ${Math.abs(d)} 天`;
			return `${d} 天`;
		},
		remainClass() {
			const d = this.remainingDays;
			if (d === null) return '';
			if (d < 0) return 'expired';
			if (d <= 7) return 'warning';
			return 'ok';
		}
	}
};
</script>

<style scoped>
.page { min-height:100vh; background:#fff; }
.nav { display:flex; align-items:center; padding:12px; background:#f8f8f8; }
.title { flex:1; text-align:center; font-weight:600; }
.content { padding:12px; }
.main-image { width:100%; height:200px; background:#f2f2f2; border-radius:8px; margin-bottom:12px; }
.info { background:#fff; padding:12px; border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,0.05); }
.row { margin-bottom:8px; color:#333; }
.name { font-size:18px; font-weight:700; }
.desc-section { margin-top:12px; }
.section-title { font-weight:600; margin-bottom:6px; }
.desc { color:#666; line-height:1.6; }
.ok { color: #2e8b57; font-weight:700; }
.warning { color: #ff9900; font-weight:700; }
.expired { color: #ff3b30; font-weight:700; }
</style>
