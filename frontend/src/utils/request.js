import config from './config.js';

/**
 * 封装的 HTTP 请求方法
 * @param {String} url - 请求路径（相对路径，会自动拼接 baseURL）
 * @param {String} method - 请求方法（GET/POST/PUT/DELETE 等）
 * @param {Object} data - 请求参数
 * @param {Object} options - 其他配置项（如自定义 header）
 * @returns {Promise}
 */
const request = (url, method = 'GET', data = {}, options = {}) => {
	return new Promise((resolve, reject) => {
		// 获取本地存储的 token
		const token = uni.getStorageSync('token') || '';
		
		// 构建完整 URL
		const fullUrl = url.startsWith('http') ? url : config.baseURL + url;
		
		// 发起请求
		uni.request({
			url: fullUrl,
			method: method.toUpperCase(),
			data,
			timeout: options.timeout || config.timeout,
			header: {
				'content-type': 'application/json',
				'Authorization': token ? `${token}` : '',
				...options.header
			},
			success: (res) => {
				// 根据状态码处理响应
				if (res.statusCode >= 200 && res.statusCode < 300) {
					resolve(res.data);
				} else if (res.statusCode === 401) {
					// token 过期或未登录，清除本地数据并跳转登录
					uni.removeStorageSync('token');
					uni.removeStorageSync('user');
					uni.showToast({ title: '登录已过期，请重新登录', icon: 'none' });
					// 可选：跳转到登录页
					// uni.reLaunch({ url: '/pages/my/my' });
					reject(res);
				} else {
					// 其他错误
					const msg = (res.data && (res.data.message || res.data.msg)) || '请求失败';
					uni.showToast({ title: msg, icon: 'none' });
					reject(res);
				}
			},
			fail: (err) => {
				console.error('请求失败:', err);
				uni.showToast({ title: '网络请求失败', icon: 'none' });
				reject(err);
			}
		});
	});
};

// 快捷方法
export const get = (url, data, options) => request(url, 'GET', data, options);
export const post = (url, data, options) => request(url, 'POST', data, options);
export const put = (url, data, options) => request(url, 'PUT', data, options);
export const del = (url, data, options) => request(url, 'DELETE', data, options);

export default request;
